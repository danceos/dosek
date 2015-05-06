from generator.tools import stack, unwrap_seq, panic
from .AtomicBasicBlock import E, S
from .Sporadic import Alarm
from .Subtask import Subtask
from .Event import Event
from .common import Node, Edge, EdgeType, NodeType
from .SystemState import SystemState

class PreciseSystemState(SystemState):
    """A precise system state is a system state. It cannot have unknown
      fields, and is optimized for speed in the symbolic system execution."""
    def __init__(self, system_graph):
        SystemState.__init__(self, system_graph)

        size = len(self.system_graph.subtasks)

        delattr(self, "events_cleared")
        delattr(self, "events_set")

        self.events = [0] * size
        for i in range(0, size):
            self.continuations[i] = None
            self.call_stack[i] = list()

        self.__hash = None

    def new(self):
        return PreciseSystemState(self.system_graph)

    def copy(self):
        # Increase the copy counter
        SystemState.copy_count += 1

        state = self.new()
        state.current_abb = self.current_abb
        def copyto(dst, src):
            for idx in range(0, len(src)):
                dst[idx] = src[idx]

        copyto(state.states, self.states)
        copyto(state.continuations, self.continuations)
        copyto(state.events, self.events)

        for subtask_id in range(0, len(self.states)):
            state.call_stack[subtask_id] = stack(self.call_stack[subtask_id])

        return state

    ## Continuations
    def get_continuations(self, subtask):
        if type(subtask) == int:
            return set([self.continuations[subtask]])

        return set([self.continuations[subtask.subtask_id]])

    def set_continuation(self, subtask, abb):
        assert not self.frozen
        self.continuations[subtask.subtask_id] = abb

    def set_continuations(self, subtask, abbs):
        assert not self.frozen
        assert(len(abbs) <= 1)
        if len(abbs) == 1:
            self.continuations[subtask.subtask_id] = abbs[0]
        else:
            self.continuations[subtask.subtask_id] = None

    def remove_continuation(self, subtask, abb):
        assert not self.frozen
        assert abb == self.continuations[subtask.subtask_id]
        self.continuations[subtask.subtask_id] = None

    def add_continuation(self, subtask, abb):
        assert not self.frozen
        assert self.continuations[subtask.subtask_id] in (None, abb)
        self.continuations[subtask.subtask_id] = abb

    def get_call_stack(self, subtask):
        assert not self.frozen
        assert not self.call_stack[subtask.subtask_id] is None
        return self.call_stack[subtask.subtask_id]

    # Events
    def get_events(self, subtask):
        """Return a tuple (None, set)"""
        events = self.events[subtask.subtask_id]
        return (subtask.event_mask_valid ^ events, events)

    def set_events(self, subtask, event_list):
        mask = Event.combine_event_masks(event_list)
        self.events[subtask.subtask_id] |= mask

    def clear_events(self, subtask, event_list):
        mask = Event.combine_event_masks(event_list)
        self.events[subtask.subtask_id] &= ~mask

    def maybe_waiting(self, subtask, event_list):
        """Returns True, if the task may block be waiting at this point"""
        mask = Event.combine_event_masks(event_list)
        if (self.events[subtask.subtask_id] & mask) == 0:
            return True
        return False

    def maybe_not_waiting(self, subtask, event_list):
        """Returns True, if the task may be continue without blocking"""
        # In the precise system state, this is the exact opposite
        return not self.maybe_waiting(subtask, event_list)

    def is_event_set(self, subtask, event):
        return (self.events[subtask.subtask_id] & event.event_mask) != 0

    def is_event_cleared(self, subtask, event):
        return (self.events[subtask.subtask_id] & event.event_mask) == 0

    ## Continuation accesors
    def was_surely_not_kickoffed(self, subtask):
        """Returns whether a task can only continue in the kickoff block."""
        assert subtask.entry_abb.isA(S.kickoff)
        is_entry = [subtask.entry_abb == x for x in self.get_continuations(subtask)]
        return all(is_entry)

    def was_surely_kickoffed(self, subtask):
        """Returns whether a task can only be continued."""
        assert subtask.entry_abb.isA(S.kickoff)
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
        count = float(len(self.get_unordered_subtasks()))
        for subtask in self.get_unordered_subtasks():
            if not self.is_unsure_ready_state(subtask):
                subtask_score += 1
            # If there is no continuation, we know that we have the
            # currently running task at our hands.
            if len(self.get_continuations[subtask.subtask_id]) == 0:
                continuation_score += 1.0
            else:
                # Calculate a score that gets lower when there are more continuations
                continuation_score += 1.0/len(self.continuations[subtask.subtask_id])

        subtask_score = subtask_score / count
        continuation_score = continuation_score / count
        ret = (subtask_score + continuation_score) / 2.0
        assert (ret >= 0.0 and ret <= 1.0)
        return ret

    @property
    def current_subtask(self):
        return self.current_abb.function.subtask

    def merge_with(self, other):
        """Returns a newly created state that is the result of the merge of
           self and the other state"""
        assert False, "Cannot merge something into a precise state"

    def __hash__(self):
        assert self.frozen, "Only frozen states can be hashed"
        if self.__hash != None:
            return self.__hash

        ret = 0
        # XOR does comute!
        ret ^= hash(self.current_abb)
        for state in self.states:
            ret ^= hash(state)
        for event in self.events:
            ret ^= hash(event)
        for conts in self.continuations:
            ret ^= hash(conts)
        for call_stack in self.call_stack:
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
            # The event masks must be equal
            if not self.events[subtask_id] == other.events[subtask_id]:
                return False
            # The possible continuations have to be equal
            if not self.continuations[subtask_id] == other.continuations[subtask_id]:
                return False
            # The call stack has to be equal
            if not self.call_stack[subtask_id] == other.call_stack[subtask_id]:
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
            ret[subtask.name] += " " +  self.format_events(subtask)

        return ret

