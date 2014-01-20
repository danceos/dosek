from generator.graph.common import *
from generator.graph.Analysis import *

class SystemState:
    READY = 'RDY'
    SUSPENDED = 'SPD'

    def __init__(self, system):
        self.system = system
        self.frozen = False
        self.states = {}
        self.continuations = {}
        # {Subtask -> set([STATES])
        for subtask in self.system.get_subtasks():
            self.states[subtask] = set()
            self.continuations[subtask] = set()

    def new(self):
        return SystemState(self.system)

    def copy(self):
        state = SystemState(self.system)
        for subtask in state.get_subtasks():
            state.states[subtask] = self.states[subtask].copy()
            state.continuations[subtask] = self.continuations[subtask].copy()
        return state

    def get_subtasks(self):
        """Sorted by priority"""
        return sorted(self.system.get_subtasks(),
                      key=lambda x: x.static_priority, reverse = True)

    def get_task_states(self, subtask):
        return self.states[subtask]

    def set_unknown(self, subtask):
        assert not self.frozen
        self.states[subtask] = set()

    def set_suspended(self, subtask):
        # When a subtask is surely suspendend, we know that it can't
        # be somewhere in its execution
        assert not self.frozen
        self.set_continuation(subtask, subtask.entry_abb)
        self.states[subtask] = set([self.SUSPENDED])

    def set_ready(self, subtask):
        assert not self.frozen
        self.states[subtask] = set([self.READY])

    def is_surely_suspended(self, subtask):
        return self.states[subtask] == set([self.SUSPENDED])

    def is_surely_ready(self, subtask):
        return self.states[subtask] == set([self.READY])

    def is_maybe_ready(self, subtask):
        return self.READY in self.states[subtask]

    def get_continuations(self, subtask):
        return self.continuations[subtask]

    def set_continuation(self, subtask, abb):
        assert not self.frozen
        self.continuations[subtask] = set([abb])

    def set_continuations(self, subtask, abbs):
        assert not self.frozen
        self.continuations[subtask] = set(abbs)

    def freeze(self):
        self.frozen = True

    def merge_with(self, other):
        """Returns a newly created state that is the result of the merge of
           self and the other state"""
        assert not self.frozen
        changed = False
        for subtask in self.get_subtasks():
            state_count = len(self.states[subtask])
            continuations_count = len(self.continuations[subtask])
            self.states[subtask] |= other.states[subtask]
            self.continuations[subtask] |= other.continuations[subtask]
            # Check whether one set has changed
            if len(self.states[subtask]) != state_count \
               or len(self.continuations[subtask]) != continuations_count:
                changed = True
        return changed

    def equal_to(self, other):
        for subtask in self.get_subtasks():
            if not(self.states[subtask] == other.states[subtask]):
                return False
            if not(self.continuations[subtask] == other.continuations[subtask]):
                return False
        return True

    def __repr__(self):
        ret = "<SystemState>\n"
        for subtask in self.get_subtasks():
            ret += "  %02x%02x %s: %s in %s \n" %(
                id(self.states[subtask]) % 256,
                id(self.continuations[subtask]) % 256,
                subtask, self.states[subtask],
                self.continuations[subtask])
        ret += "</SystemState>\n"
        return ret


class RunningTaskAnalysis(Analysis):
    def __init__(self):
        Analysis.__init__(self)
    def requires(self):
        # We require all possible system edges to be contructed
        return [CurrentRunningSubtask.name()]

    def merge_inputs(self, block):
        state = SystemState(self.system)
        for source in block.get_incoming_nodes('global'):
            state.merge_with(self.states[(source, block)])
        # The currently task is surely the highest task!
        #current_running = self.running_task.for_abb(block)
        #if current_running:
        #    state.set_ready(current_running)
        #    for x in state.get_subtasks():
        #        if x == current_running:
        #            break
        #        assert state.is_surely_suspended(x)
        return state

    def do_StartOS(self, block, before):
        state = SystemState(self.system)
        # In the StartOS node all tasks are suspended before,
        # and afterwards the idle loop and the autostarted
        # tasks are ready
        for subtask in self.system.get_subtasks():
            if subtask.autostart:
                state.set_ready(subtask)
            else:
                state.set_suspended(subtask)
            state.set_continuation(subtask, subtask.entry_abb)
        return state

    def do_ActivateTask(self, block, before):
        after = before.copy()
        after.set_continuations(self.running_task.for_abb(block),
                                block.get_outgoing_nodes('local'))
        after.set_ready(block.arguments[0])
        return after

    def do_TerminateTask(self, block, before):
        calling_task = self.running_task.for_abb(block)
        after = before.copy()
        after.set_suspended(calling_task)
        return after

    def do_ChainTask(self, block, before):
        after = before.copy()
        # Suspend the current Task, this also sets the
        # continuations correctly
        calling_task = self.running_task.for_abb(block)
        after.set_suspended(calling_task)
        # Activate other Task
        after.set_ready(block.arguments[0])
        return after

    def do_Idle(self, block, before):
        after = before.copy()
        after.set_continuations(self.running_task.for_abb(block),
                                block.get_outgoing_nodes('local'))
        return after

    def do_computation(self, block, before):
        after = before.copy()
        after.set_continuations(self.running_task.for_abb(block),
                                block.get_outgoing_nodes('local'))
        # Handle sporadic events
        for sporadic_event in self.system.sporadic_events:
            sporadic_event.manipulate_state(block, after)

        return after

    def dispatch(self, state, source, subtask, prune_higher_tasks = True):
        # We want to dispatch surely to the subtask
        # Additional knowledge: we ARE the highest task
        for target in state.get_continuations(subtask):
            copy = state.copy()
            copy.set_continuation(subtask, target)
            changed = True
            # Set all higher priority subtask to Suspended
            # -> cont = entry_block
            if prune_higher_tasks:
                for st in copy.get_subtasks():
                    if st == subtask:
                        break
                    copy.set_suspended(st)
            # When surely know that we are running
            copy.set_ready(subtask)

            if not target in source.get_outgoing_nodes('global'):
                source.add_cfg_edge(target, 'global')
                self.changed_current_block = True

            self.states[(source, target)] = copy

            self.debug("Dispatch to (%s -> %s)" % (source, target))
            self.debug(str(self.states[(source, target)]))

    def find_possible_tasks(self, state):
        # We get the subtask in the order of their priority
        subtasks = []
        for subtask in state.get_subtasks():
            if state.is_surely_ready(subtask):
                subtasks.append(subtask)
                break
            elif state.is_surely_suspended(subtask):
                continue
            elif state.is_maybe_ready(subtask):
                subtasks.append(subtask)
        return subtasks

    def schedule(self, block, state):
        current_running = self.running_task.for_abb(block)
        # If current_running task is not running, just dispatch back
        # to it again
        if current_running and not current_running.preemptable \
           and state.is_surely_ready(current_running):
            # Do not schedule, just return to current block
            self.dispatch(state, block, current_running,
                          prune_higher_tasks = False)
            return

        for subtask in self.find_possible_tasks(state):
            self.dispatch(state, block, subtask)

    def block_functor(self, fixpoint, block):
        self.debug("{{{ " + str(block))
        before = self.merge_inputs(block)
        after = None
        self.changed_current_block = False
        if not block in self.before_abb_states:
            self.before_abb_states[block] = before
            self.changed_current_block = True
        else:
            self.changed_current_block = self.before_abb_states[block].merge_with(before)

        # If this block belongs to a task, it must the highest
        # available task for the input state. Otherwise we wouldn't
        # have been scheduled (or the current task is non-preemptable)
        calling_task = self.running_task.for_abb(block)
        if calling_task:
            tasks = self.find_possible_tasks(before)
            # Task should be schedulable
            if calling_task.preemptable:
                assert len(tasks) == 1 and tasks[0] == calling_task

        if block.type == 'StartOS':
            after = self.do_StartOS(block, before)
            after.freeze()
            self.schedule(block, after)
        elif block.type == 'ActivateTask':
            after = self.do_ActivateTask(block, before)
            after.freeze()
            self.schedule(block, after)
        elif block.type == 'TerminateTask':
            after = self.do_TerminateTask(block, before)
            after.freeze()
            self.schedule(block, after)
        elif block.type == 'ChainTask':
            after = self.do_ChainTask(block, before)
            after.freeze()
            self.schedule(block, after)
        elif block.type == 'computation':
            after = self.do_computation(block, before)
            self.schedule(block, after)
        elif block.type == 'Idle':
            after = self.do_Idle(block, before)
            self.schedule(block, after)
        else:
            self.panic("BlockType %s is not supported yet"%block.type)

        # This has to be done after the system call handling, since
        # new global links could have been introduced
        if self.changed_current_block:
            for node in block.get_outgoing_nodes('global'):
                self.fixpoint.enqueue_soon(item = node)
        self.debug("}}}")

    def do(self):
        self.running_task = self.get_analysis(CurrentRunningSubtask.name())
        # (ABB, ABB) -> SystemState
        self.states = {}
        # ABB -> SystemState
        self.before_abb_states = {}

        entry_abb = self.system.functions["StartOS"].entry_abb
        self.fixpoint = FixpointIteraton([entry_abb])
        self.fixpoint.do(self.block_functor)

    def reachable_subtasks_from_abb(self, abb):
        subtasks = set()
        for reached in abb.get_outgoing_nodes('global'):
            st = self.running_task.for_abb(reached)
            subtasks.add(st)
        return subtasks

    def activated_by(self, subtask):
        subtasks = set()
        for reaching in subtask.entry_abb.get_incoming_nodes('global'):
            st = self.running_task.for_abb(reaching)
            subtasks.add(st)
        return subtasks

