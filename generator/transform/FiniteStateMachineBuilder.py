from generator.analysis.common import *
from generator.analysis import Analysis, SavedStateTransition, S
from generator.tools import pairwise
from collections import namedtuple, defaultdict
from datastructures.sage_finite_state_machine import Transducer, full_group_by, Automaton
from datastructures.fsm import FiniteStateMachine, Transition, Event

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
        fsm = self.fsm
        #fsm.rename(events = lambda x: fsm.event_mapping[x],
        #           actions = lambda x: fsm.action_mapping[x])


        def subtask(state):
            if state in fsm.state_mapping:
                if fsm.state_mapping[state].current_subtask:
                    return self.interrupted_subtask(fsm.state_mapping[state]).name
            return "XXX"
        for P in fsm.events:
            for T in P.transitions:
                ret.append(self.SimpleEdge(source = "%s_%s" % (subtask(T.source), T.source),
                                           target = "%s_%s" % (subtask(T.target), T.target),
                                           label = str(P.name) + "\\n| " + str(T.action)))
        return ret


    def find_equivalence_class(self, state, sse_states, syscall_states):
        """This function finds the equivalence class for a given system state."""
        #def path(x):
        #    if type(x) == set:
        #        return [path(y) for y in x]
        #    return sse_states[x].current_abb

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
        return ec

    def interrupted_subtask(self, state, visited = None):
        """Returns the currently running subtask, if the state is a non-ISR
           state. If it is a ISR state, the function returns the interrupted task.
        """
        if visited is None:
            visited = set()
        if not state.current_subtask.conf.is_isr:
            return state.current_subtask
        else:
            for pred in state.get_incoming_nodes(SavedStateTransition):
                # Already visited
                if pred in visited:
                    continue
                visited.add(pred)
                subtask = self.interrupted_subtask(pred, visited)
                # We found an non-isr predecessor?
                if subtask:
                    return subtask
        return None

    def do_from_app_fsm(self):
        # Construct the Event/Transition Model
        self.fsm = FiniteStateMachine()

        events = defaultdict(list)
        for start_state in self.sse.states:
            for next_state, label in start_state.get_outgoing_edges(SavedStateTransition):
                # As action for the state, we use the interrupted subtask
                if label.isA(S.CheckIRQ):
                    action = self.interrupted_subtask(start_state)
                else:
                    action = self.interrupted_subtask(next_state)

                events[label] += [Transition(start_state, next_state, action)]
        for abb, transitions in events.items():
            event = Event(name = abb, transitions = transitions)
            if abb.isA(S.StartOS):
                assert len(transitions) == 1
                self.fsm.initial_state = transitions[0].source

            self.fsm.add_event(event)

        self.fsm.rename(states = True)
        self.__minimize()

    def do(self):
        self.sse = self.system_graph.get_pass("SymbolicSystemExecution")
        if self.sse.use_app_fsm:
            self.do_from_app_fsm()
            return

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
            # Was the state already remapped? Save the work and skip it.
            if state in remapped:
                continue
            # Get the actual SSE state
            ec = self.find_equivalence_class(state, sse_states, syscall_states)
            # For the whole equivalence class, only one state number is used
            for member in ec:
                states[member] = states[state]

            # Mark the whole equivalence class as `already remapped'
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
            action = self.interrupted_subtask(next_sse_state)
            transition = Transition(source = istate, target = ostate, action = action)
            transition_count += 1
            transitions_by_abb[abb].append(transition)
            # If we chose the kickoff state (with current running
            # subtask already set to the interrupt handler, choose
            # another one)
            if sse_state.current_abb.isA(S.kickoff) \
               and sse_state.current_subtask.conf.is_isr:
                sse_state = sse_state.definite_before(SavedStateTransition)
            map_to_SystemState[istate] = sse_state

        # Construct the Event/Transition Model
        self.fsm = FiniteStateMachine()
        for abb, transitions in transitions_by_abb.items():
            if abb.isA(S.StartOS):
                assert len(transitions) == 1, transitions
                self.fsm.initial_state = transitions[0].source
            event = Event(name = abb, transitions = transitions)
            self.fsm.add_event(event)
        self.fsm.state_mapping = map_to_SystemState

        self.__minimize()

    def __minimize(self):
        def count(iter):
            return sum(1 for _ in iter)

        logging.info("  FSM: %d states; %d transisitons" ,
                     len(self.fsm.states),
                     count(self.fsm.transitions))

        self.fsm_unminimized = self.fsm
        self.fsm = FiniteStateMachineMinimizer.minimize(self.fsm)
        logging.info("  FSM(minimized): %d states; %d transisitons" ,
                     len(self.fsm.states),
                     count(self.fsm.transitions))

class FiniteStateMachineMinimizer:
    @staticmethod
    def __equivalence_classes(fsm):
        """Find equivalence classes for the sage fsm. Two states are in the
        same equivalence class, if they produce the same dispatch
        sequence.

        We start with the 0-equivalence:
          Two states are equal if they have the same running subtask (word_out == current_subtask)

        Furthermore, we split the equivalence classes, according to their:
          `What are possible next equivalence classes'-key

        This was adapted from `sage_finite_state_machine.equivalence_classes`

        """
        # initialize with 0-equivalence
        classes_previous = []
        # word_out: interupted task (is never ISR)
        # color: actual running task (might be ISR)
        key_0 = lambda state: (state.word_out, state.color)
        states_grouped = full_group_by(fsm.states(), key=key_0)
        classes_current = [equivalence_class for
                           (key,equivalence_class) in states_grouped]


        while len(classes_current) != len(classes_previous):
            class_of = {}
            followup_classes_of = {}

            classes_previous = classes_current
            classes_current = []

            # Generate a mapping from state -> current class
            for k in range(len(classes_previous)):
                for state in classes_previous[k]:
                    class_of[state] = k

            # Here we calculate to what classes a state can lead. For
            # this we follow all transitions until the current
            # equivalence class is left.
            for state in fsm.states():
                visited = set()
                followup_class = set()
                W = stack([state])
                while W:
                    # Get one from the working stack
                    S = W.pop()
                    if S in visited:
                        continue
                    visited.add(S)

                    # Add Current class to followup classes
                    followup_class.add(class_of[S])

                    # Skip if we've left the region
                    if class_of[S] != class_of[state]:
                        continue

                    # Shortcut: We have already computed the border
                    # for a state, reuse its followup classes border
                    if S in followup_classes_of:
                        followup_class.update(followup_classes_of[S])
                    else:
                        # Otherwise: follow all transitions
                        for transition in S.transitions:
                            W.push(transition.to_state)

                # We're only interested in classes this class can jump to
                followup_class.discard(class_of[state])
                # We use list(sorted(...)) here, since full_group_by
                # relies on equal string representations.
                followup_classes_of[state] = list(sorted(followup_class))
            key_current = lambda state: followup_classes_of[state]

            for class_previous in classes_previous:
                states_grouped = full_group_by(class_previous, key = key_current)
                classes_current.extend(equivalence_class
                                       for key, equivalence_class in states_grouped)

        return classes_current

    @staticmethod
    def __quotient(fsm, classes):
        """This function creates a new FSM from a sage fsm and a list of equivalence classes."""
        new = fsm.empty_copy()
        state_mapping = {}

        # Create new states and build state_mapping
        for class_ in classes:
            new_label = tuple(class_)
            new_state = class_[0].relabeled(new_label)
            new.add_state(new_state)
            for state in class_:
                state_mapping[state] = new_state

        # Merge the classes and add all transitions. Every transition
        # is added only once, duplicated onces are removed from the
        # graph.
        for class_ in classes:
            new_transitions = set()
            new_state = state_mapping[class_[0]]
            for c in class_:
                for transition in fsm.iter_transitions(c):
                    new_transition = (new_state,
                                      state_mapping[transition.to_state],
                                      transition.word_in[0],
                                      transition.word_out[0])
                    new_transitions.add(new_transition)

            for t in new_transitions:
                new.add_transition(
                        from_state = t[0],
                        to_state = t[1],
                        word_in = [t[2]],
                        word_out = [t[3]])
        return new, state_mapping

    @staticmethod
    def minimize(old_fsm):
        """Minimize the finite state automata using the an adapted FSM
        minimization algorithm.
        """
        old_fsm.rename(events = True, actions = True)
        # For Debugging: self.rename(events = str, actions = str)
        sage = old_fsm.to_sage_fsm()

        # We use our own simpliciation algorithm here
        ec = FiniteStateMachineMinimizer.__equivalence_classes(sage)
        new_fsm, state_mapping = FiniteStateMachineMinimizer.__quotient(sage, ec)

        ret = FiniteStateMachine.from_sage_fsm(old_fsm, new_fsm)
        # The resulting fsm MUST be deterministic.
        if not new_fsm.is_deterministic():
            # Get back the objects
            ret.rename(events = lambda x: ret.event_mapping[x],
                       actions = lambda x: ret.action_mapping[x])
            for event in ret.events:
                in_states = {}
                for t in event.transitions:
                    if t.source in in_states:
                        print(event.name.path())
                        print(in_states[t.source])
                        print(t)
                        print(ret.state_mapping[t.source])
                        print(ret.state_mapping[t.target])
                        print(ret.state_mapping[in_states[t.source].target])

                    in_states[t.source] = t

            assert False, "FSM is not deterministic"


        # Get back the objects
        ret.rename(events = lambda x: ret.event_mapping[x],
                   states = True, # Renumber !
                   actions = lambda x: ret.action_mapping[x])

        # Remove Events that have only transitions which are self loops
        to_del = []
        for event in ret.events:
            if all(t.source == t.target for t in event.transitions):
                to_del.append(event)
        logging.info("  FSM(minimized): %d self loop events removed", len(to_del))
        for event in to_del:
            ret.events.remove(event)

        return ret
