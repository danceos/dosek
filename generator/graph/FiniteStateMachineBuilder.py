from generator.graph.common import *
from generator.graph.Analysis import *
from generator.graph import SymbolicSystemExecution, SavedStateTransition
from generator.tools import pairwise
from types import SimpleNamespace
from collections import namedtuple, defaultdict

Transition = namedtuple("Transition", ["source", "target", "action"])

class Transition:
    def __init__(self, source, target, action):
        self.event = None
        self.source = source
        self.target = target
        self.action = action

        self.impl = SimpleNamespace()

    def __repr__(self):
        return "<Transition(%s) %d -> %d: %s>" %(self.event.name, self.source, self.target, self.action)


class Event:
    def __init__(self, name, transitions):
        self.name = name
        self.transitions = transitions
        for t in transitions:
            t.event = self

        self.impl = SimpleNamespace()

    def __repr__(self):
        return "<Event(%s) %d transitions>" %(self.name, len(self.transitions))

class FiniteStateMachine:
    def __init__(self):
        self.initial_state = None

        # Set of Integers
        self.states = set()

        # List of Event
        self.events = []

        # Mapping to SystemState
        self.mapping = {}

        self.impl = SimpleNamespace()


    def add_event(self, event):
        self.events.append(event)
        for transition in event.transitions:
            self.states.add(transition.source)
            self.states.add(transition.target)

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
        return self.fsm.states

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
        for P in self.fsm.events:
            for T in P.transitions:
                ret.append(self.SimpleEdge(source = T.source,
                                           target = T.target,
                                           label = str(P.name) + "\\n" + str(T.action)))
        return ret


    def find_equivalence_class(self, state, sse_states, syscall_states):
        """This function finds the equivalence class for a given system state."""
        #def path(x):
        #    if type(x) == set:
        #        return [path(y) for y in x]
        #    return sse_states[x].current_abb
        # print("Find EC for ", path(state))
        ec = set([state])
        changed = True
        while changed:
            # print(path(ec))
            changed = False
            new_ec = set(ec)
            # Add all successors, if it is not a syscall
            for member in ec:
                for X in sse_states[member].get_incoming_nodes(SavedStateTransition):
                    if not id(X) in syscall_states:
                        new_ec.add(id(X))
            # print(path(new_ec))
            # For all nodes that are not syscall return, go back
            for member in (ec - syscall_states):
                for X in sse_states[member].get_outgoing_nodes(SavedStateTransition):
                    new_ec.add(id(X))
            if new_ec != ec:
                ec = new_ec
                changed = True
        #print("Done: ", path(ec))
        #print()
        return ec

    def do(self):
        self.sse = self.system_graph.get_pass("SymbolicSystemExecution")

        def isSyscall(state):
            return not state.current_abb.isA([S.computation, S.CheckAlarm])

        # First we enumerate all possible system states, add them to
        # sets which are system call states and return states of
        # system call states.
        i = 1
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
            # A system call block!
            if isSyscall(sse_state):
                syscall_states.add(state)

        # For each system call ret block, we find those states that
        # are equivalent to the return state
        remapped = set()
        for state in syscall_states:
            if state in remapped:
                continue
            # Get the actual SSE state
            ec = self.find_equivalence_class(state, sse_states, syscall_states)
            # For the whole equivalence class, only one state number is used
            for member in ec:
                states[member] = states[state]

            remapped.update(ec)

        # Collect transitions per syscall ABB
        transitions_by_abb = defaultdict(list)
        transition_count = 0
        map_to_SystemState = {}
        for sse_state in self.sse.states:
            # Only system call sites
            if not isSyscall(sse_state):
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
            map_to_SystemState[istate] = sse_state

        # Construct the Event/Transition Model
        self.states = set()
        self.fsm = FiniteStateMachine()
        for abb, transitions in transitions_by_abb.items():
            if abb.isA(S.StartOS):
                assert len(transitions) == 1, transitions
                self.fsm.initial_state = transitions[0].source
            event = Event(name = abb, transitions = transitions)
            self.fsm.add_event(event)
        self.fsm.mapping = map_to_SystemState
        #for x, s in sorted(self.fsm.mapping.items(), key = lambda x: x[0]):
        #    print (x, s)

        logging.info("  FSM: %d state; %d transisitons" ,
                     len(set(states.values())),
                     transition_count)
