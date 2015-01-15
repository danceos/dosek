from generator.rules.base import BaseRules
from generator.graph.AtomicBasicBlock import E
from generator.elements import Statement, Comment, Function, VariableDefinition, Block
from generator.graph.GenerateAssertions import AssertionType
from generator.tools import panic



class FullSystemCalls(BaseRules):
    def __init__(self):
        BaseRules.__init__(self)

    def task_desc(self, subtask):
        """Returns a string that generates the task id"""
        task_desc = subtask.impl.task_descriptor.name
        return task_desc

    def get_calling_task_desc(self, abb):
        return self.task_desc(abb.function.subtask)

    def StartOS(self, block):
        block.unused_parameter(0)
        highestTask = None
        for subtask in self.system_graph.subtasks:
            if not subtask.is_real_thread():
                continue
            # Use Reset the stack pointer for all all tasks
            self.call_function(block,
                               self.task_desc(subtask) + ".tcb.reset",
                               "void", [])

            if subtask.conf.autostart:
                self.call_function(block,
                                   "scheduler_.SetReadyFromSuspended_impl",
                                   "void", [self.task_desc(subtask)])

            if subtask.conf.autostart and (not highestTask or subtask.static_priority > highestTask.static_priority):
                highestTask = subtask

        # Bootstrap: Do the initial syscall
        dispatch_func = Function("__OS_StartOS_dispatch", "void", ["int"], extern_c = True)
        self.generator.source_file.function_manager.add(dispatch_func)
        self.InitialSyscall(dispatch_func)

        self.call_function(block, "syscall", "void",
                           [dispatch_func.function_name])
        self.call_function(block, "Machine::unreachable", "void", [])

    def InitialSyscall(self, kernelspace):
        kernelspace.unused_parameter(0)
        self.call_function(kernelspace, "scheduler_.Reschedule",
                           "void", [])

    def ASTSchedule(self, kernelspace):
        kernelspace.unused_parameter(0)
        self.call_function(kernelspace, "scheduler_.Reschedule",
                           "void", [])

    def kickoff(self, syscall, userspace, kernelspace):
        userspace.attributes.append("inlinehint")
        if not syscall.subtask.conf.is_isr:
            self.arch_rules.kickoff(syscall, userspace)

    def TerminateTask(self, syscall, userspace, kernelspace):
        self.call_function(kernelspace, "scheduler_.TerminateTask_impl",
                           "void",
                           [self.get_calling_task_desc(syscall)])

    def ActivateTask(self, syscall, userspace, kernelspace):
        self.call_function(kernelspace,
                           "scheduler_.ActivateTask_impl",
                           "void",
                           [self.task_desc(syscall.arguments[0])])

    def ChainTask(self, syscall, userspace, kernelspace):
        self.call_function(kernelspace,
                           "scheduler_.ChainTask_impl",
                           "void",
                           [self.get_calling_task_desc(syscall),
                            self.task_desc(syscall.arguments[0])])


    def SetRelAlarm(self, abb, userspace, kernelspace):
        arg1 = self.arch_rules.get_syscall_argument(kernelspace, 0)
        arg2 = self.arch_rules.get_syscall_argument(kernelspace, 1)
        alarm = abb.arguments[0]
        self.call_function(kernelspace, "%s.setRelativeTime" % alarm.impl.name,
                           "void", [arg1.name])
        self.call_function(kernelspace, "%s.setCycleTime" % alarm.impl.name,
                           "void", [arg2.name])
        self.call_function(kernelspace, "%s.setArmed" % alarm.impl.name,
                           "void", ["true"])
        kernelspace.add(Comment("Dispatch directly back to Userland"))
        self.call_function(kernelspace, "Dispatcher::ResumeToTask",
                           "void",
                           [self.get_calling_task_desc(abb)])

    def AdvanceCounter(self, abb, userspace, kernelspace):
        counter = abb.arguments[0]

        # Increase Counter and check the counter
        kernelspace.add(Statement("%s.do_tick()" % counter.impl.name))
        for alarm in self.system_graph.alarms:
            if alarm.counter == counter:
                kernelspace.add(Statement("AlarmCheck%s()" % alarm.impl.name))

        kernelspace.add(Comment("Dispatch directly back to Userland"))
        self.call_function(kernelspace, "Dispatcher::ResumeToTask",
                           "void",
                           [self.get_calling_task_desc(abb)])

    def GetAlarm(self, abb, userspace, kernelspace):
        alarm = abb.arguments[0]

        return_variable = self.os_rules.get_syscall_return_variable("TickType")

        # Fill return variable
        kernelspace.add(Statement("%s.set(%s.getRemainingTicks())"%(
            return_variable.name,
            alarm.impl.name)))

        kernelspace.add(Comment("Dispatch directly back to Userland"))
        self.call_function(kernelspace, "Dispatcher::ResumeToTask",
                           "void",
                           [self.get_calling_task_desc(abb)])

        # Read out the result of the system call
        userspace.add(Statement("%s.check()" %(
            return_variable.name
        )))
        userspace.add(Statement("*%s = %s.get()" %(
            userspace.arguments()[1][0], # Name of the first argument
            return_variable.name
        )))

    def CancelAlarm(self, abb, userspace, kernelspace):
        alarm = abb.arguments[0]
        self.call_function(kernelspace, "%s.setArmed" % alarm.impl.name,
                           "void", ["false"])
        kernelspace.add(Comment("Dispatch directly back to Userland"))
        self.call_function(kernelspace, "Dispatcher::ResumeToTask",
                           "void",
                           [self.get_calling_task_desc(abb)])

    def GetResource(self, abb, userspace, kernelspace):
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

    def ReleaseResource(self, abb, userspace, kernelspace):
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

        self.arch_rules.disable_irq(block)

    def enable_irq(self, block, abb):
        before = abb.get_outgoing_nodes(E.task_level)
        disabled = [x.interrupt_block_all or x.interrupt_block_os
                    for x in before]
        # If the interrupts were unblocked before do not a thing
        if any(disabled):
            assert all(disabled)
            return

        self.arch_rules.enable_irq(block)

    def DisableAllInterrupts(self, abb, userspace, kernelspace):
        self.disable_irq(kernelspace, abb)
    SuspendAllInterrupts = DisableAllInterrupts
    SuspendOSInterrupts  = DisableAllInterrupts

    def EnableAllInterrupts(self, abb, userspace, kernelspace):
        self.enable_irq(kernelspace, abb)
    ResumeAllInterrupts = EnableAllInterrupts
    ResumeOSInterrupts  = EnableAllInterrupts

    # Dependability Service
    def AcquireCheckedObject(self, abb, userspace, kernelspace):
        co_index = "OS_" + abb.arguments[0][len("OSEKOS_CHECKEDOBJECT_Struct_"):] + "_CheckedObject_Index"
        self.call_function(kernelspace,
                           "acquire_CheckedObject",
                           "void",
                           [co_index])

    def ReleaseCheckedObject(self, abb, userspace, kernelspace):
        co_index = "OS_" + abb.arguments[0][len("OSEKOS_CHECKEDOBJECT_Struct_"):] + "_CheckedObject_Index"
        self.call_function(kernelspace,
                           "release_CheckedObject",
                           "void",
                           [co_index])

    # Assertions
    def do_assertions(self, block, assertions):
        should_equal_zero = []
        should_unequal_zero = []
        for a in assertions:
            (equal_zero, cond) = self.__do_assertion(a)
            if equal_zero:
                should_equal_zero.append(cond)
            else:
                should_unequal_zero.append(cond)

        call_hook = Statement("CALL_HOOK(FaultDetectedHook, STATE_ASSERTdetected, __LINE__, 0)")
        if should_equal_zero:
            check = Block("if ((%s) != 0)" % "  | ".join(should_equal_zero))
            check.add(call_hook)
            block.add(check)
        if should_unequal_zero:
            check = Block("if ((%s) == 0)" % " * ".join(should_unequal_zero))
            check.add(call_hook)
            block.add(check)


    def __do_assertion(self, assertion):
        task = assertion.get_arguments()[0]
        if assertion.isA(AssertionType.TaskIsSuspended):
            cond = "scheduler_.isReady(%s)" % self.task_desc(task)
            return (True, cond)
        elif assertion.isA(AssertionType.TaskIsReady):
            cond = "scheduler_.isReady(%s)" % self.task_desc(task)
            return (False, cond)
        elif assertion.isA(AssertionType.TaskWasKickoffed):
            cond = "%s.tcb.is_running()" % self.task_desc(task)
            return (False, cond)
        elif assertion.isA(AssertionType.TaskWasNotKickoffed):
            cond =  "%s.tcb.is_running()" % self.task_desc(task)
            return (True, cond)
        else:
            panic("Unsupported assert type %s in %s", assertion, block)
