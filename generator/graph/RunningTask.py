from generator.graph.common import *
from generator.graph.Analysis import *
from generator.graph.Sporadic import SporadicEvent


class SystemCallSemantic:
    def __init__(self, system, running_task):
        self.running_task = running_task
        self.system = system

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
        return [state]

    def do_ActivateTask(self, block, before):
        after = before.copy()
        # EnsureComputationBlocks ensures that after an activate task
        # only one ABB can be located
        cont = block.definite_after('local')
        after.set_continuation(self.running_task.for_abb(block),
                               cont)
        after.set_ready(block.arguments[0])
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
        after.set_ready(block.arguments[0])
        return [after]

    def do_Idle(self, block, before):
        after = before.copy()
        # EnsureComputationBlocks ensures that after the Idle() function
        # only one ABB can be located
        cont = block.definite_after('local')
        after.set_continuation(self.running_task.for_abb(block),
                               cont)
        return [after]

    def do_computation(self, block, before):
        ret = []
        calling_task = self.running_task.for_abb(block)
        for next_abb in block.get_outgoing_nodes('local'):
            after = before.copy()
            after.set_continuation(calling_task, next_abb)
            ret.append(after)
        return ret

    def do_SystemCall(self, block, before, system_calls):
        if block.type in system_calls:
            after = system_calls[block.type](block, before)
            for x in after:
                x.freeze()
            return after
        else:
            self.panic("BlockType %s is not supported yet"%block.type)

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

    def dispatch(self, state, source, target, set_state_on_edge, prune_higher_tasks = True):
        # Where are we going to
        subtask = self.running_task.for_abb(target)

        # Set all higher priority subtask to Suspended
        # -> cont = entry_block
        if prune_higher_tasks:
            for st in state.get_subtasks():
                if st == subtask:
                    break
                state.set_suspended(st)
        # When surely know that we are running
        state.set_ready(subtask)

        set_state_on_edge(source, target, state)

    def schedule(self, block, state, set_state_on_edge):
        current_running = self.running_task.for_abb(block)
        # If current_running task is not running, just dispatch back
        # to it again
        if current_running and not current_running.preemptable \
           and state.is_surely_ready(current_running):
            # Do not schedule, just return to current block
            for target in state.get_continuations(current_running):
                copy_state = state.copy()
                copy_state.set_continuation(current_running, target)

                self.dispatch(copy_state, block, target,
                              set_state_on_edge,
                              prune_higher_tasks = False)
            return

        for subtask in self.find_possible_tasks(state):
            for target in state.get_continuations(subtask):
                copy_state = state.copy()
                copy_state.set_continuation(subtask, target)

                self.dispatch(copy_state, block, target, set_state_on_edge)



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

    def set_suspended(self, subtask):
        assert not self.frozen
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

    def is_unsure_ready_state(self, subtask):
        return len(self.states[subtask]) > 1

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

    @staticmethod
    def merge_many(system, states):
        state = SystemState(system)
        for x in states:
            state.merge_with(x)
        return state

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

    @staticmethod
    def merge_inputs(edge_states, block, edge_type = 'global'):
        input_abbs = block.get_incoming_nodes(edge_type)
        input_states = [edge_states[(source, block)]
                        for source in input_abbs]
        return SystemState.merge_many(block.system, input_states)

    @staticmethod
    def update_before_state(edge_states, before_state_dict, block, edge_type = 'global'):
        before = RunningTaskAnalysis.merge_inputs(edge_states, block, edge_type)
        changed = False
        if not block in before_state_dict:
            before_state_dict[block] = before
            changed = True
        else:
            changed = before_state_dict[block].merge_with(before)
        return changed, before

    def set_state_on_edge(self, source, target, state):
        if not target in source.get_outgoing_nodes('global'):
            source.add_cfg_edge(target, 'global')
            self.changed_current_block = True

        self.edge_states[(source, target)] = state

    def install_sporadic_events(self):
        # Install the alarm handlers
        self.sporadic_events = list(self.system.alarms)
        # Install the ISR handlers
        self.isrs = []
        for subtask in self.system.get_subtasks():
            if subtask.is_isr:
                isr = ISR(self, subtask)
                self.sporadic_events.append(isr)
                self.isrs.append(isr)

    def do_computation_with_sporadic_events(self, block, before):
        after_states = self.system_call_semantic.do_computation(block, before)

        # Handle sporadic events
        for sporadic_event in self.sporadic_events:
            after = sporadic_event.trigger(block, before)
            after.set_continuations(self.running_task.for_abb(block),
                                    block.get_outgoing_nodes('local'))

            after_states.append(after)

        return after_states


    def block_functor(self, fixpoint, block):
        self.debug("{{{ " + str(block))

        self.changed_current_block, before = \
                self.update_before_state(self.edge_states,
                                         self.before_abb_states,
                                         block)

        # If this block belongs to a task, it must the highest
        # available task for the input state. Otherwise we wouldn't
        # have been scheduled (or the current task is non-preemptable)
        calling_task = self.running_task.for_abb(block)
        if calling_task and calling_task.preemptable:
            tasks = self.system_call_semantic.find_possible_tasks(before)
            # Task should be schedulable
            assert len(tasks) == 1 and tasks[0] == calling_task

        after_states = self.system_call_semantic.do_SystemCall(
            block, before,
            {'StartOS': self.system_call_semantic.do_StartOS,
             'ActivateTask': self.system_call_semantic.do_ActivateTask,
             'TerminateTask': self.system_call_semantic.do_TerminateTask,
             'ChainTask': self.system_call_semantic.do_ChainTask,
             'computation': self.do_computation_with_sporadic_events,
             'Idle': self.system_call_semantic.do_Idle})
        # Merge all system call possibilities
        after = SystemState.merge_many(self.system, after_states)
        # Schedule depending on the possible output state
        self.system_call_semantic.schedule(block, after, self.set_state_on_edge)


        # This has to be done after the system call handling, since
        # new global links could have been introduced
        if self.changed_current_block:
            for node in block.get_outgoing_nodes('global'):
                self.fixpoint.enqueue_soon(item = node)
        self.debug("}}}")


    def do(self):
        self.running_task = self.get_analysis(CurrentRunningSubtask.name())
        # (ABB, ABB) -> SystemState
        self.edge_states = {}
        # ABB -> SystemState
        self.before_abb_states = {}

        self.system_call_semantic = SystemCallSemantic(self.system, self.running_task)

        self.install_sporadic_events()

        entry_abb = self.system.functions["StartOS"].entry_abb
        self.fixpoint = FixpointIteraton([entry_abb])
        self.fixpoint.do(self.block_functor)

        # Delete this information
        self.edge_states = None

        # Merge ISRs
        for isr in self.isrs:
            # Add IRQ edges from activating blocks
            # for triggered_in in isr.triggered_in_abb:
            #    triggered_in.add_cfg_edge(isr.handler.entry_abb, 'irq')
            for abb in isr.handler.abbs:
                self.before_abb_states[abb] = isr.collected_states[abb]

    ##
    ## Result getters for this analysis
    ##
    def reachable_subtasks_from_abb(self, abb):
        subtasks = set()
        for reached in abb.get_outgoing_nodes('global'):
            st = self.running_task.for_abb(reached)
            subtasks.add(st)
        return subtasks

    def activating_subtasks(self, subtask):
        subtasks = set()
        abbs = set()
        for reaching in subtask.entry_abb.get_incoming_nodes('global'):
            st = self.running_task.for_abb(reaching)
            subtasks.add(st)
            abbs.add(reaching)
        return subtasks, abbs

    def for_abb(self, abb):
        return self.before_abb_states[abb]


class ISR(SporadicEvent):
    def __init__(self, analysis, isr_handler):
        SporadicEvent.__init__(self, analysis.system, isr_handler.function_name)
        self.analysis = analysis
        self.system_call_semantic = self.analysis.system_call_semantic
        self.handler = isr_handler
        self.idle = self.system.functions["Idle"]
        self.collected_states = {}
        for abb in self.handler.abbs:
            self.collected_states[abb] = SystemState(self.system)

    def block_functor(self, fixpoint, block):
        if block == self.handler.entry_abb:
            self.changed_current_block = True
            before = self.start_state.copy()
            before.set_ready(self.handler)
            self.before_abb_states[block] = before
        else:
            self.changed_current_block, before = \
                self.analysis.update_before_state(self.edge_states,
                                                  self.before_abb_states,
                                                  block,
                                                  edge_type = 'irq')

        after_states = self.system_call_semantic.do_SystemCall(
            block, before,
            {'ActivateTask': self.system_call_semantic.do_ActivateTask,
             'computation': self.system_call_semantic.do_computation,
             'Idle': self.system_call_semantic.do_Idle})
        # Schedule depending on the possible output states
        for after in after_states:
            self.system_call_semantic.schedule(block, after, self.set_state_on_edge)

        if len(block.get_outgoing_edges('local')) == 0:
            assert len(after_states) == 0
            assert block.type == 'computation'
            self.result.merge_with(before)


        # This has to be done after the system call handling, since
        # new irq links could have been introduced
        if self.changed_current_block:
            for node in block.get_outgoing_nodes('irq'):
                self.fixpoint.enqueue_soon(item = node)

        assert block.function in (self.handler, self.idle)


    def set_state_on_edge(self, source, target, state):

        if not target in source.get_outgoing_nodes('irq'):
            source.add_cfg_edge(target, 'irq')
            self.changed_current_block = True

        self.edge_states[(source, target)] = state

    def trigger(self, block, state):
        SporadicEvent.trigger(self, block, state)
        self.result = state.new()
        self.start_state = state
        entry_abb = self.handler.entry_abb

        # Clean old IRQ edges
        for abb in self.handler.abbs:
            for edge in abb.get_outgoing_edges('irq'):
                abb.remove_cfg_edge(edge.target, 'irq')

        self.edge_states = dict()
        self.before_abb_states = dict()

        self.fixpoint = FixpointIteraton([entry_abb])
        self.fixpoint.do(self.block_functor)

        # Merge calculated before-block states into the merged states
        for abb in self.handler.abbs:
            self.collected_states[abb].merge_with(
                self.before_abb_states[abb]
                )

        # IRET
        self.result.set_suspended(self.handler)

        return self.result


class GlobalControlFlowMetric(Analysis):
    def __init__(self, filename):
        Analysis.__init__(self)
        self.filename = filename
    def requires(self):
        # We require all possible system edges to be contructed
        return ["CurrentRunningSubtask", RunningTaskAnalysis.name()]

    def do(self):
        current_task = self.get_analysis("CurrentRunningSubtask")

        abbs = self.system.get_abbs()
        abb_count = len(abbs)
        # All possible directed edges
        all_possible_neighbours_count = 0
        # All edges that go to higher priority blocks or the system blocks
        higher_priority_count = 0
        # Analysed Edges
        analyzed_edges_count = 0
        for source in abbs:
            for target in abbs:
                if source == target:
                    continue
                abb0 = current_task.for_abb(source)
                abb1 = current_task.for_abb(target)
                # System blocks are lost
                if abb0 == None or abb1 == None:
                    continue
                all_possible_neighbours_count += 1
                if abb1.static_priority >= abb0.static_priority:
                    higher_priority_count +=1
                if target in source.get_outgoing_nodes('global'):
                    analyzed_edges_count += 1

        with open(self.filename, "w+") as fd:
            fd.write("%s, %d, %d, %d\n" %( 
                self.filename,
                all_possible_neighbours_count,
                higher_priority_count,
                analyzed_edges_count))


