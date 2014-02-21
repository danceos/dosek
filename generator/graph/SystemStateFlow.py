from generator.graph.common import *
from generator.graph.Analysis import *
from generator.graph.DynamicPriorityAnalysis import DynamicPriorityAnalysis
from generator.graph.Sporadic import SporadicEvent, ISR
from generator.graph.GlobalAbbInfo import GlobalAbbInfo
from generator.graph.SystemSemantic import *
from generator.graph.AtomicBasicBlock import E
from generator.tools import panic


class SystemStateFlow(Analysis):
    def __init__(self):
        Analysis.__init__(self)
        self.sporadic_events = []
        self.isrs = []
        # A member for the RunningTask analysis
        self.running_task = None
        # States for the fixpoint iteration
        self.changed_current_block = False
        self.before_abb_states = None
        self.edge_states = None
        self.system_call_semantic = None
        self.fixpoint = None

    def requires(self):
        # We require all possible system edges to be contructed
        return [DynamicPriorityAnalysis.name()]

    @staticmethod
    def merge_inputs(edge_states, block, edge_type):
        input_abbs = block.get_incoming_nodes(edge_type)
        input_states = [edge_states[(source, block)]
                        for source in input_abbs]
        return SystemState.merge_many(block.system, input_states)

    @staticmethod
    def update_before_state(edge_states, before_state_dict, block, edge_type):
        before = SystemStateFlow.merge_inputs(edge_states, block, edge_type)
        changed = False
        if not block in before_state_dict:
            before_state_dict[block] = before
            changed = True
        else:
            changed = before_state_dict[block].merge_with(before)
        return changed, before

    def set_state_on_edge(self, source, target, state):
        if not target in source.get_outgoing_nodes(E.system_level):
            source.add_cfg_edge(target, E.system_level)
            self.changed_current_block = True

        # We say that on the edge from one ABB to the other one, the
        # running abb is already the target
        state.current_abb = target
        if (source, target) in self.edge_states:
            self.edge_states[(source, target)].frozen = False
            self.edge_states[(source, target)].merge_with(state)
            self.edge_states[(source, target)].frozen = True
        else:
            self.edge_states[(source, target)] = state

    def install_sporadic_events(self):
        # Install the alarm handlers
        for alarm in self.system.alarms:
            self.sporadic_events.append(RunningTask_Alarm(alarm))

        # Install the ISR handlers
        for isr in self.system.isrs:
            wrapped_isr = RunningTask_ISR(isr, self.system_call_semantic)
            self.sporadic_events.append(wrapped_isr)
            self.isrs.append(wrapped_isr)

    def do_computation_with_sporadic_events(self, block, before):
        after_states = self.system_call_semantic.do_computation(block, before)

        # Handle sporadic events
        for sporadic_event in self.sporadic_events:
            if not sporadic_event.can_trigger(before):
                continue
            after = sporadic_event.trigger(before)
            after_states.append(after)

        return after_states


    def block_functor(self, fixpoint, block):
        self.debug("{{{ " + str(block))

        self.changed_current_block, before = \
                self.update_before_state(self.edge_states,
                                         self.before_abb_states,
                                         block, E.system_level)

        # If this block belongs to a task, it must the highest
        # available task for the input state. Otherwise we wouldn't
        # have been scheduled (or the current task is non-preemptable)
        calling_task = self.running_task.for_abb(block)

        after_states = self.system_call_semantic.do_SystemCall(
            block, before,
            {'StartOS': self.system_call_semantic.do_StartOS,
             'ActivateTask': self.system_call_semantic.do_ActivateTask,
             'TerminateTask': self.system_call_semantic.do_TerminateTask,
             'ChainTask': self.system_call_semantic.do_ChainTask,
             'computation': self.do_computation_with_sporadic_events,
             'kickoff': self.system_call_semantic.do_computation, # NO ISRS!
             'SetRelAlarm': self.system_call_semantic.do_computation, # ignore
             'CancelAlarm': self.system_call_semantic.do_computation, # ignore
             'GetResource': self.system_call_semantic.do_computation, # Done in DynamicPriorityAnalysis
             'ReleaseResource': self.system_call_semantic.do_computation, # Done in DynamicPriorityAnalysis
             'Idle': self.system_call_semantic.do_Idle})
        # Merge all system call possibilities
        # after = SystemState.merge_many(self.system, after_states)

        # Schedule depending on the possible output state
        for after in after_states:
            self.system_call_semantic.schedule(block, after, self.set_state_on_edge)

        
        # This has to be done after the system call handling, since
        # new global links could have been introduced
        if self.changed_current_block:
            for node in block.get_outgoing_nodes(E.system_level):
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

        # Fixup StartOS Node, otherwise usage of this pointer gets more complicated
        self.before_abb_states[entry_abb].current_abb = entry_abb

        # Merge ISRs
        for isr in self.isrs:
            # Add IRQ edges from activating blocks
            # for triggered_in in isr.triggered_in_abb:
            #    triggered_in.add_cfg_edge(isr.handler.entry_abb, E.irq_level)
            for abb in isr.wrapped_isr.handler.abbs:
                self.before_abb_states[abb] = isr.collected_states[abb]
                #for edge in abb.get_outgoing_edges(E.irq_level):
                #   if edge.level == E.irq_level:
                #        edge.level = E.system_level

    ##
    ## Result getters for this analysis
    ##
    def reachable_subtasks_from_abb(self, abb):
        subtasks = set()
        for reached in abb.get_outgoing_nodes(E.system_level):
            st = self.running_task.for_abb(reached)
            subtasks.add(st)
        return subtasks

    def activating_subtasks(self, subtask):
        subtasks = set()
        abbs = set()
        for reaching in subtask.entry_abb.get_incoming_nodes(E.system_level):
            st = self.running_task.for_abb(reaching)
            if st == subtask:
                continue
            subtasks.add(st)
            abbs.add(reaching)
        return subtasks, abbs

    def for_abb(self, abb):
        """Return a GlobalAbbInformation object for this object"""
        if abb in self.before_abb_states:
            return RunningTaskGlobalAbbInformation(self, abb)

class RunningTask_Alarm(SporadicEvent):
    def __init__(self, wrapped_alarm):
        SporadicEvent.__init__(self, wrapped_alarm.system_graph, wrapped_alarm.name)
        self.wrapped_alarm = wrapped_alarm

    def can_trigger(self, state):
        return self.wrapped_alarm.can_trigger(state)

    def trigger(self, state):
        SporadicEvent.trigger(self, state)
        subtask = self.wrapped_alarm.subtask
        copy_state = state.copy()

        # Save current IP
        current_subtask = state.current_abb.function.subtask
        copy_state.set_continuation(current_subtask, state.current_abb)

        if not copy_state.is_surely_ready(subtask):
            copy_state.set_continuation(subtask, subtask.entry_abb)
        copy_state.set_ready(subtask)

        return copy_state


class RunningTask_ISR(SporadicEvent):
    def __init__(self, wrapped_isr, system_call_semantic):
        SporadicEvent.__init__(self, wrapped_isr.system_graph, wrapped_isr.name)
        self.system_call_semantic = system_call_semantic
        self.wrapped_isr = wrapped_isr

        self.collected_states = {}
        self.collected_edge_states = {}
        for abb in self.wrapped_isr.handler.abbs:
            self.collected_states[abb] = SystemState(self.system_graph)

        # Variables for the fixpoint iterations
        self.changed_current_block = True
        self.result = None
        self.start_state = None
        self.edge_states = None
        self.before_abb_states = None
        self.fixpoint = None

    def block_functor(self, fixpoint, block):
        if block == self.wrapped_isr.handler.entry_abb:
            self.changed_current_block = True
            before = self.start_state.copy()
            before.set_ready(self.wrapped_isr.handler)
            self.before_abb_states[block] = before
        else:
            self.changed_current_block, before = \
                SystemStateFlow.update_before_state(self.edge_states,
                                                        self.before_abb_states,
                                                        block,
                                                        edge_type = E.irq_level)

        after_states = self.system_call_semantic.do_SystemCall(
            block, before,
            {'ActivateTask': self.system_call_semantic.do_ActivateTask,
             'computation': self.system_call_semantic.do_computation,
             'kickoff': self.system_call_semantic.do_computation,
             'Idle': self.system_call_semantic.do_Idle,
             'iret': self.do_iret})
        # Schedule depending on the possible output states
        for after in after_states:
            self.system_call_semantic.schedule(block, after, self.set_state_on_edge)




        # This has to be done after the system call handling, since
        # new irq links could have been introduced
        if self.changed_current_block:
            for node in block.get_outgoing_nodes(E.irq_level):
                self.fixpoint.enqueue_soon(item = node)

        # Never leave the handler function here
        assert block.function.subtask == self.wrapped_isr.handler.subtask

    def do_iret(self, block, before):
        # When there is no further local abb node, we have reached the
        # end of the interrupt handler
        self.result.merge_with(before)
        return []


    def set_state_on_edge(self, source, target, state):

        if not target in source.get_outgoing_nodes(E.irq_level):
            source.add_cfg_edge(target, E.irq_level)
            self.changed_current_block = True

        # We say that on the edge from one ABB to the other one, the
        # running abb is already the target
        state.current_abb = target

        self.edge_states[(source, target)] = state

    def can_trigger(self, state):
        return self.wrapped_isr.can_trigger(state)

    def trigger(self, state):
        SporadicEvent.trigger(self, state)
        self.result = state.new()
        self.start_state = state
        entry_abb = self.wrapped_isr.handler.entry_abb

        # Save current IP
        current_subtask = state.current_abb.function.subtask
        state.set_continuation(current_subtask, state.current_abb)

        # Clean old IRQ edges
        for abb in self.wrapped_isr.handler.abbs:
            for edge in abb.get_outgoing_edges(E.irq_level):
                abb.remove_cfg_edge(edge.target, E.irq_level)

        self.edge_states = dict()
        self.before_abb_states = dict()

        self.fixpoint = FixpointIteraton([entry_abb])
        self.fixpoint.do(self.block_functor)
        
        # fixup current running abb for entry_abb
        self.before_abb_states[entry_abb].current_abb = entry_abb

        # Merge calculated before-block states into the merged states
        for abb in self.wrapped_isr.handler.abbs:
            self.collected_states[abb].merge_with(
                self.before_abb_states[abb]
                )

        # IRET
        self.result.set_suspended(self.wrapped_isr.handler)
        self.result.current_abb = state.current_abb

        return self.result


class RunningTaskGlobalAbbInformation(GlobalAbbInfo):
    def __init__(self, analysis, abb):
        GlobalAbbInfo.__init__(self)
        self.analysis = analysis
        self.abb      = abb
        assert self.analysis.valid, "Running Task Analysis is not valid"

    @property
    def state_before(self):
        return self.analysis.before_abb_states[self.abb]

    @property
    def states_after(self):
        """Returns a list of possible next system states"""
        if len(self.abb.get_outgoing_edges(E.irq_level)) > 0:
            logging.warning("IRQs not yet supported!")
        edges = set(self.abb.get_outgoing_edges(E.system_level))

        states = []
        for edge in edges:
            states.append(self.analysis.edge_states[(edge.source, edge.target)])
        return states

