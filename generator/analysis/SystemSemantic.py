from generator.tools import stack, unwrap_seq, panic
from .AtomicBasicBlock import E, S
from .Sporadic import Alarm
from .Subtask import Subtask
from .Event import Event
from .common import Node, Edge, EdgeType, NodeType
from .SystemState import SystemState
from .PreciseSystemState import PreciseSystemState
from .ApplicationFSM import ApplicationFSMIterator


class SystemCallSemantic:
    def __init__(self, system_graph, use_app_fsm = False):
        self.system_graph = system_graph
        self.use_app_fsm = use_app_fsm

    def __entry_point(self, subtask):
        if self.use_app_fsm:
            return ApplicationFSMIterator.create(subtask, subtask.fsm.initial_state)
        else:
            return subtask.entry_abb

    def __next_continuations(self, cont, before_state, action):
        assert type(self.use_app_fsm) == bool
        if self.use_app_fsm:
            return cont.next_iterators(action)
        else:
            assert cont == action
            return action.get_outgoing_nodes(E.task_level)

    def __next_continuation(self, cont, before_state, action):
        ret = self.__next_continuations(cont, before_state, action)
        assert len(ret) == 1
        return ret[0]


    def do_StartOS(self, _, before, syscall):
        state = before.copy_if_needed()
        # In the StartOS node all tasks are suspended before,
        # and afterwards the idle loop and the autostarted
        # tasks are ready
        for subtask in self.system_graph.subtasks:
            if subtask.conf.autostart:
                state.set_ready(subtask)
            else:
                state.set_suspended(subtask)
            state.set_continuation(subtask, self.__entry_point(subtask))
        return [(syscall, state)]

    def do_ActivateTask(self, cont, before, syscall):
        after = before.copy_if_needed()
        # EnsureComputationBlocks ensures that after an activate task
        # only one ABB can be located
        next_cont = self.__next_continuation(cont, before, syscall)
        after.set_continuation(cont.subtask, next_cont)
        activated = syscall.arguments[0]
        if not (after.is_surely_ready(activated) or after.is_surely_waiting(activated)):
            after.add_continuation(activated, self.__entry_point(activated))
            # Clear the events
            after.clear_events(activated, activated.events)
        after.set_ready(activated)
        return [(syscall, after)]

    def do_TerminateTask(self, cont, before, syscall):
        after = before.copy_if_needed()
        calling_task = cont.subtask
        after.set_continuation(calling_task, self.__entry_point(calling_task))
        after.set_suspended(calling_task)
        return [(syscall, after)]

    def do_ChainTask(self, cont, before, syscall):
        after = before.copy_if_needed()
        # Suspend the current Task, this also sets the
        # continuations correctly
        calling_task = cont.subtask
        after.set_continuation(calling_task, self.__entry_point(calling_task))
        after.set_suspended(calling_task)
        # Activate other Task
        activated = syscall.arguments[0]
        if not (after.is_surely_ready(activated) or after.is_surely_waiting(activated)):
            after.add_continuation(activated, self.__entry_point(activated))
            # Clear the events
            after.clear_events(activated, activated.events)
        after.set_ready(activated)
        return [(syscall, after)]

    def do_AdvanceCounter(self, cont, before, syscall):
        # Either we directly return
        notrigger = before.copy_if_needed()
        cont_after = cont.definite_after(E.task_level)
        notrigger.set_continuation(cont.subtask, cont_after)
        ret = [(syscall, notrigger)]

        # Or we trigger the counter
        counter = syscall.arguments[0]
        sporadic_events = []
        for alarm in self.system_graph.alarms:
            if not(isinstance(alarm , Alarm) and alarm.conf.counter == counter):
                continue

            after = before.copy()
            cont_after = cont.definite_after(E.task_level)
            after.set_continuation(cont.subtask, cont_after)
            activated = alarm.conf.subtask
            assert alarm.conf.event is None
            if not after.is_surely_ready(activated):
                after.add_continuation(activated, self.__entry_point(activated))
                # Clear the events
                after.clear_events(activated, activated.events)
            after.set_ready(activated)
            ret.append((syscall, after))
        assert len(ret) > 1, "No Alarm for Soft-Counter defined (%s)" % counter
        return ret

    def do_WaitEvent(self, cont, before, syscall):
        event_list = syscall.arguments[0]
        calling_task = cont.subtask
        ret = []
        after = before.copy()
        after.set_block_list(calling_task, event_list)
        if after.maybe_waiting(calling_task):
            after.set_waiting(calling_task)
            next_cont = self.__next_continuation(cont, before, syscall)
            after.set_continuation(calling_task, next_cont)
            ret.append((syscall, after))

        after = before.copy()
        after.set_block_list(calling_task, event_list)
        if after.maybe_not_waiting(calling_task):
            after.set_ready(calling_task)
            after.clear_block_list(calling_task)
            next_cont = self.__next_continuation(cont, before, syscall)
            after.set_continuation(calling_task, next_cont)
            ret.append((syscall, after))

        return ret

    def do_SetEvent(self, cont, before, syscall):
        event_list = syscall.arguments[0]
        calling_task = cont.subtask
        unblocked_task = event_list[0].task

        after = before.copy_if_needed()
        after.set_events(unblocked_task, event_list)
        if after.maybe_not_waiting(unblocked_task):
            after.set_ready(unblocked_task)
            # WE DO NOT CLEAR THE BLOCK LIST HERE, BUT IN THE NEXT
            # DISPATCH.  By this, we indicated, that the block was
            # woken up (important for non-preemptable extended tasks)
            # Look at the dispatcher

        # We've done our system call, continue at successor
        cont = self.__next_continuation(cont, before, syscall)
        after.set_continuation(calling_task, cont)

        return [(syscall, after)]

    def do_ClearEvent(self, cont, before, syscall):
        event_list = syscall.arguments[0]
        calling_task = cont.subtask

        after = before.copy_if_needed()
        after.clear_events(calling_task, event_list)

        # We've done our system call, continue at successor
        cont = self.__next_continuation(cont, before, syscall)
        after.set_continuation(calling_task, cont)

        return [(syscall, after)]

    def do_CheckAlarm(self, cont, before, syscall):
        alarm_object = syscall.arguments[0]
        next_cont = self.__next_continuations(cont, before, syscall)
        syscalls = next_cont[:] # COPY!
        if self.use_app_fsm:
            for idx, cont in enumerate(next_cont):
                follower = cont.possible_systemcalls
                assert len(follower) == 1, follower
                syscalls[idx] = follower[0]

        chain_item = None
        if syscalls[0] == alarm_object.carried_syscall:
            action_syscall, chain_item = next_cont
        else:
            assert syscalls[1] == alarm_object.carried_syscall
            chain_item, action_syscall = next_cont

        ret = [(syscall, before.copy())]
        ret[0][1].set_continuation(syscall.subtask, chain_item)
        if alarm_object.can_trigger(before):
            ret.append( (syscall, before.copy()) )
            ret[1][1].set_continuation(syscall.subtask, action_syscall)

        # If we use the Application FSMs, we redo both system calls to
        # elimiate the CheckAlarm syscall edges
        if self.use_app_fsm:
            for idx, (_, state) in enumerate(ret):
                ret[idx] = (None, state)

        return ret

    def do_Idle(self, cont, before, syscall):
        after = before.copy_if_needed()
        # EnsureComputationBlocks ensures that after the Idle() function
        # only one ABB can be located
        next_cont = self.__next_continuation(cont, before, syscall)
        after.set_continuation(cont.subtask, next_cont)
        return [(syscall, after)]

    def do_computation(self, cont, before, syscall):
        next_blocks = self.__next_continuations(cont, before, syscall)
        ret = [(syscall, before.copy()) for _ in range(0, len(next_blocks))]
        calling_task = cont.subtask
        for i in range(0, len(next_blocks)):
            ret[i][1].set_continuation(calling_task, next_blocks[i])
        return ret

    def do_computation_with_callstack(self, cont, before, syscall):
        calling_task = cont.subtask

        if syscall.function.exit_abb == syscall:
            # Function return is done from calling stack
            after = before.copy_if_needed()
            next_abb = after.get_call_stack(calling_task).pop()
            after.set_continuation(calling_task, next_abb)
            # print "Return from %s -> %s" % (block, next_abb)
            return [(syscall, after)]
        else:
            next_blocks = self.__next_continuations(cont, before, syscall)
            # Get enought return block copies
            ret = [(syscall, x) for x in before.copy_if_needed(len(next_blocks))]
            for i in range(0, len(next_blocks)):
                next_abb = next_blocks[i]
                after = ret[i][1]
                # If next abb is entry node, push the current abb
                if next_abb.function.entry_abb == next_abb:
                    # CALL
                    assert not next_abb in after.get_call_stack(calling_task), \
                        "Recursive function calls are not allowed. Are you insane. This is a REAL-TIME System!"
                    # We saved the virtual local control flow in the
                    # AddFunction pass, otherwise we would have lost
                    # the information about the abb to return to.
                    return_to = before.current_abb.definite_after(E.function_level)
                    after.call_stack[calling_task.subtask_id].append(return_to)
                    # print "Call from %s -> %s" % (block, next_abb)

                after.set_continuation(calling_task, next_abb)

            return ret

    def do_SystemCall(self, cont, before, system_calls):
        if self.use_app_fsm and isinstance(cont, ApplicationFSMIterator):
            ret = []
            syscalls = cont.possible_systemcalls
            #if not "Alarm" in str(cont):
            #    print(str(before).count("RDY"), cont, "->", syscalls)
            for syscall in syscalls:
                after = system_calls[syscall.syscall_type](cont, before, syscall)
                ret.extend(after)
            return ret
        else:
            if cont.syscall_type in system_calls:
                # Returns [(ABB, State)]
                return system_calls[cont.syscall_type](cont, before, cont)
            else:
                panic("BlockType %s is not supported yet" % cont.syscall_type)

    def dynamic_priority(self, state, block):
        subtask = block.subtask
        if state.get_block_list(subtask) != 0:
            return subtask.conf.static_priority
        return block.dynamic_priority

    def find_possible_next_blocks(self, source, state):
        current_running = source.subtask

        # If the current task is not preemptable, we can just continue
        # on the local task graph or on ISR blocks
        if current_running and not current_running.conf.preemptable \
           and state.is_surely_ready(current_running):
            task_conts = list(state.get_continuations(current_running))
            isr_conts  = []
            if not current_running.conf.is_isr:
                for subtask in state.get_subtasks():
                    if subtask.conf.is_isr and state.is_maybe_ready(subtask):
                        isr_blocks = state.get_continuations(subtask)
                        assert state.is_surely_ready(subtask)
                        assert len(isr_blocks) == 1
                        isr_conts.extend(isr_blocks)
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
                conts_prio = [(B, self.dynamic_priority(state, B)) for B in conts]
                minimum_return_prio = min([prio for B, prio in conts_prio])
                for B, prio in conts_prio:
                    possible_blocks.append(( B, prio, prio <=  minimum_return_prio))
            elif state.is_maybe_ready(subtask):
                for B in state.get_continuations(subtask):
                    prio = self.dynamic_priority(state, B)
                    possible_blocks.append((B, prio, False))

        # Then we sort the continuing blocks after their dynamic priority
        possible_blocks = list(sorted(possible_blocks,
                                      key = lambda x: x[1], # (block, prio, surely_ready)
                                      reverse = True))

        ret = []
        # Now we take all possible blocks until we find a block, that
        # belongs to a surely runnning block
        minimum_system_prio = 0
        for block, prio, surely in possible_blocks:
            if not surely:
                continue
            if surely:
                minimum_system_prio = max(minimum_system_prio, block.dynamic_priority)
                break
        for block, prio, surely in possible_blocks:
            if minimum_system_prio <= prio:
                ret.append(block)
        return ret

    def schedule_imprecise(self, source, state):
        possible_blocks = self.find_possible_next_blocks(source, state)

        # The possible blocks are ordered with their dynamic priority.
        # [....., Block, ....]
        # All blocks left of a block are not taken blocks
        new_states = state.copy_if_needed(len(possible_blocks))
        for i in range(0, len(possible_blocks)):
            target = possible_blocks[i]
            copy_state = new_states[i]
            state = None # Just a guard

            # Our target is surely running
            copy_state.set_ready(target.subtask)
            # The currently running subtask has no saved continuations
            copy_state.set_continuations(target.subtask, [])

            # Idle subtask: reset to entry_abb, if we dispatch to
            # another subtask (user subtask
            idle = self.system_graph.idle_subtask
            if target.subtask != idle and not target.subtask.conf.is_isr:
                copy_state.set_continuation(idle, self.__entry_point(idle))

            not_taken = set(possible_blocks[:i])
            # We can wipe out all continuations that are not taken, if
            # a subtask has no possible continuations anymore, it is surely suspended
            for cont in not_taken:
                subtask = cont.subtask
                # For the own subtask we already know where we are
                if subtask == target.subtask:
                    continue
                copy_state.remove_continuation(subtask, cont)
                if len(copy_state.get_continuations(subtask)) == 0:
                    copy_state.set_suspended(subtask)
                    copy_state.set_continuation(subtask, self.__entry_point(subtask))
                    # print subtask, " cannot be running in ", target

            copy_state.current_abb = target
            # If the target is not in the idle loop, we reset the idle
            # loop, since it always starts from the beginning. But
            # only if the target is not an ISR2
            if not target.subtask or \
               (target.subtask != self.system_graph.idle_subtask \
                and not target.subtask.conf.is_isr):
                copy_state.set_continuation(self.system_graph.idle_subtask,
                                            self.__entry_point(self.system_graph.idle_subtask))

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
            yield (source, target, copy_state)

    def schedule(self, source, state):
        current_running = source.subtask
        # Find continuation with highest priority
        target = None
        prio = 0
        for subtask in state.get_unordered_subtasks():
            if state.is_surely_ready(subtask):
                cont = state.get_continuation(subtask)
                cont_prio = self.dynamic_priority(state, cont)
                if not target or cont_prio > prio:
                    prio = cont_prio
                    target = cont
            else:
                assert state.is_surely_suspended(subtask) or \
                    state.is_surely_waiting(subtask)
        # If the current task is not preemptable, we can just continue
        # on the local task graph or on ISR blocks
        if current_running and not current_running.conf.preemptable \
           and state.is_surely_ready(current_running):
            task_cont = state.get_continuation(current_running)
            # The non-preemptable task can only be preempted by an ISR
            if not target.subtask.conf.is_isr:
                target = task_cont

        # Dispatch!
        copy_state = state.copy()
        copy_state.current_abb = target
        # Clear the block this. This indicates that non-preemptable
        # tasks take the RES_SCHEDULER after being woken up again.
        copy_state.clear_block_list(target.subtask)
        # Reset the idle task
        idle = self.system_graph.idle_subtask
        if target.subtask != idle and not target.subtask.conf.is_isr:
            copy_state.set_continuation(idle, self.__entry_point(idle))
        copy_state.set_continuation(target.subtask, None)
        copy_state.frozen = True
        yield (source, target, copy_state)
