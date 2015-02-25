from generator.tools import stack, unwrap_seq, panic
from generator.graph.AtomicBasicBlock import E, S
from generator.graph.Sporadic import Alarm
from generator.graph.Subtask import Subtask
from generator.graph.Event import Event
from generator.graph.common import Node, Edge, EdgeType, NodeType
from .SystemState import SystemState
from .PreciseSystemState import PreciseSystemState


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
            activated = alarm.conf.subtask
            assert alarm.conf.event is None
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
            after = before.copy()
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

        waiting_block = after.get_continuations(unblocked_task)
        assert(len(waiting_block) == 1)
        waiting_block = list(waiting_block)[0]
        if waiting_block.isA(S.WaitEvent):
            # Recheck the blocking state
            block_list = waiting_block.arguments[0]
            # Check if the unblocked task is still blocking
            if after.maybe_not_waiting(unblocked_task, block_list):
                after.set_ready(unblocked_task)

        # We've done our system call, continue at successor
        cont = block.definite_after(E.task_level)
        after.set_continuation(calling_task, cont)

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

            # If the new state will resume to a WaitEvent, we redo the
            # wait event to succeed to the next block. We do this only, if we resume from another subtask
            if copy_state.current_abb.isA(S.WaitEvent) and source.subtask != target.subtask:
                wait_event = copy_state.current_abb
                calling_task = wait_event.subtask
                event_list = wait_event.arguments[0]
                if copy_state.maybe_not_waiting(calling_task, event_list):
                    assert copy_state.is_surely_ready(calling_task)
                    cont = wait_event.definite_after(E.task_level)
                    copy_state.current_abb = cont
                    target = cont

            # Mark the new state as frozen!
            copy_state.frozen = True
            set_state_on_edge(source, target, copy_state)

        return


