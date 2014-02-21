from generator.graph.common import *
from generator.graph.Analysis import *
from generator.graph.DynamicPriorityAnalysis import DynamicPriorityAnalysis
from generator.graph.Sporadic import SporadicEvent
from generator.graph.GlobalAbbInfo import GlobalAbbInfo
from generator.graph.SystemSemantic import *
from generator.tools import panic, stack, unwrap_seq, group_by, select_distinct

class SymbolicSystemExecution(Analysis, GraphObject):
    """This pass executes the system state symbolic. The whole system
       state space is explored. This is more precise than the state
       flow analysis, but may take longer, since it might explode.

    """
    def __init__(self):
        Analysis.__init__(self)
        GraphObject.__init__(self, "SymbolicSystemState", root = True)
        self.states_next = None
        self.states_by_abb = None

        # A member for the RunningTask analysis
        self.running_task = None
        # The SystemCall semantic
        self.system_call_semantic = None

        self.working_stack = None

        self.transitions = None

    def requires(self):
        # We require all possible system edges to be contructed
        return ["DynamicPriorityAnalysis"]

    def get_edge_filter(self):
        return set([E.function_level, E.task_level])

    def graph_subobjects(self):
        # Wrap each state in a graph subobject
        subobjects = dict([(x, StateGraphSubobject(self, x))
                           for x in self.states_next.keys()])

        abbs = {}
        # Construct the control flow edges
        for state, next_states in self.states_next.items():
            abb = state.current_abb
            if not abb in abbs:
                abbs[abb] = GraphObjectContainer(label = str(abb),
                                                 color = 'red',
                                                 data = abb.dump())
            abbs[abb].subobjects.append(subobjects[state])
            for next_state in next_states:
                edge = Edge(subobjects[state], subobjects[next_state])
                subobjects[state].edges.append(edge)

        return abbs.values()

    def state_transition(self, source_block, source_state, target_block, target_state):
        # print source_block.path(),"->", target_block.path()
        # Do not allow self loops
        if source_state == target_state:
            return
        self.states_next.setdefault(source_state, set())
        self.states_next[source_state].add(target_state)
        if not target_state in self.states_next:
            self.working_stack.push(target_state)

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

        # When there is no further local abb node, we have reached the
        # end of the interrupt handler
        current_subtask = before.current_abb.function.subtask

        # Handle sporadic events
        for sporadic_event in self.system.alarms + self.system.isrs:
            if not sporadic_event.can_trigger(before):
                continue
            after = sporadic_event.trigger(before)
            after_states.append(after)

        return after_states

    def do(self):
        self.running_task = self.get_analysis(CurrentRunningSubtask.name())

        # Instanciate a new system call semantic
        self.system_call_semantic = SystemCallSemantic(self.system, self.running_task)

        self.transitions = {S.StartOS: self.system_call_semantic.do_StartOS,
                            S.ActivateTask: self.system_call_semantic.do_ActivateTask,
                            S.TerminateTask: self.system_call_semantic.do_TerminateTask,
                            S.ChainTask: self.system_call_semantic.do_ChainTask,
                            S.computation: self.do_computation_with_sporadic_events,
                            S.kickoff: self.system_call_semantic.do_computation, # NO ISRS
                            S.SetRelAlarm: self.system_call_semantic.do_computation, # ignore
                            S.CancelAlarm: self.system_call_semantic.do_computation, # ignore
                            S.GetResource: self.system_call_semantic.do_computation, # Done in DynamicPriorityAnalysis
                            S.ReleaseResource: self.system_call_semantic.do_computation, # Done in DynamicPriorityAnalysis
                            S.Idle: self.system_call_semantic.do_Idle,
                            S.iret: self.system_call_semantic.do_TerminateTask}

        # Instanciate the big dict (State->[State])
        self.states_next = {}

        entry_abb = self.system.functions["StartOS"].entry_abb
        before_StartOS = SystemState(self.system)
        before_StartOS.current_abb = entry_abb
        for subtask in before_StartOS.states.keys():
            before_StartOS.call_stack[subtask] = stack()
        before_StartOS.frozen = True

        self.working_stack = stack()
        self.working_stack.push(before_StartOS)

        while not self.working_stack.isEmpty():
            current = self.working_stack.pop()
            if current in self.states_next:
                continue
            self.state_functor(current)

        # Group States by ABB
        self.states_by_abb = group_by(self.states_next.keys(), "current_abb")

    def for_abb(self, abb):
        """Return a GlobalAbbInformation object for this object"""
        assert self.valid
        if abb in self.states_by_abb:
            return SSE_GlobalAbbInfo(self, abb)



class SSE_GlobalAbbInfo(GlobalAbbInfo):
    def __init__(self, analysis, abb):
        GlobalAbbInfo.__init__(self)
        self.analysis = analysis
        self.abb      = abb
        assert self.analysis.valid, "SymbolicSystemExecution is not valid"

        # The saved states is always before the effect of the abb has
        # taken place
        states_in_this_abb = self.analysis.states_by_abb[abb]

        self.__cached_state_before = \
            SystemState.merge_many(self.analysis.system, states_in_this_abb)

        self.__cached_states_after = set()
        for source_state in states_in_this_abb:
            self.__cached_states_after.update(self.analysis.states_next[source_state])

    @property
    def state_before(self):
        return self.__cached_state_before

    @property
    def states_after(self):
        """Returns a list of possible next system states"""
        return self.__cached_states_after


class StateGraphSubobject(GraphObject):
    """Just a helper class to print the state graph"""
    def __init__(self, analysis, state):
        GraphObject.__init__(self, "State",
                             color = 'green')
        self.analysis = analysis
        self.state = state
        self.edges = []

    def graph_edges(self):
        return self.edges

    def dump(self):
        ret = {}
        for subtask, state in self.state.states.items():
            ret[subtask.name] = self.state.format_state(state)
            conts = self.state.get_continuations(subtask)
            assert len(conts) <= 1
            if len(conts) == 1:
                ret[subtask.name] += " " + str(unwrap_seq(conts))


        return ret
