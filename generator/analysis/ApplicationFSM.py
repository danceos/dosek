from .common import *
from .Analysis import Analysis
from .AtomicBasicBlock import E, S
from .Function import Function
from datastructures.fsm import *
from collections import defaultdict
import logging

class ApplicationFSM(Analysis, GraphObject):
    """The Application FSM Pass transforms the ICFG of every task in the
    system to an finite state machine with fewer edges and vertices,
    than the ICFG. In this transformation, the possible sequences of
    systemcalls coming from an application are preserved.

    """

    pass_alias = "app-fsm"

    def __init__(self):
        Analysis.__init__(self)
        GraphObject.__init__(self, "ApplicationFSM", root = True)

    def requires(self):
        # We require all possible system edges to be contructed
        return ["DynamicPriorityAnalysis", "InterruptControlAnalysis"]

    def get_edge_filter(self):
        return set([E.task_level])

    def graph_subobjects(self):
        ret = []
        for subtask in self.system_graph.subtasks:
            wrapper = GraphObjectContainer(str(subtask), color='red')
            nodes = {}
            for trans in subtask.conf.fsm.transitions:
                if not trans.source in nodes:
                    nodes[trans.source] = Node(None, str(trans.source), color='black')
                if not trans.target in nodes:
                    nodes[trans.target] = Node(None, str(trans.target), color='black')
                wrapper.edges.append(Edge(nodes[trans.source],
                                          nodes[trans.target],
                                          label=str(trans.event)))
            wrapper.subobjects = nodes.values()
            ret.append(wrapper)
        return ret

    def __to_fsm(self, subtask):
        "Transforms the ICFG to an FSM"

        ret = FiniteStateMachine()

        def icfg_filter(edge):
            return edge.isA(self.get_edge_filter())

        def block_functor(in_edge, cur_abb):
            transitions = []
            # ICFG Entry transition
            if cur_abb == subtask.entry_abb:
                in_edge = None
                out_edge = cur_abb.get_outgoing_edges(self.get_edge_filter())[0]
                transitions.append(Transition(in_edge, out_edge, cur_abb.definite_after(self.get_edge_filter())))
            for in_edge in cur_abb.get_incoming_edges(self.get_edge_filter()):
                for out_edge in cur_abb.get_outgoing_edges(self.get_edge_filter()):
                    # Every Edge becomes a state, every state becomes an edge
                    transitions.append(Transition(in_edge, out_edge, out_edge.target))
            event = Event(cur_abb, transitions)
            ret.add_event(event)

        # With this depth-first search, we find all reachable
        # states. For every block, we add transitions from every
        # incoming edge, to every outgoing edge.
        dfs(block_functor, icfg_filter, [subtask.entry_abb])

        # The initial state is None, since the block_functor is called
        # with (None, entry_abb)
        ret.initial_state = None
        return ret

    def __epsilon_elimination(self, fsm):
        """The epsilon elimination pass makes every computation
           event/transition to an epsilon transition. With the
           standard FSM epslion elimination, we reduce the FSM
           size.
        """
        epsilon_sets = {}
        # Initialize the epsilon sets
        for state in fsm.states:
            epsilon_sets[state] = set([state])

        # Identify the epsilon sets with a fixpoint iteration The
        # epsilon set is the set of states, that can be reached from
        # one state by using only epsilon transitions. In our case,
        # all computation blocks are epsilon transitions.
        def is_epsilon_transition(transition):
            return trans.event.isA(S.computation)
        changed = True
        while changed:
            changed = False
            for trans in fsm.transitions:
                if is_epsilon_transition(trans):
                    epsilon_target = epsilon_sets[trans.target]
                    if not epsilon_sets[trans.source].issuperset(epsilon_target):
                        changed = True
                        epsilon_sets[trans.source] |= epsilon_target

        ret = fsm.copy()
        # Now that we have the epsilon set, we can construct a new fsm
        # from it.
        transitions = defaultdict(list)
        # Set of reachable states. Initial state is always reachable
        reachable = set([fsm.initial_state])
        for in_state in fsm.states:
            represents_edges = []
            for border_state in epsilon_sets[in_state]:
                # For every transition from a border state
                for trans in fsm.get_outgoing_transitions(border_state):
                    represents_edges.append(trans)
                    if is_epsilon_transition(trans):
                        continue # Epsilon Transitions are ignored
                    # Copy transition into the new finite state machine
                    transitions[trans.event] += [Transition(in_state, trans.target, trans.action)]
                    reachable.add(trans.target)
            # Now this state represents more than one CFG edge
            ret.state_mapping[in_state] = tuple(represents_edges)


        ret.events = []
        for event, trans in transitions.items():
            # Add only transitions which are reachable, after removing
            # the epsilon transitions
            trans = [x for x in trans if x.source in reachable]
            assert trans, "Transition set for an event should not be of zero-length"
            ret.add_event(Event(event, trans))
        return ret

    def do(self):
        for subtask in self.system_graph.subtasks:
            app_fsm = self.__to_fsm(subtask)
            app_fsm.rename(states=True)

            app_fsm = self.__epsilon_elimination(app_fsm)

            subtask.conf.fsm = app_fsm
            print()
            print(app_fsm)
