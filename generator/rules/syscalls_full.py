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

        # Bootstrap: Do the initial syscall
        dispatch_func = Function("__OS_StartOS_dispatch", "void", ["int"], extern_c = True)
        self.objects["__OS_StartOS_dispatch"] = dispatch_func
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

    def kickoff(self, block, abb):
        block.attributes.append("inlinehint")
        if not abb.function.subtask.is_isr:
            self.arch_rules.kickoff(block, abb)

    def TerminateTask(self, block, abb):
        self.call_function(block, "scheduler_.TerminateTask_impl",
                           "void",
                           [self.get_calling_task_desc(abb)])

    def ActivateTask(self, block, abb):
        self.call_function(block,
                           "scheduler_.ActivateTask_impl",
                           "void",
                           [self.task_desc(abb.arguments[0])])

    def ChainTask(self, block, abb):
        self.call_function(block,
                           "scheduler_.ChainTask_impl",
                           "void",
                           [self.get_calling_task_desc(abb),
                            self.task_desc(abb.arguments[0])])


    def SetRelAlarm(self, kernelspace, abb, arguments):
        arg1 = self.arch_rules.get_syscall_argument(kernelspace, 0)
        arg2 = self.arch_rules.get_syscall_argument(kernelspace, 1)
        alarm_id = abb.arguments[0]
        alarm_object = self.objects["alarm"][alarm_id]
        self.call_function(kernelspace, "%s.setRelativeTime" % alarm_object.name,
                           "void", [arg1.name])
        self.call_function(kernelspace, "%s.setCycleTime" % alarm_object.name,
                           "void", [arg2.name])
        self.call_function(kernelspace, "%s.setArmed" % alarm_object.name,
                           "void", ["true"])
        kernelspace.add(Comment("Dispatch directly back to Userland"))
        self.call_function(kernelspace, "Dispatcher::ResumeToTask",
                           "void",
                           [self.get_calling_task_desc(abb)])

    def AdvanceCounter(self, kernelspace, abb):
        counter_id = abb.arguments[0]
        counter = self.objects["counter"][counter_id]

        # Increase Counter and check the counter
        kernelspace.add(Statement("%s.do_tick()" % counter.name))
        for alarm in self.system_graph.alarms:
            if alarm.counter == counter_id:
                kernelspace.add(Statement("AlarmCheck%s()" % self.objects["alarm"][alarm.name].name))

        kernelspace.add(Comment("Dispatch directly back to Userland"))
        self.call_function(kernelspace, "Dispatcher::ResumeToTask",
                           "void",
                           [self.get_calling_task_desc(abb)])

    def GetAlarm(self, userspace, kernelspace, abb):
        alarm_id = abb.arguments[0]
        alarm_object = self.objects["alarm"][alarm_id]

        return_variable = self.os_rules.get_syscall_return_variable("TickType")

        # Fill return variable
        kernelspace.add(Statement("%s.set(%s.getRemainingTicks())"%(
            return_variable.name,
            alarm_object.name)))

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

    def DisableAllInterrupts(self, userspace, abb):
        self.disable_irq(userspace, abb)

    def EnableAllInterrupts(self, userspace, abb):
        self.enable_irq(userspace, abb)

    # Dependability Service
    def AcquireCheckedObject(self, block, abb):
        co_index = "OS_" + abb.arguments[0][len("OSEKOS_CHECKEDOBJECT_Struct_"):] + "_CheckedObject_Index"
        self.call_function(block,
                           "acquire_CheckedObject",
                           "void",
                           [co_index])

    def ReleaseCheckedObject(self, block, abb):
        co_index = "OS_" + abb.arguments[0][len("OSEKOS_CHECKEDOBJECT_Struct_"):] + "_CheckedObject_Index"
        self.call_function(block,
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
