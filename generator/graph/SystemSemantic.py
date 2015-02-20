from generator.tools import stack, unwrap_seq, panic
from generator.graph.AtomicBasicBlock import E, S
from generator.graph.Sporadic import Alarm
from generator.graph.Subtask import Subtask
from generator.graph.Event import Event
from generator.graph.common import Node, Edge, EdgeType, NodeType


class SystemCallSemantic:
    def __init__(self, system_graph, running_task):
        self.running_task = running_task
        self.system_graph = system_graph

    def do_StartOS(self, block, before):
        state = before.copy_if_needed()
        # In the StartOS node all tasks are suspended before,
        # and afterwards the idle loop and the autostarted
        # tasks are ready
        for subtask in self.system_graph.subtasks:
            if subtask.conf.autostart:
                state.set_ready(subtask)
            else:
                state.set_suspended(subtask)
            state.set_continuation(subtask, subtask.entry_abb)
        state.current_abb = block
        return [state]

    def do_ActivateTask(self, block, before):
        after = before.copy_if_needed()
        # EnsureComputationBlocks ensures that after an activate task
        # only one ABB can be located
        cont = block.definite_after(E.task_level)
        after.set_continuation(self.running_task.for_abb(block),
                               cont)
        activated = block.arguments[0]
        if not after.is_surely_ready(activated):
            after.add_continuation(activated, activated.entry_abb)
            # Clear the events
            after.clear_events(activated, activated.events)
        after.set_ready(activated)
        return [after]

    def do_TerminateTask(self, block, before):
        after = before.copy_if_needed()
        calling_task = self.running_task.for_abb(block)
        after.set_continuation(calling_task, calling_task.entry_abb)
        after.set_suspended(calling_task)
        return [after]

    def do_ChainTask(self, block, before):
        after = before.copy_if_needed()
        # Suspend the current Task, this also sets the
        # continuations correctly
        calling_task = self.running_task.for_abb(block)
        after.set_continuation(calling_task, calling_task.entry_abb)
        after.set_suspended(calling_task)
        # Activate other Task
        activated = block.arguments[0]
        if not after.is_surely_ready(block.arguments[0]):
            after.add_continuation(activated, activated.entry_abb)
            # Clear the events
            after.clear_events(activated, activated.events)
        after.set_ready(activated)
        return [after]

    def do_AdvanceCounter(self, block, before):
        # Either we directly return
        notrigger = before.copy_if_needed()
        cont = block.definite_after(E.task_level)
        notrigger.set_continuation(self.running_task.for_abb(block),
                               cont)
        ret = [notrigger]

        # Or we trigger the counter
        counter = block.arguments[0]
        sporadic_events = []
        for alarm in self.system_graph.alarms:
            if not(isinstance(alarm , Alarm) and alarm.counter == counter):
                continue

            after = before.copy()
            cont = block.definite_after(E.task_level)
            after.set_continuation(self.running_task.for_abb(block),
                                   cont)
            activated = alarm.subtask
            if not after.is_surely_ready(activated):
                after.add_continuation(activated, activated.entry_abb)
                # Clear the events
                after.clear_events(activated, activated.events)
            after.set_ready(activated)
            ret.append(after)
        assert len(ret) > 1, "No Alarm for Soft-Counter defined (%s)" % counter
        return ret

    def do_WaitEvent(self, block, before):
        event_list = block.arguments[0]
        calling_task = block.subtask
        ret = []
        if before.maybe_waiting(calling_task, event_list):
            after = before.copy()
            after.set_waiting(calling_task)
            after.set_continuation(calling_task, block)
            ret.append(after)

        if before.maybe_not_waiting(calling_task, event_list):
            after = before.copy_if_needed()
            after.set_ready(calling_task)
            cont = block.definite_after(E.task_level)
            after.set_continuation(calling_task, cont)
            ret.append(after)

        return ret

    def do_SetEvent(self, block, before):
        event_list = block.arguments[0]
        calling_task = block.subtask
        unblocked_task = event_list[0].task

        after = before.copy_if_needed()
        after.set_events(unblocked_task, event_list)

        # We've done our system call, continue at successor
        cont = block.definite_after(E.task_level)
        after.set_continuation(calling_task, cont)

        waiting_block = after.get_continuations(unblocked_task)
        assert len(waiting_block) == 1
        waiting_block = list(waiting_block)[0]
        if waiting_block.isA(S.WaitEvent):
            # Reperform the WaitEvent system call
            return self.do_WaitEvent(waiting_block, after)
        else:
            return [after]

    def do_ClearEvent(self, block, before):
        event_list = block.arguments[0]
        calling_task = block.subtask

        after = before.copy_if_needed()
        after.clear_events(calling_task, event_list)

        cont = block.definite_after(E.task_level)
        after.set_continuation(calling_task, cont)

        return [after]

    def do_Idle(self, block, before):
        after = before.copy_if_needed()
        # EnsureComputationBlocks ensures that after the Idle() function
        # only one ABB can be located
        cont = block.definite_after(E.task_level)
        after.set_continuation(self.running_task.for_abb(block),
                               cont)
        return [after]

    def do_computation(self, block, before):
        next_blocks = block.get_outgoing_nodes(E.task_level)
        ret = before.copy_if_needed(len(next_blocks))
        calling_task = self.running_task.for_abb(block)
        for i in range(0, len(next_blocks)):
            ret[i].set_continuation(calling_task, next_blocks[i])
        return ret

    def do_computation_with_callstack(self, block, before):
        calling_task = self.running_task.for_abb(block)

        if block.function.exit_abb == block:
            # Function return is done from calling stack
            after = before.copy_if_needed()
            next_abb = after.get_call_stack(calling_task).pop()
            after.set_continuation(calling_task, next_abb)
            # print "Return from %s -> %s" % (block, next_abb)
            return [after]
        else:
            next_blocks = block.get_outgoing_nodes(E.task_level)
            ret = before.copy_if_needed(len(next_blocks))
            for i in range(0, len(next_blocks)):
                next_abb = next_blocks[i]
                after = ret[i]
                # If next abb is entry node, push the current abb
                if next_abb.function.entry_abb == next_abb:
                    # CALL
                    assert not next_abb in after.get_call_stack(calling_task), \
                        "Recursive function calls are not allowed. Are you insane. This is a REAL-TIME System!"
                    # We saved the virtual local control flow in the
                    # AddFunction pass, otherwise we would have lost
                    # the information about the abb to return to.
                    return_to = before.current_abb.definite_after(E.function_level)
                    after.call_stack[calling_task.subtask_id].push(return_to)
                    # print "Call from %s -> %s" % (block, next_abb)

                after.set_continuation(calling_task, next_abb)

            return ret

    def do_SystemCall(self, block, before, system_calls):
        if block.syscall_type in system_calls:
            after = system_calls[block.syscall_type](block, before)
            return after
        else:
            panic("BlockType %s is not supported yet" % block.syscall_type)

    def find_possible_next_blocks(self, source, state):
        current_running = self.running_task.for_abb(source)

        # If the current task is not preemptable, we can just continue
        # on the local task graph or on ISR blocks
        if current_running and not current_running.conf.preemptable \
           and state.is_surely_ready(current_running):
            task_conts = list(state.get_continuations(current_running))
            isr_conts  = []
            if not current_running.conf.is_isr:
                for subtask in state.get_subtasks():
                    if subtask.conf.is_isr and state.is_maybe_ready(subtask):
                        assert state.is_surely_ready(subtask)
                        isr_conts.append(subtask.entry_abb)
            if isr_conts:
                return isr_conts
            else:
                return task_conts

        # First of all all blocks blocks of maybe ready blocks are
        # possible at all. We will delete some in the future.
        # [(block, surely_running)]
        possible_blocks = []
        for subtask in state.get_unordered_subtasks():
            if state.is_surely_ready(subtask):
                conts = state.get_continuations(subtask)
                assert len (conts) > 0, \
                    "Every surely running task must have one continuation point, %s has none: %s" % (subtask, state)
                minimum_return_prio = min([x.dynamic_priority for x in conts])
                for B in conts:
                    possible_blocks.append([B, B.dynamic_priority <=  minimum_return_prio])
            elif state.is_maybe_ready(subtask):
                for B in state.get_continuations(subtask):
                    possible_blocks.append([B, False])

        # Then we sort the continuing blocks after their dynamic priority
        possible_blocks = list(sorted(possible_blocks,
                                      key = lambda x: x[0].dynamic_priority,
                                      reverse = True))

        ret = []
        # Now we take all possible blocks until we find a block, that
        # belongs to a surely runnning block
        minimum_system_prio = 0
        for block, surely in possible_blocks:
            if not surely:
                continue
            if surely:
                minimum_system_prio = max(minimum_system_prio, block.dynamic_priority)
                break
        for block, surely in possible_blocks:
            if minimum_system_prio <= block.dynamic_priority:
                ret.append(block)
        return ret

    def schedule(self, source, state, set_state_on_edge):
        possible_blocks = self.find_possible_next_blocks(source, state)
        #print(source, [(x.dynamic_priority, x.path()) for x in possible_blocks], state)

        # The possible blocks are ordered with their dynamic priority.
        # [....., Block, ....]
        # All blocks left of a block are not taken blocks
        new_states = state.copy_if_needed(len(possible_blocks))
        for i in range(0, len(possible_blocks)):
            target = possible_blocks[i]
            copy_state = new_states[i]
            state = None # Just a guard

            # Our target is surely running
            copy_state.set_ready(target.function.subtask)
            # The currently running subtask has no saved continuations
            copy_state.set_continuations(target.function.subtask, [])

            not_taken = set(possible_blocks[:i])
            # We can wipe out all continuations that are not taken, if
            # a subtask has no possible continuations anymore, it is surely suspended
            for cont in not_taken:
                subtask = cont.function.subtask
                # For the own subtask we already know where we are
                if subtask == target.function.subtask:
                    continue
                copy_state.remove_continuation(subtask, cont)
                if len(copy_state.get_continuations(subtask)) == 0:
                    copy_state.set_suspended(subtask)
                    copy_state.set_continuation(subtask, subtask.entry_abb)
                    # print subtask, " cannot be running in ", target

            copy_state.current_abb = target
            # If the target is not in the idle loop, we reset the idle
            # loop, since it always starts from the beginning. But
            # only if the target is not an ISR2
            if not target.function.subtask or \
               (target.function.subtask != self.system_graph.idle_subtask \
                and not target.function.subtask.conf.is_isr):
                copy_state.set_continuation(self.system_graph.idle_subtask,
                                            self.system_graph.idle_subtask.entry_abb)

            # Mark the new state as frozen!
            copy_state.frozen = True
            set_state_on_edge(source, target, copy_state)

        return


class SystemState(Node):
    READY = 1
    SUSPENDED = 2
    WAITING = 4

    # Static field that counts the system states that were created
    copy_count = 0

    def __init__(self, system_graph):
        Node.__init__(self, Edge, "", color="green")
        self.system_graph = system_graph
        self.frozen = False
        self.states = []
        self.continuations = []
        self.call_stack = []
        for subtask in self.system_graph.subtasks:
            self.states.append(0)
            self.continuations.append(set())
            self.call_stack.append(None)
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
        assert not self.frozen
        assert not self.call_stack[subtask.subtask_id] is None
        return self.call_stack[subtask.subtask_id]

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
        for subtask_id in range(0, Subtask.subtask_id_counter):
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


class PreciseSystemState(SystemState):
    def __init__(self, system_graph):
        Node.__init__(self, Edge, "", color="green")
        self.system_graph = system_graph
        self.frozen = False
        self.states = []
        self.continuations = []
        self.events = []
        self.events_cleared = []
        self.call_stack = []
        for subtask in self.system_graph.subtasks:
            self.states.append(0)
            self.continuations.append(None)
            self.call_stack.append([])
            self.events.append(0) # A bit mask
        self.current_abb = None
        self.__hash = None

    def new(self):
        return PreciseSystemState(self.system_graph)

    def copy(self):
        # Increase the copy counter
        SystemState.copy_count += 1

        state = self.new()
        state.current_abb = self.current_abb
        state.states = list(self.states)
        state.continuations = list(self.continuations)
        state.events = list(self.events)

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

    def freeze(self):
        self.frozen = True

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

