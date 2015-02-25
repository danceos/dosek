from generator.tools import stack, unwrap_seq, panic
from generator.graph.AtomicBasicBlock import E, S
from generator.graph.Sporadic import Alarm
from generator.graph.Subtask import Subtask
from generator.graph.Event import Event
from generator.graph.common import Node, Edge, EdgeType, NodeType

class SystemState(Node):
    """Normal system states capture the state at a specific point in the
       application. The normal system state may be fuzzy or imprecise. Some
       fields are unkown"""
    READY = 1
    SUSPENDED = 2
    WAITING = 4

    # Static field that counts the system states that were created
    copy_count = 0

    def __init__(self, system_graph):
        Node.__init__(self, Edge, "", color="green")
        self.system_graph = system_graph
        self.frozen = False

        size = len(self.system_graph.subtasks)

        self.states = [0] * size
        self.continuations = [None] * size
        self.events_cleared = [0] * size
        self.events_set = [0] * size
        self.call_stack = [None] * size

        for i  in range(0, size):
            self.continuations[i] = set()

        self.current_abb = None
        self.__hash = None

    def new(self):
        return SystemState(self.system_graph)

    def copy(self):
        # Increase the copy counter
        SystemState.copy_count += 1

        state = self.new()
        state.current_abb = self.current_abb
        state.states = list(self.states)
        for subtask in self.get_unordered_subtasks():
            state.continuations[subtask.subtask_id] = set(self.continuations[subtask.subtask_id])

            # Only used by SymbolicSystemExecution
            if not self.call_stack[subtask.subtask_id] is None:
                state.call_stack[subtask.subtask_id] = stack(self.call_stack[subtask.subtask_id])
        return state

    def copy_if_needed(self, multiple=None):
        if self.frozen:
            if multiple != None:
                return [self.copy() for x in range(0, multiple)]
            else:
                return self.copy()
        if multiple != None:
            return [self] + [self.copy() for x in range(1, multiple)]
        else:
            return self

    def get_subtasks(self):
        """Sorted by priority"""
        return sorted(self.system_graph.subtasks,
                      key=lambda x: x.static_priority, reverse = True)

    def get_unordered_subtasks(self):
        return self.system_graph.subtasks

    def get_task_states(self, subtask):
        return self.states[subtask]

    def set_suspended(self, subtask):
        assert not self.frozen
        self.states[subtask.subtask_id] = self.SUSPENDED

    def set_ready(self, subtask):
        assert not self.frozen
        self.states[subtask.subtask_id] = self.READY

    def set_waiting(self, subtask):
        assert not self.frozen
        self.states[subtask.subtask_id] = self.WAITING

    def set_unsure(self, subtask):
        assert not self.frozen
        self.states[subtask.subtask_id] = self.READY | self.SUSPENDED

    ## Ready state accessors

    def is_surely_suspended(self, subtask):
        return self.states[subtask.subtask_id] == self.SUSPENDED

    def is_surely_ready(self, subtask):
        return self.states[subtask.subtask_id] == self.READY

    def is_maybe_ready(self, subtask):
        return self.READY & self.states[subtask.subtask_id]

    def is_maybe_suspended(self, subtask):
        return self.SUSPENDED & self.states[subtask.subtask_id]

    def is_unsure_ready_state(self, subtask):
        return bin(self.states[subtask.subtask_id]).count("1") > 1

    # Events
    def clear_events(self, subtask, event_list):
        """Only a dummy implementation, called by the system state flow
           analysis, which does not support events."""
        pass

    def get_events(self, subtask):
        """Returns two bitmasks: (Event is cleared, Event is set)"""
        return (self.events_cleared[subtask.subtask_id],
                self.events_set[subtask.subtask_id])

    def is_event_set(self, subtask, event):
        return (self.events_set[subtask.subtask_id] & event.event_mask) != 0

    def is_event_cleared(self, subtask, event):
        return (self.events_cleared[subtask.subtask_id] & event.event_mask) != 0

    ## Continuations
    def get_continuations(self, subtask):
        if type(subtask) == int:
            return self.continuations[subtask]
        return self.continuations[subtask.subtask_id]

    def set_continuation(self, subtask, abb):
        assert not self.frozen
        self.continuations[subtask.subtask_id] = set([abb])

    def set_continuations(self, subtask, abbs):
        assert not self.frozen
        self.continuations[subtask.subtask_id] = set(abbs)

    def remove_continuation(self, subtask, abb):
        assert not self.frozen
        assert abb in self.continuations[subtask.subtask_id]
        self.continuations[subtask.subtask_id].discard(abb)

    def add_continuation(self, subtask, abb):
        assert not self.frozen
        self.continuations[subtask.subtask_id].add(abb)

    def get_call_stack(self, subtask):
        raise NotImplemented("Normal System states have no call stack")

    ## Continuation accesors
    def was_surely_not_kickoffed(self, subtask):
        """Returns whether a task can only continue in the kickoff block."""
        assert subtask.entry_abb.isA(S.kickoff)
        assert len(self.get_continuations(subtask)) > 0, str(self)
        is_entry = [subtask.entry_abb == x for x in self.get_continuations(subtask)]
        return all(is_entry)

    def was_surely_kickoffed(self, subtask):
        """Returns whether a task can only be continued."""
        assert subtask.entry_abb.isA(S.kickoff)
        assert len(self.get_continuations(subtask)) > 0, str(self)
        is_not_entry = [subtask.entry_abb != x for x in self.get_continuations(subtask)]
        return all(is_not_entry)

    # Fuzzyness indicator
    def precision(self):
        """Returns an number in [0.0, 1.0], that indicates the fuzzyness of
        the system state. Rules for the generation are:
        - task states and continuations are equaly weighted
          - All tasks know adds a score of 0.5
          - The more continuations there for a state, the less precise it is. 
            The most precise it is when there is one continuation per subtask"""

        subtask_score = 0
        continuation_score = 0
        count = float(len(list(self.get_unordered_subtasks())))

        # Get the system relevant system abbs
        is_relevant = self.system_graph.passes["AddFunctionCalls"].is_relevant_function
        abbs = [x for x in self.system_graph.abbs if is_relevant(x.function)]

        for subtask in self.get_unordered_subtasks():
            if not self.is_unsure_ready_state(subtask):
                subtask_score += 1
            # If there is no continuation, we know that we have the
            # currently running task at our hands.
            subtask_abbs = len([x for x in abbs if x.function.subtask == subtask])

            conts = len(self.continuations[subtask.subtask_id])
            if conts == 0:
                continuation_score += 1.0
            else:
                # Calculate a score that gets lower when there are more continuations
                continuation_score += (subtask_abbs - conts) / (subtask_abbs - 1)

        subtask_score = subtask_score / count
        continuation_score = continuation_score / count
        ret = (subtask_score + continuation_score) / 2.0
        assert (ret >= 0.0 and ret <= 1.0)
        return ret

    @property
    def current_subtask(self):
        if not self.current_abb:
            return None
        return self.current_abb.function.subtask

    def freeze(self):
        self.frozen = True

    def merge_with(self, other, return_changed = True):
        """Returns a newly created state that is the result of the merge of
           self and the other state"""
        assert not self.frozen
        assert self.current_abb == None or self.current_abb == other.current_abb,\
            "%s != %s" %(self.current_abb.path(), other.current_abb.path())
        self.current_abb = other.current_abb
        changed = False

        for subtask in self.system_graph.subtasks:
            subtask_id = subtask.subtask_id

            old_state = self.states[subtask_id]
            continuations_count = len(self.continuations[subtask_id])

            self.states[subtask_id] |= other.states[subtask_id]
            self.continuations[subtask_id] |= other.get_continuations(subtask_id)
            # Check whether one set has changed
            if return_changed and \
               ( self.states[subtask_id] != old_state \
                 or len(self.continuations[subtask_id]) != continuations_count):
                changed = True

            # We cannot merge call stacks!
            self.call_stack[subtask_id] = None

            # Merge Event masks
            # FIXME: Events do not influence the changed flag correctly
            (events_cleared, events_set) = other.get_events(subtask)
            self.events_cleared[subtask_id] |= events_cleared
            self.events_set[subtask_id] |= events_set


        return changed

    @staticmethod
    def merge_many(system, states):
        state = SystemState(system)
        for x in states:
            state.merge_with(x)
        return state

    def format_state(self, state):
        ret = []
        if state & self.READY:
            ret.append("RDY")
        if state & self.SUSPENDED:
            ret.append("SPD")
        if state & self.WAITING:
            ret.append("WAI")

        return "|".join(ret)

    def format_events(self, subtask):
        ret = []
        for event in subtask.events:
            SET = self.is_event_set(subtask, event)
            CLEARED = self.is_event_cleared(subtask, event)
            if SET and CLEARED:
                ret.append("%s:*" % event.conf.name)
            elif SET:
                ret.append("%s:1" % event.conf.name)
            else:
                assert CLEARED
                ret.append("%s:0" % event.conf.name)
        return " ".join(ret)

    def __repr__(self):
        if self.current_abb:
            ret = "<SystemState: %s>\n" %(self.current_abb.path())
        else:
            ret = "<SystemState: -->\n"

        for subtask in self.get_subtasks():
            ret += "  %02x%02x %s: %s in %s [%s]\n" %(
                id(self.states[subtask.subtask_id]) % 256,
                id(self.continuations[subtask.subtask_id]) % 256,
                subtask, self.format_state(self.states[subtask.subtask_id]),
                self.continuations[subtask.subtask_id],
                self.format_events(subtask))
        ret += "</SystemState>\n"
        return ret

    def __hash__(self):
        assert self.frozen, "Only frozen states can be hashed"
        if self.__hash != None:
            return self.__hash
        ret = 0
        # XOR does comute!
        ret ^= hash(self.current_abb)
        for state in self.states:
            ret ^= hash(state)
        for conts in self.continuations:
            for cont in conts:
                ret ^= hash(cont)
        for call_stack in self.call_stack:
            if not call_stack:
                continue
            for go_back in call_stack:
                ret ^= hash(go_back)
        self.__hash = ret
        return ret

    def __eq__(self, other):
        if id(self) == id(other):
            return True
        if not isinstance(other, SystemState):
            return False
        # The Currently Running Task has to be equal
        if not self.current_abb == other.current_abb:
            return False

        for subtask_id in range(0, len(self.states)):
            # The subtask states have to equal
            if not self.states[subtask_id] == other.states[subtask_id]:
                return False
            # The possible continuations have to be equal
            if not self.continuations[subtask_id] == other.continuations[subtask_id]:
                return False
            # The call stack has to be equal
            if not self.call_stack[subtask_id] == other.call_stack[subtask_id]:
                return False

        return True

    def is_definite(self):
        for subtask in list(self.states.keys()):
            if self.is_unsure_ready_state(subtask):
                return False
            if len(self.continuations[subtask]) > 1:
                return False
        return True

    def dump(self):
        ret = {"ABB": str(self.current_abb)}
        for subtask in self.get_unordered_subtasks():
            state = self.states[subtask.subtask_id]
            ret[subtask.name] = self.format_state(state)
            conts = self.get_continuations(subtask)
            assert len(conts) <= 1
            if len(conts) == 1:
                ret[subtask.name] += " " + str(unwrap_seq(conts))

        return ret

