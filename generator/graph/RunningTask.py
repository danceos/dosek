from generator.graph.common import *
from generator.graph.Analysis import *

class SystemState:
    READY = 'RDY'
    SUSPENDED = 'SPD'


    def __init__(self, system):
        self.system = system
        self.states = {}
        self.continuations = {}
        # {Subtask -> set([STATES])
        for subtask in self.system.get_subtasks():
            self.states[subtask] = set()
            self.continuations[subtask] = set()

    def get_subtasks(self):
        """Sorted by priority"""
        return sorted(self.system.get_subtasks(),
                      key=lambda x: x.static_priority, reverse = True)

    def get_task_states(self, subtask):
        return self.states[subtask]

    def set_unknown(self, subtask):
        self.states[subtask] = set()

    def set_suspended(self, subtask):
        self.states[subtask] = set([self.SUSPENDED])

    def set_ready(self, subtask):
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
        self.continuations[subtask] = set([abb])

    def set_continuations(self, subtask, abbs):
        self.continuations[subtask] = set(abbs)

    def merge_with(self, other):
        """Returns a newly created state that is the result of the merge of
           self and the other state"""
        for subtask in self.get_subtasks():
            self.states[subtask] |= other.states[subtask]
            self.continuations[subtask] |= other.continuations[subtask]

    def equal_to(self, other):
        for subtask in self.get_subtasks():
            if len(self.states[subtask] ^ other.states[subtask]) != 0:
                return False
            if len(self.continuations[subtask] ^ other.continuations[subtask]) != 0:
                return False
        return True

    def copy(self):
        state = SystemState(self.system)
        for subtask in state.get_subtasks():
            state.states[subtask] = self.states[subtask].copy()
            state.continuations[subtask] = self.continuations[subtask].copy()
        return state

    def __repr__(self):
        ret = "<SystemState>\n"
        for subtask in self.get_subtasks():
            ret += "  %s: %s in %s\n" %(subtask, self.states[subtask],
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
        return state

    def do_StartOS(self):
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

    def dispatch(self, state, source, subtask):
        for target in state.get_continuations(subtask):
            copy = state.copy()
            copy.set_continuation(subtask, target)

            if not target in source.get_outgoing_nodes('global'):
                source.add_cfg_edge(target, 'global')
                self.states[(source, target)] = copy
            else:
                self.states[(source, target)].merge_with(state)
            self.fixpoint.enqueue_soon(item = target)

    def find_possible_tasks(self, state):
        # We get the subtask in the order of their priority
        for subtask in state.get_subtasks():
            if state.is_surely_ready(subtask):
                return [subtask]
            elif state.is_surely_suspended(subtask):
                continue
            else:
                # There is one undecided task
                # -> Return all possibly running tasks
                return [x for x in state.get_subtasks()
                        if state.is_maybe_ready(x)]

    def schedule(self, block, state):
        for subtask in self.find_possible_tasks(state):
            self.dispatch(state, block, subtask)

    def block_functor(self, fixpoint, block):
        before = self.merge_inputs(block)
        if block.type == 'StartOS':
            after = self.do_StartOS()
            self.schedule(block, after)
        elif block.type == 'ActivateTask':
            after = before.copy()
            after.set_continuations(self.running_task.for_abb(block),
                                    block.get_outgoing_nodes('local'))
            after.set_ready(block.arguments[0])
            self.schedule(block, after)
        elif block.type == 'TerminateTask':
            after = before.copy()
            calling_task = self.running_task.for_abb(block)
            after.set_continuation(calling_task,
                                   calling_task.entry_abb)
            after.set_suspended(calling_task)
            self.schedule(block, after)

        elif block.type == 'computation':
            after = before.copy()
            after.set_continuations(self.running_task.for_abb(block),
                                    block.get_outgoing_nodes('local'))
            self.schedule(block, after)

    def do(self):
        self.running_task = self.get_analysis(CurrentRunningSubtask.name())
        # (ABB, ABB) -> SystemState
        self.states = {}

        entry_abb = self.system.functions["StartOS"].entry_abb
        self.fixpoint = FixpointIteraton([entry_abb])
        self.fixpoint.do(self.block_functor)
