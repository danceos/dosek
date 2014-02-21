from generator.graph.common import *
from generator.graph.Analysis import *
from generator.graph.DynamicPriorityAnalysis import DynamicPriorityAnalysis
from generator.graph.Sporadic import SporadicEvent
from generator.graph.GlobalAbbInfo import GlobalAbbInfo
from generator.graph.SystemSemantic import *
from generator.tools import panic, stack, unwrap_seq, group_by, select_distinct


class SymbolicSystemExecution(Analysis, GraphObject):
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

        self.transitions = {'StartOS': self.system_call_semantic.do_StartOS,
                            'ActivateTask': self.system_call_semantic.do_ActivateTask,
                            'TerminateTask': self.system_call_semantic.do_TerminateTask,
                            'ChainTask': self.system_call_semantic.do_ChainTask,
                            'computation': self.do_computation_with_sporadic_events,
                            'kickoff': self.system_call_semantic.do_computation, # NO ISRS
                            'SetRelAlarm': self.system_call_semantic.do_computation, # ignore
                            'CancelAlarm': self.system_call_semantic.do_computation, # ignore
                            'GetResource': self.system_call_semantic.do_computation, # Done in DynamicPriorityAnalysis
                            'ReleaseResource': self.system_call_semantic.do_computation, # Done in DynamicPriorityAnalysis
                            'Idle': self.system_call_semantic.do_Idle,
                            'iret': self.system_call_semantic.do_TerminateTask}

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


class StateGraphSubobject(GraphObject):
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

class Combine_RunningTask_SSE(Analysis):
    def __init__(self):
        Analysis.__init__(self)
        self.removed_edges = None

    def requires(self):
        # We require all possible system edges to be contructed
        return ["SystemStateFlow", "SymbolicSystemExecution"]

    def do(self):
        self.removed_edges = []
        SSE = self.system.get_pass("SymbolicSystemExecution")
        for source_abb in SSE.states_by_abb:
            old_global_nodes = set(source_abb.get_outgoing_nodes(E.system_level))
            followup_abbs    = set()
            for state in SSE.states_by_abb[source_abb]:
                followup_abbs |= select_distinct(SSE.states_next[state], "current_abb")
            # Are there edges that where discovered in SSE, that are not already in the graph?
            more_in_SSE = followup_abbs - old_global_nodes
            # Are there edges that where discovered in the graph but not by SSE
            more_in_Graph = old_global_nodes - followup_abbs

            # We can remove all edges from the graph, that are not in
            # SSE, since SSE produces more precise results
            for target_abb in more_in_Graph:
                # FIXME: Jumps from computation might be the result of
                # sporadic actions, but those are not explicitly
                # drawed in the RunningTaskGraph
                if not source_abb.type in ("kickoff", "computation"):
                    edge = source_abb.remove_cfg_edge(target_abb, E.system_level)
                    logging.debug("Removed Edge from %s -> %s", source_abb, target_abb)
                    self.removed_edges.append(edge)

            for target_abb in more_in_SSE:
                if source_abb.function.subtask.is_isr\
                   or target_abb.function.subtask.is_isr:
                    continue

                panic("SSE has found more edges than RunningTask (%s -> %s)", 
                      source_abb.path(), target_abb.path())
