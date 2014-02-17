from generator.rules.base import BaseRules
from generator.elements import CodeTemplate, Include, VariableDefinition, \
    Block, Statement, Comment


class FullSystemCalls(BaseRules):
    def __init__(self):
        BaseRules.__init__(self)

    def task_desc(self, subtask):
        """Returns a string that generates the task id"""
        task_desc = self.objects[subtask]["task_descriptor"].name
        return task_desc

    def get_calling_task_desc(self, abb):
        return self.task_desc(abb.function.subtask)

    def StartOS(self, block):
        block.unused_parameter(0)
        highestTask = None
        for subtask in self.system_graph.get_subtasks():
            if not subtask.is_real_thread():
                continue
            # Use Reset the stack pointer for all all tasks
            self.call_function(block,
                               self.task_desc(subtask) + ".tcb.reset",
                               "void", [])

            if subtask.autostart:
                self.call_function(block,
                                   "scheduler_.SetReadyFromSuspended_impl",
                                   "void", [self.task_desc(subtask)])


            if subtask.autostart and (not highestTask or subtask.static_priority > highestTask.static_priority):
                highestTask = subtask

        self.call_function(block, "Machine::enable_interrupts", "void", [])
        # Call a full reschedule
        self.call_function(block, "syscall", "void", ["os::scheduler::ScheduleC_impl", "0"])
        self.call_function(block, "Machine::unreachable", "void", [])

    def TerminateTask(self, block, abb):
        self.call_function(block, "scheduler_.TerminateTask_impl",
                           "void",
                           [self.get_calling_task_desc(abb)])

    def ActivateTask(self, block, abb):
        self.call_function(block,
                           "scheduler_.ActivateTask_impl" + self.os_rules.sigs(1),
                           "void",
                           [self.task_desc(abb.arguments[0])])

    def ChainTask(self, block, abb):
        self.call_function(block,
                           "scheduler_.ChainTask_impl" + self.os_rules.sigs(2),
                           "void",
                           [self.get_calling_task_desc(abb),
                            self.task_desc(abb.arguments[0])])

    def SetRelAlarm(self, kernelspace, abb, arguments):
        arg1 = kernelspace.arguments()[0]
        arg2 = kernelspace.arguments()[1]
        alarm_id = abb.arguments[0]
        alarm_object = self.objects["alarm"][alarm_id]
        self.call_function(kernelspace, "%s.setRelativeTime" % alarm_object.name,
                           "void", [arg1[0]])
        self.call_function(kernelspace, "%s.setCycleTime" % alarm_object.name,
                           "void", [arg2[0]])
        self.call_function(kernelspace, "%s.setArmed" % alarm_object.name,
                           "void", ["true"])
        kernelspace.add(Comment("Dispatch directly back to Userland"))
        self.call_function(kernelspace, "Dispatcher::ResumeToTask",
                           "void",
                           [self.get_calling_task_desc(abb)])

    def CancelAlarm(self, kernelspace, abb):
        alarm_id = abb.arguments[0]
        alarm_object = self.objects["alarm"][alarm_id]
        self.call_function(kernelspace, "%s.setArmed" % alarm_object.name,
                           "void", ["false"])
        kernelspace.add(Comment("Dispatch directly back to Userland"))
        self.call_function(kernelspace, "Dispatcher::ResumeToTask",
                           "void",
                           [self.get_calling_task_desc(abb)])

    def GetResource(self, kernelspace, abb):
        next_prio = abb.definite_after('local').dynamic_priority
        self.call_function(kernelspace,
                           "scheduler_.GetResource_impl",
                           "void",
                           [self.get_calling_task_desc(abb),
                            str(next_prio)])

        kernelspace.add(Comment("Dispatch directly back to Userland"))
        self.call_function(kernelspace, "Dispatcher::ResumeToTask",
                           "void",
                           [self.get_calling_task_desc(abb)])

    def ReleaseResource(self, kernelspace, abb):
        next_prio = abb.definite_after('local').dynamic_priority
        self.call_function(kernelspace,
                           "scheduler_.ReleaseResource_impl",
                           "void",
                           [self.get_calling_task_desc(abb),
                            str(next_prio)])
