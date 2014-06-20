from generator.graph.common import *
from generator.graph.Analysis import *
from generator.graph.GlobalAbbInfo import GlobalAbbInfo
from generator.graph.SystemSemantic import *
from generator.tools import stack, unwrap_seq, group_by, IntEnum

@unique
class StateTransitionEdge(IntEnum):
    """All used edge types"""
    common = 1

StateTransition = StateTransitionEdge.common

class SymbolicSystemExecution(Analysis, GraphObject):
    """This pass executes the system state symbolic. The whole system
       state space is explored. This is more precise than the state
       flow analysis, but may take longer, since it might explode.

    """
    pass_alias = "sse"

    def __init__(self):
        Analysis.__init__(self)
        GraphObject.__init__(self, "SymbolicSystemState", root = True)
        self.states = None
        self.states_by_abb = None

        # A member for the RunningTask analysis
        self.running_task = None
        # The SystemCall semantic
        self.system_call_semantic = None

        self.working_stack = None

        self.transitions = None

        self.__abb_info_cache = {}

    def requires(self):
        # We require all possible system edges to be contructed
        return ["DynamicPriorityAnalysis", "InterruptControlAnalysis"]

    def get_edge_filter(self):
        return set([E.function_level, E.task_level])

    def graph_subobjects(self):
        if len(self.states) > 500:
            return []
        ret = []
        for abb, states in self.states_by_abb.items():
            assert all([x.current_abb == abb for x in states])
            cont = GraphObjectContainer(str(abb), color="red",
                                        subobjects=list(states))
            cont.data = {"ABB": str(abb), "func": abb.function.name}
            cont.abb = abb
            ret.append(cont)

        ret = list(sorted(ret, key=lambda x: x.abb.abb_id))

        return ret

    def state_transition(self, source_block, source_state, target_block, target_state):
        # print(source_block.path(),"->", target_block.path())
        # Do not allow self loops
        #if source_state == target_state:
        #    return
        if target_state in self.states:
            real_instance = self.states[target_state]
            source_state.add_cfg_edge(real_instance, StateTransition)
        else:
            self.working_stack.push(target_state)
            source_state.add_cfg_edge(target_state, StateTransition)

    def state_functor(self, state):
        # Do the System Call
        after_states = self.system_call_semantic.do_SystemCall(
            state.current_abb, state, self.transitions)

        # Schedule on each possible block
        for next_state in after_states:
            self.system_call_semantic.schedule(state.current_abb, next_state,
                                               lambda source, target, new_state: \
                                                 self.state_transition(source, state, target, new_state))

    def do_computation_with_sporadic_events(self, block, before):
        after_states = self.system_call_semantic.do_computation_with_callstack(block, before)

        # Handle sporadic events
        for sporadic_event in self.system_graph.alarms + self.system_graph.isrs:
            if not sporadic_event.can_trigger(before):
                continue
            after = sporadic_event.trigger(before)
            after_states.append(after)

        return after_states

    def do(self):
        old_copy_count = SystemState.copy_count
        self.running_task = self.get_analysis(CurrentRunningSubtask.name())

        # Instanciate a new system call semantic
        self.system_call_semantic = SystemCallSemantic(self.system_graph, self.running_task)
        scc = self.system_call_semantic

        self.transitions = {S.StartOS         : scc.do_StartOS,
                            S.ActivateTask    : scc.do_ActivateTask,
                            S.TerminateTask   : scc.do_TerminateTask,
                            S.ChainTask       : scc.do_ChainTask,
                            S.computation     : self.do_computation_with_sporadic_events,
                            S.kickoff         : scc.do_computation, # NO ISRS
                            S.SetRelAlarm     : scc.do_computation, # ignore
                            S.CancelAlarm     : scc.do_computation, # ignore
                            # Done in DynamicPriorityAnalysis
                            S.GetResource          : scc.do_computation,
                            S.ReleaseResource      : scc.do_computation,
                            # Done in InterruptControlAnalysis
                            S.DisableAllInterrupts : scc.do_computation,
                            S.EnableAllInterrupts  : scc.do_computation,
                            S.SuspendAllInterrupts : scc.do_computation,
                            S.ResumeAllInterrupts  : scc.do_computation,
                            S.SuspendOSInterrupts  : scc.do_computation,
                            S.ResumeOSInterrupts   : scc.do_computation,

                            S.Idle            : scc.do_Idle,
                            S.iret            : scc.do_TerminateTask}

        # Instanciate the big dict (State->State)
        self.states = {}

        entry_abb = self.system_graph.functions["StartOS"].entry_abb
        before_StartOS = PreciseSystemState(self.system_graph)
        before_StartOS.current_abb = entry_abb
        for subtask in before_StartOS.get_unordered_subtasks():
            before_StartOS.call_stack[subtask.subtask_id] = stack()
        before_StartOS.frozen = True

        self.working_stack = stack()
        self.working_stack.push(before_StartOS)

        state_count = 0
        ignored_count = 0
        while not self.working_stack.isEmpty():
            # Current is a system state
            current = self.working_stack.pop()
            # State was already marked as done!
            if current in self.states:
                ignored_count += 1
                continue
            # The current state is marked as done. This dictionary is
            # used to translate all equal system states to a single instance/object.
            self.states[current] = current
            state_count += 1
            if (state_count % 10000) == 0 and state_count > 0:
                logging.info(" + already %d states (%d on stack, %d ignored)", 
                             state_count, len(self.working_stack), ignored_count)

            self.state_functor(current)

        logging.info(" + symbolic execution done")

        self.transform_isr_transitions()

        # Group States by ABB
        self.states_by_abb = group_by(self.states, "current_abb")
        logging.info(" + %d system states", len(self.states))

        # Set analysis to valid, since only statistics follow from here.
        self.valid = True

        ################################################################
        # Statistics
        ################################################################

        # Record the number of copied system states
        self.system_graph.stats.add_data(self, "copied-system-states",
                                         SystemState.copy_count - old_copy_count,
                                         scalar = True)

        # Record the precision indicators for each abb
        # Count the number of ABBs in the system the analysis works on
        is_relevant = self.system_graph.passes["AddFunctionCalls"].is_relevant_function
        abbs = [x for x in self.system_graph.get_abbs() if is_relevant(x.function)]
        precisions = []
        for abb in abbs:
            if not abb.function.subtask or not abb.function.subtask.is_real_thread:
                continue
            x = self.for_abb(abb)
            if x:
                precision = x.state_before.precision()
                if not abb.isA(S.StartOS):
                    self.stats.add_data(abb, "sse-precision", precision, scalar=True)
                precisions.append(precision)
            else:
                # State will not be visited, this is for sure
                precisions.append(1.0)
        self.stats.add_data(self, "precision", precisions, scalar = True)

    def transform_isr_transitions(self):
        # Special casing of sporadic events What happens here: In
        # order to seperate interrupt space from the application
        # space, we purge all state transitions from the application
        # level to interrupt level. We connect the interrupt handler
        # continuation with the block that activates the interrupt.
        def is_isr_state(state):
            if not state.current_abb.function.subtask:
                return False
            return state.current_abb.function.subtask.is_isr
        del_edges = []
        add_edges = []
        for app_level in [x for x in self.states if not is_isr_state(x)]:
            for isr_level in[x for x in app_level.get_outgoing_nodes(StateTransition)
                           if is_isr_state(x)]:
                # Remove the Interrupt activation Edge
                del_edges.append((app_level, isr_level))

                # Now we have to find all iret states that can
                # follow. We do this in depth-first-search
                ws = stack([isr_level])
                exits = set()
                while not ws.isEmpty():
                    iret = ws.pop()
                    if iret.current_abb.isA(S.iret):
                        for retpoint in iret.get_outgoing_nodes(StateTransition):
                            del_edges.append((iret, retpoint))
                            add_edges.append((app_level, retpoint))
                    else:
                        # Not an IRET
                        ws.extend(iret.get_outgoing_nodes(StateTransition))

        for source, target in del_edges:
            x = source.remove_cfg_edge(target, StateTransition)
        for source, target in add_edges:
            source.add_cfg_edge(target, StateTransition)

    def fsck(self):
        pass
        #for state in self.states:
        #    for next_state in state.get_outgoing_nodes(StateTransition):
        #        assert id(self.states[state]) == id(state)
        #    for next_state in state.get_incoming_nodes(StateTransition):
        #        assert id(self.states[state]) == id(state)

    def for_abb(self, abb):
        """Return a GlobalAbbInformation object for this object"""
        assert self.valid, "The analysis is not valid"
        if abb in self.__abb_info_cache:
            return self.__abb_info_cache[abb]
        if abb in self.states_by_abb:
            info = SSE_GlobalAbbInfo(self, abb)
            self.__abb_info_cache[abb] = info
            return info

class SSE_GlobalAbbInfo(GlobalAbbInfo):
    def __init__(self, analysis, abb):
        GlobalAbbInfo.__init__(self)
        self.analysis = analysis
        self.abb      = abb
        assert self.analysis.valid, "SymbolicSystemExecution is not valid"
        self.__cached_state_before = None
        self.__cached_states_after = None
        self.__cached_abbs_before  = None

    @property
    def state_before(self):
        if not self.__cached_state_before:
            # The saved states is always before the effect of the abb has
            # taken place
            states_in_this_abb = self.analysis.states_by_abb[self.abb]

            self.__cached_state_before = \
                SystemState.merge_many(self.analysis.system_graph, states_in_this_abb)

        return self.__cached_state_before

    @property
    def states_after(self):
        """Returns a list of possible next system states"""
        if not self.__cached_states_after:
            self.__cached_states_after = set()
            for source_state in self.analysis.states_by_abb[self.abb]:
                followup = source_state.get_outgoing_nodes(StateTransition)
                self.__cached_states_after.update(followup)

        return self.__cached_states_after

    @property
    def abbs_before(self):
        """Returns list of possible source ABBS"""
        if not self.__cached_abbs_before:
            self.__cached_abbs_before = set()
            for source_state in self.analysis.states_by_abb[self.abb]:
                prev_states = source_state.get_incoming_nodes(StateTransition)
                for prev_state in prev_states:
                    self.__cached_abbs_before.add(prev_state.current_abb)
        return self.__cached_abbs_before

