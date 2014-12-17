from generator.graph.common import *
from generator.graph.Analysis import *
from generator.graph import SymbolicSystemExecution, SavedStateTransition
from generator.tools import pairwise

from collections import namedtuple, defaultdict

Transition = namedtuple("Transition", ["source", "target", "action"])
Event     = namedtuple("Event", ["name", "transitions"])

class FiniteStateMachineBuilder(Analysis, GraphObject):
    """This pass does construct a finite state machine from the results of
       the SSE. As a result of this pass, we gathered an Event/Transition model

       self.fsm: A list of events. Each Event is an system-call ABB. The .name
                 field is the issuing system call ABB.
       self.representant_states: Within the Event/Transition model, numbers are used.
                 Each of these number has a representant system state in this dict.

    """
    pass_alias = "fsm"

    def __init__(self):
        Analysis.__init__(self)
        GraphObject.__init__(self, "FiniteStateMachineBuilder", root = True)

    def requires(self):
        # We require only the possible system states
        return ["SymbolicSystemExecution"]

    def get_edge_filter(self):
        return set([SavedStateTransition])

    ################################################################
    # For dumping the finite statemachine
    def graph_subobjects(self):
        if len(self.sse.states) > 500:
            return []
        return self.representant_states.keys()

    class SimpleEdge:
        def __init__(self, source, target, label='',
                     color = 'black'):
            self.source = source
            self.target = target
            self.label = label
            self.color = color

        def dump_as_dot(self):
            return "%s -> %s[minlen=3,label=\"%s\",color=%s];" %(
                self.source,
                self.target,
                self.label,
                self.color
            )

    def graph_edges(self):
        ret = []
        for P in self.fsm:
            for T in P.transitions:
                ret.append(self.SimpleEdge(source = T.source,
                                           target = T.target,
                                           label = str(P.name) + "\\n" + str(T.action)))
        return ret


    def find_equivalence_class(self, ret_sse_state, sse_states, syscall_states, syscall_ret_states):
        """This function finds the equivalence class for a given return state
        of a system call."""
        # Find the equvalence class for this syscall return state
        ret_state = id(ret_sse_state)
        ec = set([ret_state])
        changed = True
        while changed:
            changed = False
            new_ec = set(ec)
            # Add all successors, if it is not a syscall
            for member in (ec - syscall_states):
                for X in sse_states[member].get_outgoing_nodes(SavedStateTransition):
                    new_ec.add(id(X))
            # For all nodes that are not syscall return, go back
            for member in (ec - syscall_ret_states):
                for X in sse_states[member].get_incoming_nodes(SavedStateTransition):
                    new_ec.add(id(X))
            if new_ec != ec:
                ec = new_ec
                changed = True
        return ec

    def do(self):
        self.sse = self.system_graph.get_pass("SymbolicSystemExecution")

        # First we enumerate all possible system states, add them to
        # sets which are system call states and return states of
        # system call states.
        i = 0
        syscall_states  = set() # States with a syscall current_abb
        syscall_ret_states  = set() # States that have a syscall predecessor
        sse_states = {} # id(sse_state) => sse_state
        states = {} # id(SystemState) => Number
        for sse_state in self.sse.states:
            # Tramsform the SSE state object to its ID
            state = id(sse_state)
            sse_states[state] = sse_state # For back-mapping
            states[state] = i
            i += 1
            if not sse_state.current_abb.isA(S.computation):
                # A system call block!
                syscall_states.add(state)
                ret_state = id(sse_state.definite_after(SavedStateTransition))
                syscall_ret_states.add(ret_state)

        # For each system call ret block, we find those states that
        # are equivalent to the return state
        for ret_state in syscall_ret_states:
            # Get the actual SSE state
            ret_sse_state = sse_states[ret_state]
            ec = self.find_equivalence_class(ret_sse_state,
                                             sse_states,
                                             syscall_states,
                                             syscall_ret_states)
            # For the whole equivalence class, only one state number is used
            for member in ec:
                states[member] = states[ret_state]

        # Collect transitions per syscall ABB
        transitions_by_abb = defaultdict(list)
        transition_count = 0
        self.representant_states = {}
        for sse_state in self.sse.states:
            # Only system call sites
            if sse_state.current_abb.isA(S.computation):
                continue
            abb = sse_state.current_abb
            next_sse_state = sse_state.definite_after(SavedStateTransition)
            # Get the state numbers. This number is only a
            # representant for the whole equivalence class
            istate = states[id(sse_state)]
            ostate = states[id(next_sse_state)]
            action = next_sse_state.current_abb.subtask
            transition = Transition(source = istate, target = ostate, action = action)
            transition_count += 1
            transitions_by_abb[abb].append(transition)
            self.representant_states[istate] = sse_state


        # Construct the Event/Transition Model
        self.fsm = []
        for abb, transitions in transitions_by_abb.items():
            event = Event(name = abb, transitions = transitions)
            self.fsm.append(event)

        logging.info("  FSM: %d state; %d transisitons" ,
                     len(set(states.values())),
                     transition_count)
