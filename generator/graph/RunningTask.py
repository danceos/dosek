from generator.graph.common import *
from generator.graph.Analysis import *
from generator.graph.DynamicPriorityAnalysis import DynamicPriorityAnalysis
from generator.graph.Sporadic import SporadicEvent
from generator.graph.GlobalAbbInfo import GlobalAbbInfo
from generator.graph.SystemSemantic import *
from generator.tools import panic


class RunningTaskAnalysis(Analysis):
    def __init__(self):
        Analysis.__init__(self)
        self.sporadic_events = []
        self.isrs = []
        # A member for the RunningTask analysis
        self.running_task = None
        # States for the fixpoint iteration
        self.changed_current_block = False
        self.before_abb_states = None
        self.system_call_semantic = None
        self.fixpoint = None
        self.edge_states = None


    def requires(self):
        # We require all possible system edges to be contructed
        return [CurrentRunningSubtask.name(), DynamicPriorityAnalysis.name()]

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

        # We say that on the edge from one ABB to the other one, the
        # running abb is already the target
        state.current_abb = target
        self.edge_states[(source, target)] = state

    def install_sporadic_events(self):
        # Install the alarm handlers
        self.sporadic_events.extend(list(self.system.alarms))
        # Install the ISR handlers
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

        after_states = self.system_call_semantic.do_SystemCall(
            block, before,
            {'StartOS': self.system_call_semantic.do_StartOS,
             'ActivateTask': self.system_call_semantic.do_ActivateTask,
             'TerminateTask': self.system_call_semantic.do_TerminateTask,
             'ChainTask': self.system_call_semantic.do_ChainTask,
             'computation': self.do_computation_with_sporadic_events,
             'SetRelAlarm': self.system_call_semantic.do_computation, # ignore
             'CancelAlarm': self.system_call_semantic.do_computation, # ignore
             'GetResource': self.system_call_semantic.do_computation, # Done in DynamicPriorityAnalysis
             'ReleaseResource': self.system_call_semantic.do_computation, # Done in DynamicPriorityAnalysis
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

        # Fixup StartOS Node, otherwise usage of this pointer gets more complicated
        self.before_abb_states[entry_abb].current_abb = entry_abb

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
        """Return a GlobalAbbInformation object for this object"""
        if abb in self.before_abb_states:
            return RunningTaskGlobalAbbInformation(self, abb)


class ISR(SporadicEvent):
    def __init__(self, analysis, isr_handler):
        SporadicEvent.__init__(self, analysis.system, isr_handler.function_name)
        self.analysis = analysis
        self.system_call_semantic = self.analysis.system_call_semantic
        self.handler = isr_handler
        self.idle = self.system.functions["Idle"]
        self.collected_states = {}
        self.collected_edge_states = {}
        for abb in self.handler.abbs:
            self.collected_states[abb] = SystemState(self.system)


        # Variables for the fixpoint iterations
        self.changed_current_block = True
        self.result = None
        self.start_state = None
        self.edge_states = None
        self.before_abb_states = None
        self.fixpoint = None

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

        # We say that on the edge from one ABB to the other one, the
        # running abb is already the target
        state.current_abb = target

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
        
        # fixup current running abb for entry_abb
        self.before_abb_states[entry_abb].current_abb = entry_abb

        # Merge calculated before-block states into the merged states
        for abb in self.handler.abbs:
            self.collected_states[abb].merge_with(
                self.before_abb_states[abb]
                )

        # IRET
        self.result.set_suspended(self.handler)

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
        if len(self.abb.get_outgoing_edges('irq')) > 0:
            logging.warning("IRQs not yet supported!")
        edges = set(self.abb.get_outgoing_edges('global'))

        states = []
        for edge in edges:
            states.append(self.analysis.edge_states[(edge.source, edge.target)])
        return states

