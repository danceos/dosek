from generator.rules.base import BaseRules
from generator.graph.AtomicBasicBlock import E
from generator.elements import Statement, Comment
from generator.graph.GenerateAssertions import AssertionType
from generator.tools import panic



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
        next_prio = abb.definite_after(E.task_level).dynamic_priority
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
        next_prio = abb.definite_after(E.task_level).dynamic_priority
        self.call_function(kernelspace,
                           "scheduler_.ReleaseResource_impl",
                           "void",
                           [self.get_calling_task_desc(abb),
                            str(next_prio)])

    # Interrupt Handling
    def disable_irq(self, block, abb):
        before = abb.get_incoming_nodes(E.task_level)
        disabled = [x.interrupt_block_all or x.interrupt_block_os
                    for x in before]
        # If the interrupts were blocked before do not a thing
        if any(disabled):
            assert all(disabled)
            return

        self.call_function(block,
                           "Machine::disable_interrupts",
                           "void", [])

    def enable_irq(self, block, abb):
        before = abb.get_outgoing_nodes(E.task_level)
        disabled = [x.interrupt_block_all or x.interrupt_block_os
                    for x in before]
        # If the interrupts were unblocked before do not a thing
        if any(disabled):
            assert all(disabled)
            return

        self.call_function(block,
                           "Machine::enable_interrupts",
                           "void", [])

    def DisableAllInterrupts(self, userspace, abb):
        self.disable_irq(userspace, abb)

    def EnableAllInterrupts(self, userspace, abb):
        self.enable_irq(userspace, abb)

    # Assertions
    def do_assertion(self, block, assertion):
        if assertion.isA(AssertionType.TaskIsSuspended):
            task = assertion.get_arguments()[0]
            block.add(Statement("assert(scheduler_.isSuspended(%s))" \
                                % self.task_desc(task)))
        elif assertion.isA(AssertionType.TaskIsReady):
            task = assertion.get_arguments()[0]
            block.add(Statement("assert(!scheduler_.isSuspended(%s))" \
                                % self.task_desc(task)))
        elif assertion.isA(AssertionType.TaskWasKickoffed):
            task = assertion.get_arguments()[0]
            block.add(Statement("assert(%s.tcb.is_running())" \
                                % self.task_desc(task)))
        elif assertion.isA(AssertionType.TaskWasNotKickoffed):
            task = assertion.get_arguments()[0]
            block.add(Statement("assert(! %s.tcb.is_running())" \
                                % self.task_desc(task)))
        else:
            panic("Unsupported assert type %s in %s", assertion, block)


