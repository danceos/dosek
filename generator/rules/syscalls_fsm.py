from generator.rules.syscalls_full import FullSystemCalls, AlarmTemplate
from generator.elements import Statement, Comment
from generator.elements import CodeTemplate, Include, VariableDefinition, \
    Block, Statement, Comment, Function, Hook, DataObject, DataObjectArray
from generator.tools import unwrap_seq
from generator.graph.AtomicBasicBlock import E,S
from generator.graph.SystemSemantic import SystemState
import logging


class FSMSystemCalls(FullSystemCalls):
    def __init__(self):
        super(FSMSystemCalls, self).__init__()

        self.alarms = FSMAlarmTemplate
        self.fsm_template = SimpleFSMTemplate

    def generate_system_code(self):
        self.generator.source_file.includes.add(Include("syscall.h"))

        # Grab the finite state machine
        self.fsm = self.system_graph.get_pass("fsm").fsm

        # Use the fsm template
        self.generator.source_file.includes.add(Include("reschedule-ast.h"))

        self.generator.source_file.includes.add(Include("os/scheduler/task.h"))
        self.generator.source_file.declarations.append(self.fsm_template(self).expand())

        self.generator.source_file.includes.add(Include("os/alarm.h"))
        self.generator.source_file.includes.add(Include("os/util/redundant.h"))
        self.generator.source_file.declarations.append(self.alarms(self).expand())



        self.syscall_map = {}
        # Generate the transition table
        for event in self.fsm.events:
            self.syscall_map[event.name] = event
            table = DataObjectArray("os::fsm::SimpleFSM::Transition", "fsm_table_" + event.name.generated_function_name(),
                                    str(len(event.transitions)))
            inits = []
            for trans in event.transitions:
                task_id = trans.action.impl.task_id
                if task_id == None:
                    assert event.name.subtask.conf.is_isr
                    task_id = 255
                inits.append("{%d, %d, %s}" % (trans.source, trans.target,
                                               task_id))
            table.static_initializer = inits
            event.impl.transition_table = table

            self.generator.source_file.data_manager\
                .add(table, namespace = ('os', 'fsm'))

        # The state machine instance
        self.fsm.impl = "fsm_engine"

    def StartOS(self, block):
        block.unused_parameter(0)
        for subtask in self.system_graph.real_subtasks:
            # Use Reset the stack pointer for all all tasks
            self.call_function(block,
                               self.task_desc(subtask) + ".tcb.reset",
                               "void", [])


        # Call the StartupHook
        self.call_function(block, "CALL_HOOK", "void", ["StartupHook"])

        # Bootstrap: Do the initial syscall
        dispatch_func = Function("__OS_StartOS_dispatch", "void", ["int"], extern_c = True)
        self.generator.source_file.function_manager.add(dispatch_func)

        # Initial SystemCall
        for ev in self.fsm.events:
            if ev.name.isA(S.StartOS):
                self.fsm_schedule(ev.name, block, dispatch_func)
                break

        self.call_function(block, "arch::syscall", "void",
                           [dispatch_func.function_name])
        self.call_function(block, "Machine::unreachable", "void", [])

    def fsm_event(self, syscall, userspace, kernelspace):
        if not syscall in self.syscall_map:
            return
        event = self.syscall_map[syscall]

        transition_table  = event.impl.transition_table.name
        transition_length = str(len(event.transitions))

        # kernelspace.add(Statement('kout << "%s" << endl' % syscall.path()))
        task = self.call_function(kernelspace, "os::fsm::fsm_engine.event",
                               "SimpleFSM::task_t", [transition_table, transition_length])
        return task


    def fsm_schedule(self, syscall, userspace, kernelspace):
        if not syscall in self.syscall_map:
            return
        task = self.fsm_event(syscall, userspace, kernelspace)
        self.call_function(kernelspace, "os::fsm::fsm_engine.dispatch",
                               "void", [task.name])

    def kickoff(self, syscall, userspace, kernelspace):
        self.fsm_event(syscall, userspace, kernelspace)
        if not syscall.subtask.conf.is_isr:
            self.arch_rules.kickoff(syscall, userspace)


    def TerminateTask(self, syscall, userspace, kernelspace):
        self.call_function(kernelspace, self.task_desc(syscall.subtask) + ".tcb.reset",
                           "void", [])
        self.fsm_schedule(syscall, userspace, kernelspace)

    def iret(self, syscall, userspace, kernelspace):
        if not syscall in self.syscall_map:
            return
        task = self.fsm_event(syscall, userspace, kernelspace)
        self.call_function(kernelspace, "os::fsm::fsm_engine.iret",
                               "void", [task.name])


    ChainTask = TerminateTask
    ActivateTask = fsm_schedule
    WaitEvent = fsm_schedule
    ClearEvent = fsm_schedule
    SetEvent = fsm_schedule
    GetResource = fsm_schedule
    ReleaseResource = fsm_schedule

    def ASTSchedule(self, function):
        pass

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
        self.fsm_event(syscall, userspace, kernelspace)
        FullSystemCalls.SetRelAlarm(self, syscall, userspace, kernelspace)

    def GetAlarm(self, syscall, userspace, kernelspace):
        self.fsm_event(syscall, userspace, kernelspace)
        FullSystemCalls.GetAlarm(self, syscall, userspace, kernelspace)

    def CancelAlarm(self, syscall, userspace, kernelspace):
        self.fsm_event(syscall, userspace, kernelspace)
        FullSystemCalls.CancelAlarm(self, syscall, userspace, kernelspace)

    def DisableAllInterrupts(self, syscall, userspace, kernelspace):
        self.fsm_event(syscall, userspace, kernelspace)
        FullSystemCalls.DisableAllInterrupts(self, syscall, userspace, kernelspace)

    def SuspendAllInterrupts(self, syscall, userspace, kernelspace):
        self.fsm_event(syscall, userspace, kernelspace)
        FullSystemCalls.SuspendAllInterrupts(self, syscall, userspace, kernelspace)

    def SuspendOSInterrupts(self, syscall, userspace, kernelspace):
        self.fsm_event(syscall, userspace, kernelspace)
        FullSystemCalls.SuspendOSInterrupts(self, syscall, userspace, kernelspace)

    def EnableAllInterrupts(self, syscall, userspace, kernelspace):
        self.fsm_event(syscall, userspace, kernelspace)
        FullSystemCalls.EnableAllInterrupts(self, syscall, userspace, kernelspace)

    def ResumeAllInterrupts(self, syscall, userspace, kernelspace):
        self.fsm_event(syscall, userspace, kernelspace)
        FullSystemCalls.ResumeAllInterrupts(self, syscall, userspace, kernelspace)

    def ResumeOSInterrupts(self, syscall, userspace, kernelspace):
        self.fsm_event(syscall, userspace, kernelspace)
        FullSystemCalls.ResumeOSInterrupts(self, syscall, userspace, kernelspace)

    def AcquireCheckedObject(self, syscall, userspace, kernelspace):
        self.fsm_event(syscall, userspace, kernelspace)
        FullSystemCalls.AcquireCheckedObject(self, syscall, userspace, kernelspace)

    def ReleaseCheckedObject(self, syscall, userspace, kernelspace):
        self.fsm_event(syscall, userspace, kernelspace)
        FullSystemCalls.ReleaseCheckedObject(self, syscall, userspace, kernelspace)

    def do_assertions(self, block, assertions):
        """We do not support assertions for a FSM kernel"""
        logging.error("Assertions are not implemented for the FSM coder")


class SimpleFSMTemplate(CodeTemplate):
    def __init__(self, rules):
        CodeTemplate.__init__(self, rules.generator, "os/fsm/simple-fsm.h.in")
        self.rules = rules
        self.system_graph = self.generator.system_graph

        self.rules.generator.source_file.includes.add(Include("os/fsm/simple-fsm.h"))

        self.fsm = self.rules.fsm

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


class FSMAlarmTemplate(AlarmTemplate):
    def __init__(self, rules):
        AlarmTemplate.__init__(self, rules)

