from generator.rules.simple import SimpleSystem, AlarmTemplate
from generator.elements import CodeTemplate, Include, VariableDefinition, \
    Block, Statement, Comment, Function, Hook, DataObject
from generator.graph.AtomicBasicBlock import S, AtomicBasicBlock
from generator.graph.Function import Function


class UnencodedSystem(SimpleSystem):
    def __init__(self):
        SimpleSystem.__init__(self)
        self.task_list = TaskListTemplate
        self.scheduler = SchedulerTemplate
        self.alarms = AlarmTemplate
        self.return_variables = {}

    def sigs(self, count):
        return ""

    def generate_system_code(self):
        self.generator.source_file.includes.add(Include("os/scheduler/tasklist.h"))
        self.generator.source_file.declarations.append(self.task_list(self).expand())

        self.generator.source_file.includes.add(Include("os/scheduler/scheduler.h"))
        self.generator.source_file.includes.add(Include("os/scheduler/task.h"))
        self.generator.source_file.declarations.append(self.scheduler(self).expand())

        self.generator.source_file.includes.add(Include("os/alarm.h"))
        self.generator.source_file.includes.add(Include("os/util/redundant.h"))
        self.generator.source_file.declarations.append(self.alarms(self).expand())

    def convert_argument(self, block, argument):
        var = VariableDefinition.new(self.generator, argument[1])
        block.prepend(var)
        block.add(Statement("%s = %s" % (var.name, argument[0])))
        return var

    def __instantiate_kernelspace(self, abb):
        """This function instantiates kernelspace and the hook in the correct
           place for each system call."""
        # No arguments, but a real kernelspace
        if abb.isA([S.TerminateTask,
                    S.ActivateTask,
                    S.ChainTask,
                    S.CancelAlarm,
                    S.GetAlarm,
                    S.GetResource,
                    S.ReleaseResource,
                    S.AdvanceCounter]):
            # Theese are normal system calls with a general purpose kernelspace
            x = self.arch_rules.generate_kernelspace(abb.impl.userspace, abb, [])
            abb.impl.kernelspace = x.system
            abb.impl.pre_hook    = x.pre_hook
            abb.impl.post_hook   = x.post_hook
        # Two arguments
        elif abb.isA(S.SetRelAlarm):
            args = abb.impl.userspace.arguments()
            arg1 = self.convert_argument(abb.impl.userspace, args[1])
            arg2 = self.convert_argument(abb.impl.userspace, args[2])
            x = self.arch_rules. generate_kernelspace(abb.impl.userspace,
                                                      abb, [arg1, arg2])
            abb.impl.kernelspace = x.system
            abb.impl.pre_hook    = x.pre_hook
            abb.impl.post_hook   = x.post_hook
        else:
            abb.impl.pre_hook  = Hook("SystemEnterHook")
            abb.impl.post_hook = Hook("SystemLeaveHook")
            abb.impl.kernelspace = Hook("Kernelspace")

            if abb.isA([S.EnableAllInterrupts,
                        S.ResumeAllInterrupts,
                        S.ResumeOSInterrupts,
                        S.kickoff]):
                # { /* SystemEnterHook */ }
                # { /* SystemLeaveHook */ }
                # { /* Kernel */ sti(); }
                abb.impl.userspace.add(abb.impl.pre_hook)
                abb.impl.userspace.add(abb.impl.post_hook)
                abb.impl.userspace.add(abb.impl.kernelspace)

            elif abb.isA([S.DisableAllInterrupts,
                          S.SuspendAllInterrupts,
                          S.SuspendOSInterrupts]):
                # { /* Kernel */ cli(); }
                # { /* SystemEnterHook */ }
                # { /* SystemLeaveHook */ }
                abb.impl.userspace.add(abb.impl.kernelspace)
                abb.impl.userspace.add(abb.impl.pre_hook)
                abb.impl.userspace.add(abb.impl.post_hook)
            elif abb.isA([S.AcquireCheckedObject,
                          S.ReleaseCheckedObject]):
                # FIXME: Interrupt services
                # { /* SystemEnterHook */ }
                # { /* Kernel */ sti(); }
                # { /* SystemLeaveHook */ }
                abb.impl.userspace.add(abb.impl.pre_hook)
                abb.impl.userspace.add(abb.impl.kernelspace)
                abb.impl.userspace.add(abb.impl.post_hook)
            else:
                assert False

    def systemcall(self, abb):
        """Generate systemcall into userspace"""

        subtask = abb.subtask
        syscall_type = abb.syscall_type

        userspace   = abb.impl.userspace
        kernelspace = None
        pre_hook    = None
        post_hook   = None

        self.arch_rules.asm_marker(userspace, "syscall_start_%s" % userspace.name)

        self.__instantiate_kernelspace(abb)

        # Dispatch to self.syscall_rules by syscall type name
        if hasattr(self.syscall_rules, abb.syscall_type.name):
            # Mark all Parameters as unused
            for i in range(0, len(abb.impl.userspace.arguments())):
                abb.impl.userspace.unused_parameter(0)
            # Call Generator from syscall_rules
            f = getattr(self.syscall_rules, abb.syscall_type.name)
            f(abb, abb.impl.userspace, abb.impl.kernelspace)
        else:
            assert False, "Not yet supported %s"% abb.syscall_type

        self.arch_rules.asm_marker(userspace, "syscall_end_%s" % userspace.name)

        # Fill up the hooks
        self.system_enter_hook(abb, abb.impl.pre_hook)
        self.system_leave_hook(abb, abb.impl.post_hook)

        if abb.impl.rettype != 'void':
            self.return_statement(userspace, "E_OK")

    def system_enter_hook(self, abb, hook):
        self.callback_in_valid_passes("system_enter_hook", abb, hook)

    def system_leave_hook(self, abb, hook):
        self.callback_in_valid_passes("system_leave_hook", abb, hook)

    def get_syscall_return_variable(self, Type):
        """Returns a Variable, that is able to capture the return value of a
           system call.

        """
        if Type in self.return_variables:
            return self.return_variables[Type]

        var = DataObject("os::redundant::WithLinkage<uint16_t, os::redundant::Plain>",
                         "syscall_return_%s" % Type)
        self.generator.source_file.data_manager.add(var)
        self.return_variables[Type] = var
        return var

class TaskListTemplate(CodeTemplate):
    def __init__(self, rules):
        CodeTemplate.__init__(self, rules.generator, self.template_file())
        self.rules = rules
        self.system_graph = self.generator.system_graph
        # Reference to the objects object of our rule system
        self.objects = self.rules.objects
        self.idle = self.system_graph.find(Function, "Idle")
        # Link the foreach_subtask method from the rules
        self.foreach_subtask = self.rules.foreach_subtask

    def template_file(self):
        return "os/scheduler/tasklist-unencoded.h.in"

    def ready_flag_variables(self, snippet, args):
        def do(subtask):
            # Intantiate the correct macros
            return self.expand_snippet("ready_flag",
                                       name = subtask.name) + "\n"

        return self.foreach_subtask(do)

    def ready_flag_constructor(self, snippet, args):
        def do(subtask):
            return self.expand_snippet("ready_flag_init", name = subtask.name)

        return self.foreach_subtask(do)

    def task_set_call(self, snippet, args):
        def do(subtask):
            return self.expand_snippet(args[0],
                                       name = subtask.name,
                                       id = subtask.impl.task_id)

        return self.foreach_subtask(do)

    # Implementation of head
    def head_update_max_cascade(self, snippet, args):
        """Generate the update max cascade for tasklist::head"""
        def do(subtask):
            # Generate a new signature for this cascade step
            do.i += 1
            return self.expand_snippet("head_update_max",
                                       task = subtask.name,
                                       task_id  = subtask.impl.task_id,
                                       i = str(do.i-1),
                                       ii = str(do.i)
                                       )
        # This is a ugly hack to fix python binding madness
        do.i = 0
        ret = self.foreach_subtask(do)

        # Update current prio for idle task
        ret += self.expand_snippet("head_update_idle_prio",
                                   i = str(do.i), ii = str(do.i + 1))

        return ret



class SchedulerTemplate(CodeTemplate):
    def __init__(self, rules):
        CodeTemplate.__init__(self, rules.generator, self.template_file())
        self.rules = rules
        self.system_graph = self.generator.system_graph
        # Reference to the objects object of our rule system
        self.objects = self.rules.objects

        # Link the foreach_subtask method from the rules
        self.foreach_subtask = self.rules.foreach_subtask

    def template_file(self):
        return "os/scheduler/scheduler-unencoded.h.in"

    def scheduler_prio(self, snippet, args):

        max_prio = 0
        for subtask in self.system_graph.subtasks:
            if not subtask.is_real_thread():
                continue
            if(subtask.static_priority > max_prio):
                max_prio = subtask.static_priority

        return str(max_prio+1)

    def foreach_subtask_snippet(self, snippet, args):
        def do(subtask):
            return self.expand_snippet(args[0],
                                       task = subtask.name,
                                       desc = subtask.impl.task_descriptor.name)

        return self.foreach_subtask(do)


    # Reschedule
    def reschedule_foreach_task(self, snippet, args):
        def do(subtask):
            return self.expand_snippet("reschedule_dispatch_task",
                                       task = subtask.impl.task_descriptor.name
            )

        return self.foreach_subtask(do)

    # Reschedule
    def activate_task_foreach_task(self, snippet, args):
        def do(subtask):
            return self.expand_snippet("activate_task_task",
                                       task = subtask.impl.task_descriptor.name,
                                       )

        return self.foreach_subtask(do)

