from generator.tools import stack, unwrap_seq, panic
from .AtomicBasicBlock import E, S
from .Sporadic import Alarm
from .Subtask import Subtask
from .Event import Event
from .common import Node, Edge, EdgeType, NodeType
from .SystemState import SystemState

class PreciseSystemState():
    """A precise system state is a system state. It cannot have unknown
      fields, and is optimized for speed in the symbolic system execution."""

    READY = 1
    SUSPENDED = 2
    WAITING = 4

    system_graph = None

    __slots__ = ["frozen", "states", "call_stack", "continuations",
                 "current_abb", "__hash", "__next_states", "__prev_states", "events"]

    def __init__(self, system_graph, init = True):
        PreciseSystemState.system_graph = system_graph
        self.frozen = False
        self.__hash = None
        self.__next_states = []
        self.__prev_states = []

        if not init:
            return

        size = len(self.system_graph.subtasks)
        self.states = [0] * size
        self.continuations = [None] * size
        self.current_abb = None
        self.events = [0] * size
        self.call_stack = []
        for i in range(0, size):
            self.call_stack.append(list())

    def new(self):
        return PreciseSystemState(self.system_graph)

    def add_cfg_edge(self, block, ty, label = None):
        self.__next_states.append((ty, block, label))
        block.__prev_states.append((ty, self, label))

    def remove_cfg_edge(self, block, ty):
        for i, elem in enumerate(self.__next_states):
            if tuple(elem[0:2]) == (ty, block):
                del self.__next_states[i]
                break

        for i, elem in enumerate(block.__prev_states):
            if tuple(elem[0:2]) == (ty, self):
                del block.__prev_states[i]
                break

    def get_outgoing_nodes(self, ty):
        return [block for Ty,block,label in self.__next_states if Ty == ty]

    def get_incoming_nodes(self, ty):
        return [block for Ty,block,label in self.__prev_states if Ty == ty]

    def get_outgoing_edges(self, ty):
        return [(block, label) for Ty,block,label in self.__next_states if Ty == ty]

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

    def copy(self):
        # Increase the copy counter
        SystemState.copy_count += 1

        # For faster copying, we use the do-not-init constructor and
        # do everything ourselves here.
        state = PreciseSystemState(self.system_graph, init = False)
        state.current_abb = self.current_abb

        # Shallow copies
        state.states = self.states[:]
        state.continuations = self.continuations[:]
        state.events = self.events[:]
        state.call_stack = []
        for subtask_id in range(0, len(self.states)):
            state.call_stack.append(self.call_stack[subtask_id][:])

        return state

    def get_subtasks(self):
        """Sorted by priority"""
        return sorted(self.system_graph.subtasks,
                      key=lambda x: x.static_priority, reverse = True)

    def get_unordered_subtasks(self):
        return self.system_graph.subtasks


    def set_suspended(self, subtask):
        assert not self.frozen
        self.states[subtask.subtask_id] = self.SUSPENDED

    def set_ready(self, subtask):
        assert not self.frozen
        self.states[subtask.subtask_id] = self.READY

    def set_waiting(self, subtask):
        assert not self.frozen
        self.states[subtask.subtask_id] = self.WAITING

    ## Ready state accessors
    def is_surely_suspended(self, subtask):
        return self.states[subtask.subtask_id] == self.SUSPENDED

    def is_surely_ready(self, subtask):
        return self.states[subtask.subtask_id] == self.READY

    def is_surely_waiting(self, subtask):
        return self.states[subtask.subtask_id] == self.WAITING

    def is_maybe_ready(self, subtask):
        return self.READY & self.states[subtask.subtask_id]

    def is_maybe_suspended(self, subtask):
        return self.SUSPENDED & self.states[subtask.subtask_id]

    def is_unsure_ready_state(self, subtask):
        return False

    ## Continuations
    def get_continuations(self, subtask):
        if type(subtask) == int:
            return set([self.continuations[subtask]])
        return set([self.continuations[subtask.subtask_id]])

    def get_continuation(self, subtask):
        if type(subtask) == int:
            return self.continuations[subtask]
        return self.continuations[subtask.subtask_id]

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
    def __events(self, subtask, set_events = None, set_block_list = None):
        events = self.events[subtask.subtask_id] & 0xffff
        block_list = (self.events[subtask.subtask_id] >> 16) & 0xffff
        if not set_events is None:
            assert (set_events & 0xffff == set_events)
            self.events[subtask.subtask_id] = (set_events | (block_list << 16))
            events = set_events
        if not set_block_list is None:
            assert (set_block_list & 0xffff == set_block_list)
            self.events[subtask.subtask_id] = (events | (set_block_list << 16))
            block_list = set_block_list

        return (events, block_list)

    def get_events(self, subtask):
        """Return a tuple (None, set)"""
        events, _ = self.__events(subtask)
        return (subtask.event_mask_valid ^ events, events)

    def set_events(self, subtask, event_list):
        mask = Event.combine_event_masks(event_list)
        events, bl = self.__events(subtask)
        events |= mask
        self.__events(subtask, set_events = events)

    def clear_events(self, subtask, event_list):
        mask = Event.combine_event_masks(event_list)
        events, bl = self.__events(subtask)
        events &= ~mask
        assert bl == 0
        self.__events(subtask, set_events = events)

    def clear_block_list(self, subtask):
        self.__events(subtask, set_block_list = 0)

    def set_block_list(self, subtask, event_list):
        mask = Event.combine_event_masks(event_list)
        self.__events(subtask, set_block_list = mask)

    def get_block_list(self, subtask):
        events, bl = self.__events(subtask)
        return bl

    def maybe_waiting(self, subtask):
        """Returns True, if the task may block be waiting at this point"""
        events, block_list = self.__events(subtask)
        if (block_list & events) == 0:
            return True
        return False

    def maybe_not_waiting(self, subtask):
        """Returns True, if the task may be continue without blocking"""
        # In the precise system state, this is the exact opposite
        return not self.maybe_waiting(subtask)

    def is_event_set(self, subtask, event):
        events, block_list = self.__events(subtask)

        return (events & event.event_mask) != 0

    def is_event_waiting(self, subtask, event):
        events, block_list = self.__events(subtask)
        return (block_list & event.event_mask) != 0

    def is_event_cleared(self, subtask, event):
        events, block_list = self.__events(subtask)

        return (events & event.event_mask) == 0

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
        return self.current_abb.subtask

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
        if not isinstance(other, PreciseSystemState):
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
            WAITING = self.is_event_waiting(subtask, event)
            if SET and CLEARED:
                ret.append("%s:*" % event.conf.name)
            elif SET:
                ret.append("%s:1" % event.conf.name)
            else:
                assert CLEARED
                ret.append("%s:0" % event.conf.name)
            if WAITING:
                ret[-1] += ":W"
        return " ".join(ret)


    def definite_after(self, level):
        nodes = self.get_outgoing_nodes(level)
        assert len(nodes) == 1
        return nodes[0]

    def definite_before(self, level):
        nodes = self.get_incoming_nodes(level)
        assert len(nodes) == 1
        return nodes[0]

    def __repr__(self):
        if self.current_abb:
            ret = "<PreciseSystemState: %s>\n" %(self.current_abb.path())
        else:
            ret = "<PreciseSystemState: -->\n"

        for subtask in self.get_subtasks():
            ret += "  %02x%02x %s: %s in %s [%s]\n" %(
                id(self.states[subtask.subtask_id]) % 256,
                id(self.continuations[subtask.subtask_id]) % 256,
                subtask, self.format_state(self.states[subtask.subtask_id]),
                self.continuations[subtask.subtask_id],
                self.format_events(subtask))
        ret += "</PreciseSystemState>\n"
        return ret
    
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
