from generator.graph.Analysis import Analysis
from generator.graph.AtomicBasicBlock import E, S
from generator.tools import panic, stack
from generator.graph.common import Edge
from generator.graph.SymbolicSystemExecution import StateTransition
import logging


class ConstructGlobalCFG(Analysis):
    """The global control flow graph contains all transitions that the
       real hardware can execute assisted by the operating
       system. This pass combines different sources of information to
       construct this global cfg.

    """
    def __init__(self):
        Analysis.__init__(self)
        self.removed_edges = None
        self.state_flow    = None
        self.sse           = None

    def requires(self):
        # We require all passes that are enqueued
        self.state_flow = self.system_graph.get_pass("SystemStateFlow",
                                               only_enqueued = True)
        self.sse        = self.system_graph.get_pass("SymbolicSystemExecution",
                                               only_enqueued = True)

        # Default is SSE
        if not self.sse and not self.state_flow:
            self.sse = self.system_graph.enqueue_analysis("SymbolicSystemExecution")

        ret = []
        if self.sse:
            ret.append(self.sse.name())
        if self.state_flow:
            ret.append(self.state_flow.name())
        assert ret, "At least one method for constructing a global flow information must be enabled"
        return ret

    def get_edge_filter(self):
        return set([E.state_flow, E.state_flow_irq, E.system_level, E.task_level])

    def global_abb_information_provider(self):
        self.requires()
        return self.sse or self.state_flow

    def edges_in_state_flow(self, source_abb):
        """Returns the system_level edges that were discoverd by the state
        flow analysis"""
        if self.state_flow:
            return source_abb.get_outgoing_nodes(E.state_flow) \
                + source_abb.get_outgoing_nodes(E.state_flow_irq)
        return []

    def edges_in_sse(self, source_abb):
        """Returns the system_level edges that were discoverd by the symbolic
        execution

        """
        if self.sse:
            followup_abbs    = set()
            if not source_abb in self.sse.states_by_abb:
                return []
            for state in self.sse.states_by_abb[source_abb]:
                for next_state in state.get_outgoing_nodes(StateTransition):
                    followup_abbs.add(next_state.current_abb)
            return followup_abbs
        return []


    def do(self):
        self.removed_edges = []
        edge_count_in_ssf = 0
        edge_count_in_sse = 0

        for source_abb in self.system_graph.get_abbs():
            in_state_flow = set(self.edges_in_state_flow(source_abb))
            in_sse = set(self.edges_in_sse(source_abb))
            edge_count_in_sse += len(in_sse)
            edge_count_in_ssf += len(in_state_flow)

            # Edges found by both analyses are always good
            for target_abb in in_state_flow & in_sse:
                source_abb.add_cfg_edge(target_abb, E.system_level)

            more_in_state_flow = in_state_flow - in_sse
            more_in_sse = in_sse - in_state_flow

            for target_abb in more_in_state_flow:
                # Found in the dataflow analysis but not by the sse

                if self.sse:
                    edge = Edge(source_abb, target_abb)
                    logging.debug(" + remove edge from %s -> %s", source_abb, target_abb)
                    self.removed_edges.append(edge)
                else:
                    # If no symbolic analysis is done we use the
                    # edges build by symbolic execution
                    source_abb.add_cfg_edge(target_abb, E.system_level)

            for target_abb in more_in_sse:
                # Returns from or to interrupts are not part of the system_level flow
                if source_abb.function.subtask and \
                   (bool(source_abb.function.subtask.is_isr) \
                    ^ bool(target_abb.function.subtask.is_isr)):
                    assert False, "Invalid application/ISR transition"

                # There should not be more edges in the symbolic
                # execution, besides a few exceptions
                if self.state_flow:
                    panic("SSE has found more edges than RunningTask (%s -> %s)",
                          source_abb.path(), target_abb.path())
                else:
                    # If no state_flow analysis is done we use the
                    # edges build by symbolic execution
                    source_abb.add_cfg_edge(target_abb, E.system_level)
        logging.info(" + removed %d edges", len(self.removed_edges))

        ################################################################
        # Statistics
        ################################################################

        # Count the number of ABBs in the system the analysis works on
        is_relevant = self.system_graph.passes["AddFunctionCalls"].is_relevant_function
        abbs = [x for x in self.system_graph.get_abbs() if is_relevant(x.function)]
        self.stats.add_data(self, "abb-count", len(abbs), scalar = True)

        # Record Edge Count
        self.stats.add_data(self, "sse-edges", edge_count_in_sse, scalar=True)
        self.stats.add_data(self, "ssf-edges", edge_count_in_ssf, scalar=True)

        # Record the number of (possible) from lower to higher priority subtask
        edge_count = 0
        for abb1 in abbs:
            for abb2 in abbs:
                if abb1 in abb2.get_outgoing_nodes(E.task_level) or \
                   (abb1.dynamic_priority and abb2.dynamic_priority and abb1.dynamic_priority > abb2.dynamic_priority):
                    # We would a preemption edge from abb2 to abb1, if there is no natural edge
                    edge_count += 1
        self.stats.add_data(self, "possible-priority-edges",
                                         edge_count, scalar = True)

        # Record the number of subtasks that can be reached
        subtask_count = 0
        for subtask in self.system_graph.get_subtasks():
            if subtask.is_real_thread() and \
               len(subtask.entry_abb.get_incoming_edges(E.system_level)) > 0:
                subtask_count += 1
        self.system_graph.stats.add_data(self, "subtask-count", subtask_count, scalar = True)

        # ISR Count
        self.stats.add_data(self, "isr-count", len(self.system_graph.isrs), scalar = True)

        # Describe the removed edges
        self.stats.add_data(self, "removed-edges", []) # empty List
        for edge in self.removed_edges:
            self.stats.add_data(self, "removed-edges",
                                (edge.source.syscall_type.name, edge.target.syscall_type.name))
