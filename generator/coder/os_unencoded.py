from .os_generic import GenericOS
from .elements import CodeTemplate, Include, VariableDefinition, \
    Block, Statement, Comment, Function, Hook, DataObject
from generator.analysis.AtomicBasicBlock import S, AtomicBasicBlock
from generator.analysis.Resource import Resource
from generator.analysis.Subtask import Subtask
from generator.analysis.Function import Function


class UnencodedOS(GenericOS):
    def __init__(self):
        super(UnencodedOS, self).__init__()
        # These template slots are used by the system call layer
        self.task_list = TaskListTemplate
        self.scheduler = SchedulerTemplate
        self.return_variables = {}

    def sigs(self, count):
        return ""

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
                    S.AdvanceCounter,
                    S.SetEvent,
                    S.ClearEvent,
                    S.WaitEvent]):
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
                        S.kickoff,
                        S.iret,
            ]):
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
                assert False, abb

    def systemcall(self, abb):
        """Generate systemcall into userspace"""

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
        self.idle = self.system_graph.find(Function, "Idle")

    def template_file(self):
        return "os/scheduler/tasklist-unencoded.h.in"

    def subtask(self, snippet, args):
        return self._subtask.name

    def subtask_id(self, snippet, args):
        return str(self._subtask.impl.task_id)

    def subtask_desc(self, snippet, args):
        return self._subtask.impl.task_descriptor.name


    def foreach_subtask(self, snippet, args):
        body = args[0]
        def do(subtask):
            self._subtask = subtask
            return self.expand_snippet(body)
        return self.rules.foreach_subtask(do)

    def if_events(self, snippet, args):
        if len(self._subtask.events) > 0:
            return self.expand_snippet(args[0])
        return ""

    def if_not_preemptable(self, snippet, args):
        if not self._subtask.conf.preemptable:
            return self.expand_snippet(args[0])
        return ""


class SchedulerTemplate(CodeTemplate):
    def __init__(self, rules):
        CodeTemplate.__init__(self, rules.generator, self.template_file())
        self.rules = rules
        self.system_graph = self.generator.system_graph

    def template_file(self):
        return "os/scheduler/scheduler-unencoded.h.in"

    def subtask_desc(self, snippet, args):
        return self._subtask.impl.task_descriptor.name

    def subtask_id(self, snippet, args):
        return str(self._subtask.impl.task_id)

    def foreach_subtask(self, snippet, args):
        body = args[0]
        def do(subtask):
            self._subtask = subtask
            return self.expand_snippet(body)
        return self.rules.foreach_subtask(do)

    def if_not_preemptable(self, snippet, args):
        if not self._subtask.conf.preemptable:
            return self.expand_snippet(args[0])
        return ""

    def scheduler_prio(self, snippet, args):
        RES_SCHEDULER = self.system_graph.get(Resource, "RES_SCHEDULER")
        return str(RES_SCHEDULER.conf.static_priority)

