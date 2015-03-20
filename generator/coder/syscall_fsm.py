from .syscall_full import FullSystemCalls, AlarmTemplate
from .elements import Statement, Comment
from .elements import CodeTemplate, Include, VariableDefinition, \
    Block, Statement, Comment, Function, Hook, DataObject, DataObjectArray
from generator.tools import unwrap_seq
from generator.analysis.AtomicBasicBlock import E,S
from generator.analysis.SystemSemantic import SystemState
from generator.analysis import Subtask
import logging


class FSMSystemCalls(FullSystemCalls):
    def __init__(self, use_pla = False):
        super(FSMSystemCalls, self).__init__()

        self.alarms = FSMAlarmTemplate
        if use_pla:
            self.fsm_template = PLA_FSMTemplate
        else:
            self.fsm_template = SimpleFSMTemplate


    def generate_system_code(self):
        self.generator.source_file.include("syscall.h")

        # Grab the finite state machine
        self.fsm = self.system_graph.get_pass("fsm").fsm

        # Use the fsm template
        self.generator.source_file.include("reschedule-ast.h")

        self.generator.source_file.include("os/scheduler/task.h")
        self.impl = self.fsm_template(self)
        self.impl.add_transition_table()
        self.generator.source_file.declarations.append(self.impl.expand())

        self.generator.source_file.include("os/alarm.h")
        self.generator.source_file.include("os/util/redundant.h")
        self.generator.source_file.declarations.append(self.alarms(self).expand())

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

    # Forward fsm_schedule and fsm_event
    def fsm_event(self, *args, **kwargs):
        self.impl.fsm_event(*args, **kwargs)

    def fsm_schedule(self, *args, **kwargs):
        self.impl.fsm_schedule(*args, **kwargs)

    def iret(self, *args, **kwargs):
        self.impl.fsm_iret(*args, **kwargs)


    def kickoff(self, syscall, userspace, kernelspace):
        self.fsm_event(syscall, userspace, kernelspace)
        if not syscall.subtask.conf.is_isr:
            self.arch_rules.kickoff(syscall, userspace)


    def TerminateTask(self, syscall, userspace, kernelspace):
        self.call_function(kernelspace, self.task_desc(syscall.subtask) + ".tcb.reset",
                           "void", [])
        self.fsm_schedule(syscall, userspace, kernelspace)


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
    def __init__(self, syscall_fsm):
        CodeTemplate.__init__(self, syscall_fsm.generator, "os/fsm/simple-fsm.h.in")
        self.syscall_fsm = syscall_fsm
        self.system_graph = self.generator.system_graph

        self.syscall_fsm.generator.source_file.include("os/fsm/simple-fsm.h")

        self.fsm = self.syscall_fsm.fsm

    def add_transition_table(self):
        self.syscall_map = {}

        # Rename action labels to their task id
        def action_rename(action):
            task_id = action.impl.task_id
            if task_id == None:
                task_id = 255
            return task_id
        self.fsm.rename(actions = action_rename)

        # Generate the transition table
        for event in self.fsm.events:
            self.syscall_map[event.name] = event

            # Do not generate a transition table, if there is only one
            # transition.
            if len(event.transitions) == 1:
                event.impl.transition_table = None
                continue

            table = DataObjectArray("os::fsm::SimpleFSM::Transition",
                                    "fsm_table_" + event.name.generated_function_name(),
                                    str(len(event.transitions)))
            table.static_initializer = []
            for t in event.transitions:
                table.static_initializer\
                     .append("{%d, %d, %d}" % (t.source, t.target, t.action))
            event.impl.transition_table = table

            self.syscall_fsm.generator.source_file.data_manager\
                .add(table, namespace = ('os', 'fsm'))

    def fsm_event(self, syscall, userspace, kernelspace):
        if not syscall in self.syscall_map:
            return
        event = self.syscall_map[syscall]

        if event.impl.transition_table:
            transition_table  = event.impl.transition_table.name
            transition_length = str(len(event.transitions))

            # kernelspace.add(Statement('kout << "%s" << endl' % syscall.path()))
            task = self.syscall_fsm.call_function(kernelspace, "os::fsm::fsm_engine.event",
                                                  "SimpleFSM::task_t", [transition_table, transition_length])
        else:
            followup_state = event.impl.followup_state = event.transitions[0].target
            self.syscall_fsm.call_function(kernelspace, "os::fsm::fsm_engine.set_state",
                                                  "void", [str(followup_state)])

            task = event.transitions[0].action

        return task

    def fsm_schedule(self, syscall, userspace, kernelspace):
        if not syscall in self.syscall_map:
            return
        task = self.fsm_event(syscall, userspace, kernelspace)

        if type(task) == int:
            self.syscall_fsm.call_function(kernelspace, "os::fsm::fsm_engine.dispatch",
                                           "void", [str(task)])
        else:
            self.syscall_fsm.call_function(kernelspace, "os::fsm::fsm_engine.dispatch",
                                           "void", [task.name])

    def fsm_iret(self, syscall, userspace, kernelspace):
        if not syscall in self.syscall_map:
            return
        task = self.fsm_event(syscall, userspace, kernelspace)
        if type(task) == int:
            self.syscall_fsm.call_function(kernelspace, "os::fsm::fsm_engine.iret",
                                           "void", [str(task)])
        else:
            self.syscall_fsm.call_function(kernelspace, "os::fsm::fsm_engine.iret",
                                           "void", [task.name])

    ################################################################
    # Used in Template Code
    ################################################################
    def subtask_desc(self, snippet, args):
        return self._subtask.impl.task_descriptor.name

    def subtask_id(self, snippet, args):
        return str(self._subtask.impl.task_id)

    def foreach_subtask_sorted(self, snippet, args):
        body = args[0]
        ret = []
        for subtask in sorted(self.system_graph.real_subtasks, key=lambda s: s.impl.task_id):
            self._subtask = subtask
            ret.append(self.expand_snippet(body))
        return ret

class PLA_FSMTemplate(CodeTemplate):
    def __init__(self, syscall_fsm):
        CodeTemplate.__init__(self, syscall_fsm.generator, "os/fsm/pla-fsm.h.in")
        self.syscall_fsm = syscall_fsm
        self.system_graph = self.generator.system_graph
        self.logic = self.system_graph.get_pass("LogicMinimizer")
        self.fsm = self.logic.fsm

    def add_transition_table(self):
        # Truth table is generated in pla-fsm.h
        return


    def fsm_event(self, syscall, userspace, kernelspace):
        event = None
        for ev in self.fsm.events:
            if self.fsm.event_mapping[ev.name] == syscall:
                event = ev
                break
        if not event:
            return # No Dispatch
        # kernelspace.add(Statement('kout << "%s" << endl' % syscall.path()))
        task = self.syscall_fsm.call_function(kernelspace, "os::fsm::fsm_engine.event",
                                              "unsigned", [str(int(event.name, 2))])
        return task

    def fsm_schedule(self, syscall, userspace, kernelspace):
        task = self.fsm_event(syscall, userspace, kernelspace)
        if not task:
            return
        if type(task) == int:
            self.syscall_fsm.call_function(kernelspace, "os::fsm::fsm_engine.dispatch",
                                           "void", [str(task)])
        else:
            self.syscall_fsm.call_function(kernelspace, "os::fsm::fsm_engine.dispatch",
                                           "void", [task.name])

    def fsm_iret(self, syscall, userspace, kernelspace):
        task = self.fsm_event(syscall, userspace, kernelspace)
        if not task:
            return

        if type(task) == int:
            self.syscall_fsm.call_function(kernelspace, "os::fsm::fsm_engine.iret",
                                           "void", [str(task)])
        else:
            self.syscall_fsm.call_function(kernelspace, "os::fsm::fsm_engine.iret",
                                           "void", [task.name])

    ################################################################
    # Used in Template Code
    ################################################################
    def truth_table(self, *args):
        # Generate the transition table
        initializer = []
        for (mask, pattern, output_state, output_action) in self.logic.truth_table:
            initializer.append("{{{0}, {1}, {2}, {3}}}".format(
                int(mask, 2),
                int(pattern, 2),
                int(output_state, 2),
                int(output_action, 2)))

        return "{" + (", ".join(initializer)) + "}"

    def mask_pattern_len(self, *args):
        return str(self.logic.event_len + self.logic.state_len)

    def truth_table_entries(self, *args):
        return str(len(self.logic.truth_table))

    def initial_state(self, *args):
        return str(int(self.fsm.initial_state,2))

    def dispatch_table(self, *args):
        mapping = {}
        for k, subtask in self.fsm.action_mapping.items():
            mapping[int(k, 2)] = subtask
        if not 0 in mapping:
            mapping[0] = None
        self.NO_DISPATCH = 0

        initializer = []
        for k,subtask in sorted(mapping.items(), key = lambda x:x[0]):
            if not subtask or subtask.conf.is_isr:
                initializer.append("0 /* NO_DISPATCH */")
            elif subtask == self.system_graph.idle_subtask:
                initializer.append("0 /* IDLE */")
                self.IDLE = k
            else:
                initializer.append("&" +subtask.impl.task_descriptor.name)
        if not hasattr(self, "IDLE"):
            self.IDLE = len(mapping) + 100
        return ", ".join(initializer)

class FSMAlarmTemplate(AlarmTemplate):
    def __init__(self, rules):
        AlarmTemplate.__init__(self, rules)
