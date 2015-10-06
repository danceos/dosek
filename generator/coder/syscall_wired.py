from .base import BaseCoder
from .elements import Statement, Comment
from .elements import CodeTemplate, Include, VariableDefinition, \
    Block, Statement, Comment, Function, Hook, DataObject, DataObjectArray, \
    FunctionDeclaration
from generator.tools import unwrap_seq
from generator.analysis.AtomicBasicBlock import E,S
from generator.analysis.Function import Function as GraphFunction
from generator.analysis.SystemSemantic import SystemState
from generator.analysis import Subtask
from .syscall_full import AlarmTemplate, FullSystemCalls
import logging

# config-constraint-: (os.systemcalls == wired) -> (arch.self == osek-v)

class WiredSystemCalls(BaseCoder):
    def __init__(self, use_pla = False):
        super(WiredSystemCalls, self).__init__()
        self.syscall_map = {}
        self.alarms = AlarmTemplate

    def task_desc(self, subtask):
        """Returns a string that generates the task id"""
        task_desc = subtask.impl.task_descriptor.name
        return task_desc

    def get_calling_task_desc(self, abb):
        return self.task_desc(abb.function.subtask)

    def generate_system_code(self):
        self.generator.source_file.include("output.h")

        self.logic = self.system_graph.get_pass("LogicMinimizer")
        self.fsm = self.logic.fsm

        # Generate the transition table
        for event in self.fsm.events:
            self.syscall_map[event.name] = event

        self.generator.source_file.declarations.append(self.alarms(self).expand())


    def StartOS(self, kernelspace):
        # kernelspace.add(Statement('kout << "Booted..." << endl;'))
        kernelspace.unused_parameter(0)

        idle_entry = FunctionDeclaration("idle_entry" , "void", [],
                                         extern_c = True)
        self.generator.source_file.function_manager.add(idle_entry)

        for subtask in self.system_graph.real_subtasks:
            # Unused Task
            if not subtask.impl.present:
                continue
            wrapper = Function("OSEKOS_TASK_%s_wrapper" % subtask.name, "void", [],
                               attributes=["__attribute__(( naked ))"],
                               extern_c = True)
            self.generator.source_file.function_manager.add(wrapper)
            
            sp = subtask.impl.stack.name
            self.call_function(wrapper,
                               "Machine::set_sp",
                               "void",
                               ["(void *) (((char *)%s) + sizeof(%s) - 16)" % (sp, sp)])

            
            WHILE = Block("while (1)")
            wrapper.add(WHILE)
            self.call_function(WHILE, subtask.function_name, "void", [])

            self.call_function(kernelspace,
                               "Machine::exchange_saved_ip",
                               "void",
                               [str(subtask.impl.task_id), "(void*) &" +wrapper.function_name])

        StartOS = self.system_graph.get(GraphFunction, "StartOS")
        self.fsm_schedule(StartOS.entry_abb, None, kernelspace)

    def ShutdownOS(self, block):
        FullSystemCalls.ShutdownOS(self, block)

    def fsm_event_number(self, syscall):
        fsm = self.system_graph.get_pass("LogicMinimizer").fsm
        event = None
        for ev in fsm.events:
            if fsm.event_mapping[ev.name] == syscall:
                event = ev
                break
        if event is None:
            return
        return int(event.name, 2)

    def fsm_schedule(self, syscall, userspace, kernelspace):
        number = self.fsm_event_number(syscall)
        if number is None:
            return (syscall, None)
        self.call_function(kernelspace, "Machine::syscall",
                           "void", [str(number)])
        print(syscall, number)


    def kickoff(self, syscall, userspace, kernelspace):
        # If the subtask is activated within an ISR, we reset the idle
        # loop IP here.
        activated_from_isr = False
        for subtask in self.system_graph.subtasks:
            if not subtask.conf.is_isr:
                continue
            for abb in subtask.abbs:
                if not abb.isA(S.ActivateTask):
                    continue
                if abb.arguments[0] == syscall.subtask:
                    activated_from_isr = True
                    break
        if activated_from_isr:
            self.call_function(kernelspace,
                               "Machine::exchange_saved_ip",
                               "void", ["0", "(void*) &idle_entry"])
        self.fsm_schedule(syscall, userspace, kernelspace)
        # Enable Interrupts
        if not syscall.subtask.conf.is_isr:
            self.arch_rules.kickoff(syscall, userspace)


    iret = fsm_schedule
    ChainTask = fsm_schedule
    TerminateTask = fsm_schedule
    ActivateTask = fsm_schedule
    WaitEvent = fsm_schedule
    ClearEvent = fsm_schedule
    SetEvent = fsm_schedule
    GetResource = fsm_schedule
    ReleaseResource = fsm_schedule

    def ASTSchedule(self, function):
        function.unused_parameter(0)

    def AdvanceCounter(self, abb, userspace, kernelspace):
        raise NotImplementedError

    ################################################################
    # These system calls are only enhanced by the FSM step function
    ################################################################
    # Do not overwrite: SetRelAlarm
    # Do not overwrite: GetAlarm
    # Do not overwrite: CancelAlarm
    # Do not overwrite: DisableAllInterrupts
    # Do not overwrite: SuspendAllInterrupts
    # Do not overwrite: SuspendOSInterrupts
    # Do not overwrite: EnableAllInterrupts
    # Do not overwrite: ResumeAllInterrupts
    # Do not overwrite: ResumeOSInterrupts
    # Do not overwrite: AcquireCheckedObject
    # Do not overwrite: ReleaseCheckedObject

    def SetRelAlarm(self, syscall, userspace, kernelspace):
        self.fsm_schedule(syscall, userspace, kernelspace)
        FullSystemCalls.SetRelAlarm(self, syscall, userspace, kernelspace)

    def GetAlarm(self, syscall, userspace, kernelspace):
        self.fsm_schedule(syscall, userspace, kernelspace)
        FullSystemCalls.GetAlarm(self, syscall, userspace, kernelspace)

    def CancelAlarm(self, syscall, userspace, kernelspace):
        self.fsm_schedule(syscall, userspace, kernelspace)
        FullSystemCalls.CancelAlarm(self, syscall, userspace, kernelspace)

    def DisableAllInterrupts(self, syscall, userspace, kernelspace):
        self.fsm_schedule(syscall, userspace, kernelspace)
        FullSystemCalls.DisableAllInterrupts(self, syscall, userspace, kernelspace)

    def SuspendAllInterrupts(self, syscall, userspace, kernelspace):
        self.fsm_schedule(syscall, userspace, kernelspace)
        FullSystemCalls.SuspendAllInterrupts(self, syscall, userspace, kernelspace)

    def SuspendOSInterrupts(self, syscall, userspace, kernelspace):
        self.fsm_schedule(syscall, userspace, kernelspace)
        FullSystemCalls.SuspendOSInterrupts(self, syscall, userspace, kernelspace)

    def EnableAllInterrupts(self, syscall, userspace, kernelspace):
        self.fsm_schedule(syscall, userspace, kernelspace)
        FullSystemCalls.EnableAllInterrupts(self, syscall, userspace, kernelspace)

    def ResumeAllInterrupts(self, syscall, userspace, kernelspace):
        self.fsm_schedule(syscall, userspace, kernelspace)
        FullSystemCalls.ResumeAllInterrupts(self, syscall, userspace, kernelspace)

    def ResumeOSInterrupts(self, syscall, userspace, kernelspace):
        self.fsm_schedule(syscall, userspace, kernelspace)
        FullSystemCalls.ResumeOSInterrupts(self, syscall, userspace, kernelspace)

    def AcquireCheckedObject(self, syscall, userspace, kernelspace):
        self.fsm_schedule(syscall, userspace, kernelspace)
        FullSystemCalls.AcquireCheckedObject(self, syscall, userspace, kernelspace)

    def ReleaseCheckedObject(self, syscall, userspace, kernelspace):
        self.fsm_schedule(syscall, userspace, kernelspace)
        FullSystemCalls.ReleaseCheckedObject(self, syscall, userspace, kernelspace)

    def do_assertions(self, block, assertions):
        """We do not support assertions for a FSM kernel"""
        logging.error("Assertions are not implemented for the FSM coder")

    def enable_irq(self, *args):
        FullSystemCalls.enable_irq(self, *args)

    def disable_irq(self, *args):
        FullSystemCalls.disable_irq(self, *args)



