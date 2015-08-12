from .common import *
from .Analysis import Analysis
from .AtomicBasicBlock import E, S, AtomicBasicBlock
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
            for trans in subtask.fsm.transitions:
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
            # Here we do the following. Each Edge becomes a state in our finite state machine.
            # So from
            #   ---[in_edge]--> [in_edge.target] --[out_edge]-->
            # we make
            #   [in_edge] --[in_edge.target == ABB]--> [out_edge]
            # Entry and exit nodes are handleded differently
            if cur_abb == subtask.entry_abb:
                in_edge = None
                out_edge = cur_abb.get_outgoing_edges(self.get_edge_filter())[0]
                transitions.append(Transition(in_edge, out_edge, cur_abb.definite_after(self.get_edge_filter())))
            for in_edge in cur_abb.get_incoming_edges(self.get_edge_filter()):
                for out_edge in cur_abb.get_outgoing_edges(self.get_edge_filter()):
                    # Every Edge becomes a state, every state becomes an edge
                    transitions.append(Transition(in_edge, out_edge, out_edge.target))
                # Exit nodes are different
                if cur_abb == subtask.exit_abb:
                    out_edge = None
                    # Every Edge becomes a state, every state becomes an edge
                    transitions.append(Transition(in_edge, -1, None))

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

    def epsilon_elimination(self, fsm):
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
        def is_epsilon_transition(trans):
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

            app_fsm = self.epsilon_elimination(app_fsm)
            subtask.fsm = app_fsm
            subtask.ApplicationFSMIterator = ApplicationFSMIterator.create

        # Rewrite AlarmSubtask
        if self.system_graph.AlarmHandlerSubtask:
            fsm = self.system_graph.AlarmHandlerSubtask.fsm
            for E in fsm.events:
                if not E.name.isA([S.CheckAlarm, S.iret]):
                    continue
                old_states = set([T.source for T in E.transitions])
                new_state = [T.source for T in E.transitions][0]
                def renamer(state):
                    if state in old_states:
                        return new_state
                    return state
                fsm.rename(states = renamer)
                tgt = {(T.source, T.target): T for T in E.transitions}
                E.transitions = tgt.values()

        for trans in self.system_graph.idle_subtask.fsm.transitions:
            if trans.event.isA(S.Idle):
                trans.target = trans.source

fsm_iter_cache = {}

class ApplicationFSMIterator:
    """The Application FSM Iterator is a wrapper for APP-FSM states to be
       used by the symbolic system execution. It has a similar
       interface to the AtomicBasicBlock.
    """
    @staticmethod
    def create(subtask, state):
        if not (subtask, state) in fsm_iter_cache:
            it = ApplicationFSMIterator()
            it.__create__(subtask, state)
            fsm_iter_cache[(subtask, state)] = it
        return fsm_iter_cache[(subtask, state)]

    def __init__(self):
        pass

    def __create__(self, subtask, state):
        self.subtask = subtask
        self.__state   = state
        self.dynamic_priority = self.__consistent(
            self.__originating_blocks(),
            lambda x: x.dynamic_priority
            )
        computations = self.__originating_blocks(True)
        if computations:
            self.interrupt_block_all = self.__consistent(
                computations,
                lambda x: x.interrupt_block_all
            )
            self.interrupt_block_os = self.__consistent(
                computations,
                lambda x: x.interrupt_block_os
            )

        self.possible_systemcalls = set()
        for trans in self.subtask.fsm.get_outgoing_transitions(self.__state):
            self.possible_systemcalls.add(trans.event)

        if self.__state != self.subtask.fsm.initial_state \
           and self.subtask.is_user_thread():
            # Besides the initial state, we give back an additional
            # computation block as possible system-call.
            edges = self.subtask.fsm.state_mapping[self.__state]
            computations = [x.event for x in edges if x.event.isA(S.computation)]
            abb  = AtomicBasicBlock(self.subtask.system_graph)
            abb.make_it_a_syscall(S.CheckIRQ, computations)
            self.possible_systemcalls.add(abb)

        self.possible_systemcalls = list(self.possible_systemcalls)

    

    def __originating_blocks(self, only_computation = False):
        blocks = [x.event for x in self.subtask.fsm.state_mapping[self.__state]]
        if only_computation:
            blocks = [x for x in blocks if x.isA(S.computation)]
        return blocks

    def __consistent(self, seq, mapper=lambda x:x):
        ret  = [mapper(x) for x in seq]
        assert len(ret) > 0, "To have a consistent value, at least one value must be present"
        assert all([ret[0] == ret[i] for i in range(1, len(ret))]), "Inconsistent %s" % seq
        return ret[0]

    def __repr__(self):
        try:
            return "<It %s:%s prio:%d>" %(self.subtask.name, self.__state, self.dynamic_priority)
        except:
            return "<It %s:%s prio>" %(self.subtask.name, self.__state)

    def isA(self, cls):
        return self.__consistent(
            self.__originating_blocks(),
            lambda x: x.isA(cls)
            )

    def path(self):
        return "%s/%d" % (self.subtask, self.__state)

    @property
    def abb_id(self):
        return self.__state


    def get_blocks(self):
        return self.__originating_blocks()

    def next_iterators(self, event):
        ret = []
        for trans in self.subtask.fsm.get_outgoing_transitions(self.__state):
            if trans.event == event:
                ret.append(self.create(self.subtask, trans.target))
        # No computation block should ever arrive here as event
        assert not event.isA(S.computation)
        return ret

