from tools import SimpleNamespace
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

    def get_outgoing_transitions(self, state):
        for trans in self.transitions:
            if trans.source == state:
                yield trans

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
                # We use the actual dispatched subtask here as color
                # of the state. Afterwards, the color for ISR states
                # the output_word is the dispatched real task. The
                # color is set to the subtask_id of the ISR Task.
                subtask = self.state_mapping[state.label()].current_subtask
                state.color = subtask.subtask_id
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

    def dump_as_dot(self):
        ret = "digraph G {"
        for t in self.transitions:
            ret += '\t%d -> %d [label="%s\n%s"];\n'%(
                t.source, t.target, t.event, t.action
            )
        ret += "}"
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
