from generator.graph.common import *
from generator.graph.Analysis import *
from generator.graph.DynamicPriorityAnalysis import DynamicPriorityAnalysis
from generator.graph.Sporadic import SporadicEvent
from generator.graph.GlobalAbbInfo import GlobalAbbInfo
from generator.graph.SystemSemantic import *
from generator.graph.AtomicBasicBlock import E


class SystemStateFlow(Analysis):
    """This pass lets the system state flow through the system. It should
       be faster than the symbolic execution, but lead to a more
       imprecise global cfg, since it merges states at function calls
       and join nodes.

    """
    pass_alias = "state-flow"

    def __init__(self):
        Analysis.__init__(self)
        self.sporadic_events = []
        self.isrs = []
        self.alarms = []
        # A member for the RunningTask analysis
        self.running_task = None
        # States for the fixpoint iteration
        self.before_abb_states = None
        self.edge_states = None
        self.system_call_semantic = None
        self.fixpoint = None

    def requires(self):
        # We require all possible system edges to be contructed
        return [DynamicPriorityAnalysis.name(), "InterruptControlAnalysis"]

    def get_edge_filter(self):
        return set([E.task_level, E.state_flow, E.state_flow_irq])

    @staticmethod
    def update_before_state(edge_states, before_state_dict, block, edge_type):
        input_abbs = block.get_incoming_nodes(edge_type)
        input_states = [edge_states[(source, block)] for source in input_abbs]
        before = SystemState.merge_many(block.system_graph, input_states)

        changed = False
        if not block in before_state_dict:
            assert not before.frozen
            before_state_dict[block] = before.copy()
            before_state_dict[block].freeze()
            changed = True
        else:
            before_state_dict[block].frozen = False
            changed = before_state_dict[block].merge_with(before)
            before_state_dict[block].frozen = True
            before = before_state_dict[block]

        return changed, before

    def set_state_on_edge(self, source, target, state):
        if not target in source.get_outgoing_nodes(E.state_flow):
            source.add_cfg_edge(target, E.state_flow)

        # We say that on the edge from one ABB to the other one, the
        # running abb is already the target
        state.current_abb = target
        if target in self.before_abb_states:
            self.before_abb_states[target].frozen = False
            changed = self.before_abb_states[target].merge_with(state)
        else:
            changed = True
            self.before_abb_states[target] = state
        self.before_abb_states[target].frozen = True
        if changed and not target in self.fixpoint:
            self.fixpoint.enqueue_later(item = target)

    def install_sporadic_events(self):
        # Install the alarm handlers
        for alarm in self.system_graph.alarms:
            wrapped_alarm = SSF_SporadicEvent(alarm, self.system_call_semantic)
            self.sporadic_events.append(wrapped_alarm)
            self.alarms.append(wrapped_alarm)

        # Install the ISR handlers
        for isr in self.system_graph.isrs:
            wrapped_isr = SSF_SporadicEvent(isr, self.system_call_semantic)
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

        before = self.before_abb_states[block]

        # If this block belongs to a task, it must the highest
        # available task for the input state. Otherwise we wouldn't
        # have been scheduled (or the current task is non-preemptable)
        scc = self.system_call_semantic

        after_states = scc.do_SystemCall(
            block, before,
            {S.StartOS         : scc.do_StartOS,
             S.ActivateTask    : scc.do_ActivateTask,
             S.TerminateTask   : scc.do_TerminateTask,
             S.ChainTask       : scc.do_ChainTask,
             S.computation     : self.do_computation_with_sporadic_events,
             S.kickoff         : scc.do_computation, # NO ISRS!
             S.SetRelAlarm     : scc.do_computation, # ignore
             S.CancelAlarm     : scc.do_computation, # ignore
             S.GetAlarm        : scc.do_computation, # ignore
             S.AdvanceCounter  : scc.do_AdvanceCounter,
             # Done in DynamicPriorityAnalysis
             S.GetResource     : scc.do_computation,
             S.ReleaseResource : scc.do_computation,
             # Done in InterruptControlAnalysis
             S.DisableAllInterrupts : scc.do_computation,
             S.EnableAllInterrupts  : scc.do_computation,
             S.SuspendAllInterrupts : scc.do_computation,
             S.ResumeAllInterrupts  : scc.do_computation,
             S.SuspendOSInterrupts  : scc.do_computation,
             S.ResumeOSInterrupts   : scc.do_computation,

             S.Idle            : scc.do_Idle})

        # Schedule depending on the possible output state
        for after in after_states:
            self.system_call_semantic.schedule(block, after, self.set_state_on_edge)

        self.debug("}}}")


    def do(self):
        old_copy_count = SystemState.copy_count

        self.running_task = self.get_analysis(CurrentRunningSubtask.name())
        # (ABB, ABB) -> SystemState
        self.edge_states = {}
        # ABB -> SystemState

        self.system_call_semantic = SystemCallSemantic(self.system_graph, self.running_task)

        self.install_sporadic_events()

        entry_abb = self.system_graph.functions["StartOS"].entry_abb
        entry_state = SystemState(self.system_graph)
        entry_state.current_abb = entry_abb
        entry_state.freeze()

        self.before_abb_states = {entry_abb: entry_state}

        self.fixpoint = FixpointIteration([entry_abb])
        self.fixpoint.do(self.block_functor)

        # Fixup StartOS Node, otherwise usage of this pointer gets more complicated
        self.before_abb_states[entry_abb].current_abb = entry_abb

        # Merge SporadicEvents
        for isr in self.sporadic_events:
            isr.fixup_before_states()
            if isinstance(isr.wrapped_event, Alarm):
                counter = self.system_graph.counters[isr.wrapped_event.counter]
                # Ignore softcounters
                if counter.softcounter:
                    continue
            for abb in isr.wrapped_event.handler.abbs:
                self.before_abb_states[abb] = isr.collected_states[abb]

    

        # Record the number of copied system states
        self.system_graph.stats.add_data(self, "copied-system-states",
                                         SystemState.copy_count - old_copy_count,
                                         scalar = True)
        logging.info(" + %d system states copied", SystemState.copy_count - old_copy_count)
        # Record the precision indicators for each abb
        # Count the number of ABBs in the system the analysis works on
        is_relevant = self.system_graph.passes["AddFunctionCalls"].is_relevant_function
        abbs = [x for x in self.system_graph.get_abbs() if is_relevant(x.function)]
        precisions = []
        for abb in abbs:
            # Only ABBs from Subtasks
            if not abb.function.subtask or not abb.function.subtask.is_real_thread():
                continue

            if abb in self.before_abb_states:
                precision = self.before_abb_states[abb].precision()
                if not abb.isA(S.StartOS):
                    self.stats.add_data(abb, "ssf-precision", precision, scalar=True)
                precisions.append(precision)
            else:
                # State will not be visited, for sure
                precisions.append(1.0)
        self.stats.add_data(self, "precision", precisions, scalar = True)

    ##
    ## Result getters for this analysis
    ##
    def reachable_subtasks_from_abb(self, abb):
        subtasks = set()
        for reached in abb.get_outgoing_nodes(E.state_flow):
            st = self.running_task.for_abb(reached)
            subtasks.add(st)
        return subtasks

    def activating_subtasks(self, subtask):
        subtasks = set()
        abbs = set()
        for reaching in subtask.entry_abb.get_incoming_nodes(E.state_flow):
            st = self.running_task.for_abb(reaching)
            if st == subtask:
                continue
            subtasks.add(st)
            abbs.add(reaching)
        return subtasks, abbs

    def for_abb(self, abb):
        """Return a GlobalAbbInformation object for this object"""
        if abb in self.before_abb_states:
            return SSF_GlobalAbbInformation(self, abb)

class SSF_SporadicEvent(SporadicEvent):
    def __init__(self, wrapped_event, system_call_semantic):
        SporadicEvent.__init__(self, wrapped_event.system_graph, \
                               wrapped_event.name, wrapped_event.task,
                               wrapped_event.handler)
        self.system_call_semantic = system_call_semantic
        self.wrapped_event = wrapped_event

        self.collected_states = {}
        # Initialize empty states for merging collected states into
        for abb in self.wrapped_event.handler.abbs:
            self.collected_states[abb] = SystemState(self.system_graph)

        # Variables for the fixpoint iterations
        self.result = None
        self.start_state = None
        self.edge_states = None
        self.before_abb_states = None
        self.fixpoint = None

        irq_entry_state = SystemState(self.system_graph)
        self.irq_exit_state = SystemState(self.system_graph)
        for subtask in self.system_graph.get_subtasks():
            irq_entry_state.set_suspended(subtask)
            irq_entry_state.set_continuation(subtask, subtask.entry_abb)

        irq_entry_state.set_ready(self.wrapped_event.handler)
        irq_entry_abb = self.wrapped_event.handler.entry_abb
        irq_entry_state.current_abb = irq_entry_abb

        self.edge_states = dict()
        self.before_abb_states = {irq_entry_abb: irq_entry_state}

        self.fixpoint = FixpointIteration([irq_entry_abb])
        self.fixpoint.do(self.block_functor)

        self.surely_activated = []
        self.maybe_activated = []
        self.in_state = SystemState(self.system_graph)
        for subtask in self.system_graph.get_subtasks():
            # Only Real Tasks
            if subtask.is_isr:
                continue
            if self.irq_exit_state.is_surely_ready(subtask):
                self.surely_activated.append(subtask)
            elif self.irq_exit_state.is_maybe_ready(subtask):
                self.maybe_activated.append(subtask)


    def can_trigger(self, state):
        return self.wrapped_event.can_trigger(state)

    def do_iret(self, block, before):
        # When there is no further local abb node, we have reached the
        # end of the interrupt handler
        self.irq_exit_state.merge_with(before)
        self.irq_exit_state.set_suspended(self.wrapped_event.handler)

        return []


    def block_functor(self, fixpoint, block):
        if block == self.wrapped_event.handler.entry_abb:
            self.changed_current_block = True
            before = self.before_abb_states[block]
        else:
            self.changed_current_block, before = \
                SystemStateFlow.update_before_state(self.edge_states,
                                                        self.before_abb_states,
                                                        block,
                                                        edge_type = E.state_flow_irq)

        after_states = self.system_call_semantic.do_SystemCall(
            block, before,
            {S.ActivateTask: self.system_call_semantic.do_ActivateTask,
             S.computation: self.system_call_semantic.do_computation,
             S.kickoff: self.system_call_semantic.do_computation,
             S.Idle: self.system_call_semantic.do_Idle,
             S.iret: self.do_iret})
        # Schedule depending on the possible output states
        for after in after_states:
            self.system_call_semantic.schedule(block, after, self.set_state_on_edge)

        # This has to be done after the system call handling, since
        # new irq links could have been introduced
        if self.changed_current_block:
            for node in block.get_outgoing_nodes(E.state_flow_irq):
                self.fixpoint.enqueue_soon(item = node)

        # Never leave the handler function here
        assert block.function.subtask == self.wrapped_event.handler.subtask

    def set_state_on_edge(self, source, target, state):
        if not target in source.get_outgoing_nodes(E.state_flow_irq):
            source.add_cfg_edge(target, E.state_flow_irq)
            self.changed_current_block = True

        # We say that on the edge from one ABB to the other one, the
        # running abb is already the target
        state.current_abb = target

        self.edge_states[(source, target)] = state

    def trigger(self, in_state):
        self.in_state.current_abb = in_state.current_abb
        self.in_state.merge_with(in_state, return_changed = False)
        current_subtask = in_state.current_subtask
        current_abb     = in_state.current_abb
        # We have also preempted this one
        self.in_state.add_continuation(current_subtask, current_abb)
        self.in_state.current_abb = None

        ret_state = in_state.copy()
        ret_state.set_continuation(current_subtask, current_abb)

        for subtask in self.surely_activated:
            # Task was surely activated by ISR
            ret_state.set_ready(subtask)
            # If the task is alreay surely running, we cannot add
            # the entry_abb
            if not ret_state.is_surely_ready(subtask):
                ret_state.add_continuation(subtask, subtask.entry_abb)
        for subtask in self.maybe_activated:
            # Task was maybe activated by ISR
            if not ret_state.is_surely_ready(subtask):
                ret_state.set_unsure(subtask)
                # If the task is alreay surely running, we cannot add
                # the entry_abb
                ret_state.add_continuation(subtask, subtask.entry_abb)

        return ret_state

    def fixup_before_states(self):
        for abb in self.wrapped_event.handler.abbs:
            self.in_state.current_abb = abb
            self.collected_states[abb].merge_with(self.in_state)

class SSF_GlobalAbbInformation(GlobalAbbInfo):
    def __init__(self, analysis, abb):
        GlobalAbbInfo.__init__(self)
        self.analysis = analysis
        self.abb      = abb
        assert self.analysis.valid, "SystemStateFlow is not valid"

    @property
    def state_before(self):
        return self.analysis.before_abb_states[self.abb]

    @property
    def states_after(self):
        """Returns a list of possible next system states"""
        edges = set(self.abb.get_outgoing_edges(E.state_flow))

        states = []
        for edge in edges:
            states.append(self.analysis.before_abb_states[edge.target])
        return states

    @property
    def abbs_before(self):
        return self.abb.get_incoming_nodes(E.state_flow)
