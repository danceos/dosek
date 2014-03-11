from generator.rules.simple import SimpleSystem, AlarmTemplate
from generator.elements import CodeTemplate, Include, VariableDefinition, \
    Block, Statement, Comment, Function, Hook
from generator.graph.AtomicBasicBlock import S

class UnencodedSystem(SimpleSystem):
    def __init__(self):
        SimpleSystem.__init__(self)
        self.task_list = TaskListTemplate
        self.scheduler = SchedulerTemplate
        self.alarms = AlarmTemplate

    def sigs(self, count):
        return ""

    def generate_system_code(self):
        self.generator.source_file.includes.add(Include("os/scheduler/tasklist.h"))
        self.generator.source_file.declarations.append(self.task_list(self).expand())

        self.generator.source_file.includes.add(Include("os/scheduler/scheduler.h"))
        self.generator.source_file.includes.add(Include("os/scheduler/task.h"))
        self.generator.source_file.declarations.append(self.scheduler(self).expand())

        self.generator.source_file.includes.add(Include("os/alarm.h"))
        self.generator.source_file.declarations.append(self.alarms(self).expand())

    def convert_argument(self, block, argument):
        var = VariableDefinition.new(self.generator, argument[1])
        block.prepend(var)
        block.add(Statement("%s = %s" % (var.name, argument[0])))
        return var

    def systemcall(self, systemcall, userspace):
        """Generate systemcall into userspace"""

        subtask = systemcall.abb.function.subtask
        abb  = systemcall.abb
        syscall_type = systemcall.abb.syscall_type

        kernelspace = None
        pre_hook    = None
        post_hook   = None
        if abb.isA([S.TerminateTask, S.ActivateTask, S.ChainTask,
                    S.CancelAlarm, S.GetResource, S.ReleaseResource]):
            # Need a kernelspace
            kernelspace = self.arch_rules.generate_kernelspace(userspace, abb, [])
            pre_hook, post_hook = kernelspace.pre_hook, kernelspace.post_hook


        if systemcall.function == "TerminateTask":
            self.syscall_rules.TerminateTask(kernelspace.system, abb)

        elif systemcall.function == "ActivateTask":
            userspace.unused_parameter(0)
            self.syscall_rules.ActivateTask(kernelspace.system, abb)

        elif systemcall.function == "ChainTask":
            userspace.unused_parameter(0)
            self.syscall_rules.ChainTask(kernelspace.system, abb)

        elif systemcall.function == "CancelAlarm":
            userspace.unused_parameter(0)
            self.syscall_rules.CancelAlarm(kernelspace.system, abb)

        elif systemcall.function == "GetResource":
            userspace.unused_parameter(0)
            self.syscall_rules.GetResource(kernelspace.system, abb)

        elif systemcall.function == "ReleaseResource":
            userspace.unused_parameter(0)
            self.syscall_rules.ReleaseResource(kernelspace.system, abb)
        # Interrupt Handling
        elif systemcall.function in ("DisableAllInterrupts", 
                                     "SuspendAllInterrupts", 
                                     "SuspendOSInterrupts"):
            self.syscall_rules.DisableAllInterrupts(userspace, abb)
            pre_hook, post_hook = Hook("SystemEnterHook"), Hook("SystemLeaveHook")
            userspace.add(pre_hook)
            userspace.add(post_hook)
        elif systemcall.function in ("EnableAllInterrupts",
                                     "ResumeAllInterrupts",
                                     "ResumeOSInterrupts"):
            pre_hook, post_hook = Hook("SystemEnterHook"), Hook("SystemLeaveHook")
            userspace.add(pre_hook)
            userspace.add(post_hook)
            self.syscall_rules.EnableAllInterrupts(userspace, abb)
        # Alarms
        elif systemcall.function == "SetRelAlarm":
            userspace.unused_parameter(0)
            arg1 = self.convert_argument(userspace, userspace.arguments()[1])
            arg2 = self.convert_argument(userspace, userspace.arguments()[2])
            kernelspace = self.arch_rules.\
                          generate_kernelspace(userspace, abb, [arg1, arg2])
            self.syscall_rules.SetRelAlarm(kernelspace.system, abb, [arg1, arg2])
            pre_hook, post_hook = kernelspace.pre_hook, kernelspace.post_hook
        else:
            assert False, "Not yet supported %s"% systemcall.function

        # Fill up the hooks
        if pre_hook:
            self.system_enter_hook(abb, pre_hook)
        if post_hook:
            self.system_leave_hook(abb, post_hook)

        if systemcall.rettype != 'void':
            self.return_statement(userspace, "E_OK")

    def system_enter_hook(self, abb, hook):
        self.callback_in_valid_passes("system_enter_hook", abb, hook)

    def system_leave_hook(self, abb, hook):
        self.callback_in_valid_passes("system_leave_hook", abb, hook)

class TaskListTemplate(CodeTemplate):
    def __init__(self, rules):
        CodeTemplate.__init__(self, rules.generator, self.template_file())
        self.rules = rules
        self.system_graph = self.generator.system_graph
        # Reference to the objects object of our rule system
        self.objects = self.rules.objects
        self.idle = self.system_graph.find_function("Idle")
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
                                       id = self.objects[subtask]["task_id"])

        return self.foreach_subtask(do)

    # Implementation of head
    def head_update_max_cascade(self, snippet, args):
        """Generate the update max cascade for tasklist::head"""
        def do(subtask):
            # Generate a new signature for this cascade step
            do.i += 1
            return self.expand_snippet("head_update_max",
                                       task = subtask.name,
                                       task_id  = self.objects[subtask]["task_id"],
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
        for subtask in self.system_graph.get_subtasks():
            if not subtask.is_real_thread():
                continue
            if(subtask.static_priority > max_prio):
                max_prio = subtask.static_priority

        return str(max_prio+1)

    def foreach_subtask_snippet(self, snippet, args):
        def do(subtask):
            return self.expand_snippet(args[0],
                                       task = subtask.name,
                                       desc = self.objects[subtask]["task_descriptor"].name)

        return self.foreach_subtask(do)


    # Reschedule
    def reschedule_foreach_task(self, snippet, args):
        def do(subtask):
            return self.expand_snippet("reschedule_dispatch_task",
                                       task = self.objects[subtask]["task_descriptor"].name
            )

        return self.foreach_subtask(do)

    # Reschedule
    def activate_task_foreach_task(self, snippet, args):
        def do(subtask):
            return self.expand_snippet("activate_task_task",
                                       task = self.objects[subtask]["task_descriptor"].name,
                                       )

        return self.foreach_subtask(do)

