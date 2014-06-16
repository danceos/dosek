from generator.tools import stack, unwrap_seq
from generator.graph.AtomicBasicBlock import E, S
from generator.graph.common import Node, Edge, EdgeType, NodeType


class SystemCallSemantic:
    def __init__(self, system_graph, running_task):
        self.running_task = running_task
        self.system_graph = system_graph

    def do_StartOS(self, block, before):
        state = before.copy()
        # In the StartOS node all tasks are suspended before,
        # and afterwards the idle loop and the autostarted
        # tasks are ready
        for subtask in self.system_graph.get_subtasks():
            if subtask.autostart:
                state.set_ready(subtask)
            else:
                state.set_suspended(subtask)
            state.set_continuation(subtask, subtask.entry_abb)
        state.current_abb = block
        return [state]

    def do_ActivateTask(self, block, before):
        after = before.copy()
        # EnsureComputationBlocks ensures that after an activate task
        # only one ABB can be located
        cont = block.definite_after(E.task_level)
        after.set_continuation(self.running_task.for_abb(block),
                               cont)
        activated = block.arguments[0]
        if not after.is_surely_ready(block.arguments[0]):
            after.add_continuation(activated, activated.entry_abb)
        after.set_ready(activated)
        return [after]

    def do_TerminateTask(self, block, before):
        after = before.copy()
        calling_task = self.running_task.for_abb(block)
        after.set_continuation(calling_task, calling_task.entry_abb)
        after.set_suspended(calling_task)
        return [after]

    def do_ChainTask(self, block, before):
        after = before.copy()
        # Suspend the current Task, this also sets the
        # continuations correctly
        calling_task = self.running_task.for_abb(block)
        after.set_continuation(calling_task, calling_task.entry_abb)
        after.set_suspended(calling_task)
        # Activate other Task
        activated = block.arguments[0]
        if not after.is_surely_ready(block.arguments[0]):
            after.add_continuation(activated, activated.entry_abb)
        after.set_ready(activated)
        return [after]

    def do_Idle(self, block, before):
        after = before.copy()
        # EnsureComputationBlocks ensures that after the Idle() function
        # only one ABB can be located
        cont = block.definite_after(E.task_level)
        after.set_continuation(self.running_task.for_abb(block),
                               cont)
        return [after]

    def do_computation(self, block, before):
        ret = []
        calling_task = self.running_task.for_abb(block)
        for next_abb in block.get_outgoing_nodes(E.task_level):
            after = before.copy()
            after.set_continuation(calling_task, next_abb)
            ret.append(after)
        return ret

    def do_computation_with_callstack(self, block, before):
        calling_task = self.running_task.for_abb(block)

        if block.function.exit_abb == block:
            # Function return is done from calling stack
            after = before.copy()
            next_abb = after.get_call_stack(calling_task).pop()
            after.set_continuation(calling_task, next_abb)
            # print "Return from %s -> %s" % (block, next_abb)
            return [after]
        else:
            ret = []
            for next_abb in block.get_outgoing_nodes(E.task_level):
                after = before.copy()
                # If next abb is entry node, push the current abb
                if next_abb.function.entry_abb == next_abb:
                    # CALL
                    assert not next_abb in after.get_call_stack(calling_task), \
                        "Recursive function calls are not allowed. Are you insane. This is a REAL-TIME System!"
                    # We saved the virtual local control flow in the
                    # AddFunction pass, otherwise we would have lost
                    # the information about the abb to return to.
                    return_to = before.current_abb.definite_after(E.function_level)
                    after.call_stack[calling_task].push(return_to)
                    # print "Call from %s -> %s" % (block, next_abb)

                after.set_continuation(calling_task, next_abb)
                ret.append(after)
            return ret

    def do_SystemCall(self, block, before, system_calls):
        if block.syscall_type in system_calls:
            after = system_calls[block.syscall_type](block, before)
            for x in after:
                x.freeze()
            return after
        else:
            panic("BlockType %s is not supported yet" % block.syscall_type)

    def find_possible_next_blocks(self, source, state):
        current_running = self.running_task.for_abb(source)

        # If the current task is not preemptable, we can just continue
        # on the local task graph or on ISR blocks
        if current_running and not current_running.preemptable \
           and state.is_surely_ready(current_running):
            task_conts = list(state.get_continuations(current_running))
            isr_conts  = []
            if not current_running.is_isr:
                for subtask in state.get_subtasks():
                    if subtask.is_isr and state.is_maybe_ready(subtask):
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
        for i in range(0, len(possible_blocks)):
            target = possible_blocks[i]
            copy_state = state.copy()
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
            # loop, since it always starts from the beginning.
            if not target.function.subtask or \
               target.function.subtask != self.system_graph.idle_subtask:
                copy_state.set_continuation(self.system_graph.idle_subtask,
                                            self.system_graph.idle_subtask.entry_abb)

            # Mark the new state as frozen!
            copy_state.frozen = True
            set_state_on_edge(source, target, copy_state)

        return


class SystemState(Node):
    READY = 1
    SUSPENDED = 2

    # Static field that counts the system states that were created
    copy_count = 0

    def __init__(self, system_graph):
        Node.__init__(self, Edge, "", color="green")
        self.system_graph = system_graph
        self.frozen = False
        self.states = {}
        self.continuations = {}
        self.call_stack = {}
        for subtask in self.system_graph.get_subtasks():
            self.states[subtask] = 0
            self.continuations[subtask] = set()
            self.call_stack[subtask] = None
        self.current_abb = None

    def new(self):
        return SystemState(self.system_graph)

    def copy(self):
        # Increase the copy counter
        SystemState.copy_count += 1

        state = SystemState(self.system_graph)
        state.current_abb = self.current_abb
        for subtask in self.get_unordered_subtasks():
            state.states[subtask] = self.states[subtask]
            state.continuations[subtask] = set(self.continuations[subtask])

            # Only used by SymbolicSystemExecution
            if not self.call_stack[subtask] is None:
                state.call_stack[subtask] = stack(self.call_stack[subtask])
        assert self == state
        return state

    def get_subtasks(self):
        """Sorted by priority"""
        return sorted(self.system_graph.get_subtasks(),
                      key=lambda x: x.static_priority, reverse = True)

    def get_unordered_subtasks(self):
        return self.system_graph.get_subtasks()

    def get_task_states(self, subtask):
        return self.states[subtask]

    def set_suspended(self, subtask):
        assert not self.frozen
        self.states[subtask] = self.SUSPENDED

    def set_ready(self, subtask):
        assert not self.frozen
        self.states[subtask] = self.READY

    ## Ready state accessors

    def is_surely_suspended(self, subtask):
        return self.states[subtask] == self.SUSPENDED

    def is_surely_ready(self, subtask):
        return self.states[subtask] == self.READY

    def is_maybe_ready(self, subtask):
        return self.READY & self.states[subtask]

    def is_maybe_suspended(self, subtask):
        return self.SUSPENDED & self.states[subtask]

    def is_unsure_ready_state(self, subtask):
        return bin(self.states[subtask]).count("1") > 1

    ## Continuations
    def get_continuations(self, subtask):
        return self.continuations[subtask]

    def set_continuation(self, subtask, abb):
        assert not self.frozen
        self.continuations[subtask] = set([abb])

    def set_continuations(self, subtask, abbs):
        assert not self.frozen
        self.continuations[subtask] = set(abbs)

    def remove_continuation(self, subtask, abb):
        assert not self.frozen
        assert abb in self.continuations[subtask]
        self.continuations[subtask].discard(abb)

    def add_continuation(self, subtask, abb):
        assert not self.frozen
        self.continuations[subtask].add(abb)

    def get_call_stack(self, subtask):
        assert not self.frozen
        assert not self.call_stack[subtask] is None
        return self.call_stack[subtask]

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
            if len(self.continuations[subtask]) == 0:
                continuation_score += 1.0
            else:
                # Calculate a score that gets lower when there are more continuations
                continuation_score += 1.0/len(self.continuations[subtask])

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
        assert not self.frozen
        assert self.current_abb == None or self.current_abb == other.current_abb,\
            "%s != %s" %(self.current_abb.path(), other.current_abb.path())
        self.current_abb = other.current_abb
        changed = False
        for subtask in self.get_unordered_subtasks():
            old_state = self.states[subtask]
            continuations_count = len(self.continuations[subtask])
            self.states[subtask] |= other.states[subtask]
            self.continuations[subtask] |= other.continuations[subtask]
            # Check whether one set has changed
            if self.states[subtask] != old_state \
               or len(self.continuations[subtask]) != continuations_count:
                changed = True

            # We cannot merge call stacks!
            self.call_stack[subtask] = None
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

        return "|".join(ret)

    def __repr__(self):
        ret = "<SystemState: %s>\n" %(self.current_abb.path())
        for subtask in self.get_subtasks():
            ret += "  %02x%02x %s: %s in %s \n" %(
                id(self.states[subtask]) % 256,
                id(self.continuations[subtask]) % 256,
                subtask, self.format_state(self.states[subtask]),
                self.continuations[subtask])
        ret += "</SystemState>\n"
        return ret

    def __hash__(self):
        assert self.frozen, "Only frozen states can be hashed"
        ret = 0
        # XOR does comute!
        ret ^= hash(self.current_abb)
        for state in list(self.states.values()):
            ret ^= hash(state)
        for conts in list(self.continuations.values()):
            for cont in conts:
                ret ^= hash(cont)
        for call_stack in list(self.call_stack.values()):
            if not call_stack:
                continue
            for go_back in call_stack:
                ret ^= hash(go_back)

        return ret

    def __eq__(self, other):
        if id(self) == id(other):
            return True
        if not isinstance(other, SystemState):
            return False
        # The Currently Running Task has to be equal
        if not self.current_abb == other.current_abb:
            return False

        for subtask in list(self.states.keys()):
            # The subtask states have to equal
            if not self.states[subtask] == other.states[subtask]:
                return False
            # The possible continuations have to be equal
            if not self.continuations[subtask] == other.continuations[subtask]:
                return False
            # The call stack has to be equal
            if not self.continuations[subtask] == other.continuations[subtask]:
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
        for subtask, state in self.states.items():
            ret[subtask.name] = self.format_state(state)
            conts = self.get_continuations(subtask)
            assert len(conts) <= 1
            if len(conts) == 1:
                ret[subtask.name] += " " + str(unwrap_seq(conts))

        return ret
