from generator.analysis.common import *
from generator.analysis import Analysis, SavedStateTransition, S, E
from generator.tools import pairwise
from tools import SimpleNamespace
from collections import namedtuple, defaultdict
from .sage_finite_state_machine import Transducer, full_group_by, Automaton

class Transition:
    def __init__(self, source, target, action):
        self._event = None
        self.source = source
        self.target = target
        self.action = action

        self.impl = SimpleNamespace()

    @property
    def event(self):
        if self._event:
            return self._event.name

    def __repr__(self):
        return "<Transition(%s) %s -> %s: %s>" %(self.event, self.source, self.target, self.action)


class Event:
    def __init__(self, name, transitions):
        self.name = name
        self.transitions = transitions
        for t in transitions:
            t._event = self

        self.impl = SimpleNamespace()

    def add_transition(self, transition):
        transition._event = self
        self.transitions.append(transition)

    def __repr__(self):
        return "<Event(%s) %d transitions>" %(self.name, len(self.transitions))

class FiniteStateMachine:
    def __init__(self):
        self.initial_state = None

        # List of Event
        self.events = []

        # Indirection tables
        self.state_mapping  = {}
        self.event_mapping  = {}
        self.action_mapping = {}

        self.impl = SimpleNamespace()

    @property
    def states(self):
        return self.state_mapping.keys()

    @property
    def transitions(self):
        for ev in self.events:
            for t in ev.transitions:
                yield t

    @property
    def actions(self):
        return self.action_mapping.keys()

    def copy(self):
        ret = FiniteStateMachine()
        ret.initial_state = self.initial_state

        #Copy Mappings
        ret.action_mapping = self.action_mapping.copy()
        ret.event_mapping = self.event_mapping.copy()
        ret.state_mapping = self.state_mapping.copy()

        # Generate new transitions and events
        for event in self.events:
            n_event = Event(event.name, [])
            for t in event.transitions:
                n_t = Transition(t.source, t.target, t.action)
                n_event.add_transition(n_t)
            ret.add_event(n_event)
        return ret

    def add_event(self, event):
        self.events.append(event)
        if not event.name in self.event_mapping:
            self.event_mapping[event.name] = event.name
        for transition in event.transitions:
            if not transition.source in self.state_mapping:
                self.state_mapping[transition.source] = transition.source
            if not transition.target in self.state_mapping:
                self.state_mapping[transition.target] = transition.target
            if not transition.action in self.action_mapping:
                self.action_mapping[transition.action] = transition.action

    def __rename_events(self, from_to_map):
        new_mapping = {}
        for event in self.events:
            new = from_to_map[event.name]
            new_mapping[new] = self.event_mapping[event.name]
            event.name = new
        self.event_mapping = new_mapping

    def __rename_actions(self, from_to_map):
        new_mapping = {}
        for t in self.transitions:
            new = from_to_map[t.action]
            new_mapping[new] = self.action_mapping[t.action]
            t.action = new
        self.action_mapping = new_mapping

    def __rename_states(self, from_to_map):
        self.initial_state = from_to_map[self.initial_state]
        new_mapping = {}
        for t in self.transitions:
            new = from_to_map[t.source]
            new_mapping[new] = self.state_mapping[t.source]
            t.source = new

            new = from_to_map[t.target]
            new_mapping[new] = self.state_mapping[t.target]
            t.target = new
        self.state_mapping = new_mapping

    def rename(self, events = None, states = None, actions = None):
        class count_rename:
            def __init__(self):
                self.__i = 0
            def __call__(self, _):
                x = self.__i
                self.__i += 1
                return x

        if type(events) == bool and events:
            events = count_rename()
        if type(states) == bool and states:
            states = count_rename()
        if type(actions) == bool and actions:
            actions = count_rename()

        if events:
            from_to_map = {}
            for event in self.events:
                from_to_map[event.name] = events(event.name)
            self.__rename_events(from_to_map)

        if states:
            from_to_map = {}
            for t in self.transitions:
                if not t.source in from_to_map:
                    from_to_map[t.source] = states(t.source)
                if not t.target in from_to_map:
                    from_to_map[t.target] = states(t.target)
            self.__rename_states(from_to_map)

        if actions:
            from_to_map = {}
            for t in self.transitions:
                if not t.action in from_to_map:
                    from_to_map[t.action] = actions(t.action)
            self.__rename_actions(from_to_map)



    def to_sage_fsm(self):
        actions = []
        # What is task at that point
        output_map = {}
        for t in self.transitions:
            actions.append((t.source, t.target, t.event, t.action))
            output_map[t.target] = t.action
        m = Transducer(actions, initial_states = [self.initial_state])

        for state in m.states():
            if state.label() in output_map:
                state.word_out = [output_map[state.label()]]
        return m

    @staticmethod
    def from_sage_fsm(old_fsm, sage):
        events = {}
        for transition in sage.transitions():
            abb = transition.word_in[0]
            if not abb in events:
                events[abb] = Event(abb, [])
            event = events[abb]

            from_state = transition.from_state.label()[0].label()
            to_state = transition.to_state.label()[0].label()
            action = transition.word_out[0]
            event.add_transition(Transition(from_state, to_state, action))

        # Assemble a finite state machine
        ret = FiniteStateMachine()
        for event in events.values():
            ret.add_event(event)
        ret.initial_state = sage.initial_states()[0].label()[0].label()
        ret.action_mapping = old_fsm.action_mapping.copy()
        ret.event_mapping = old_fsm.event_mapping.copy()
        ret.state_mapping = old_fsm.state_mapping.copy()

        return ret


    def __str__(self):
        ret = []
        max_lengths = [0,0,0,0]
        table = []
        for t in self.transitions:
            row = [t.event, t.source, t.target, t.action]
            table.append(row)
            for i, e in enumerate(row):
                max_lengths[i] = max(max_lengths[i], len(str(e)))
        for row in table:
            # Don't ask
            line = "{0!s:<{4}}\t{1!s:<{5}}\t{2!s:<{6}}\t{3!s:<{7}}".format(*(row + max_lengths))
            ret.append(line)
        return "\n".join(ret)



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
            action = next_sse_state.current_abb.subtask
            transition = Transition(source = istate, target = ostate, action = action)
            transition_count += 1
            transitions_by_abb[abb].append(transition)
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
        key_0 = lambda state: state.word_out
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
        return new

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
        new_fsm = FiniteStateMachineMinimizer.__quotient(sage, ec)

        # The resulting fsm MUST be deterministic.
        assert new_fsm.is_deterministic()

        ret = FiniteStateMachine.from_sage_fsm(old_fsm, new_fsm)

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
