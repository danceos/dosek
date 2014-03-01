from generator.graph.Analysis import Analysis
from generator.graph.AtomicBasicBlock import E, S
from generator.tools import panic, select_distinct
from generator.graph.common import Edge
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

        ret = []
        if self.sse:
            ret.append(self.sse.name())
        if self.state_flow:
            ret.append(self.state_flow.name())
        assert ret, "At least one method for constructing a global flow information must be enabled"
        return ret

    def get_edge_filter(self):
        return set([E.state_flow, E.state_flow_irq, E.system_level])

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
                followup_abbs |= select_distinct(self.sse.states_next[state],
                                                 "current_abb")
            return followup_abbs
        return []


    def do(self):
        self.removed_edges = []
        for source_abb in self.system_graph.get_abbs():
            in_state_flow = set(self.edges_in_state_flow(source_abb))
            in_sse = set(self.edges_in_sse(source_abb))

            # Edges found by both analyses are always good
            for target_abb in in_state_flow & in_sse:
                source_abb.add_cfg_edge(target_abb, E.system_level)

            more_in_state_flow = in_state_flow - in_sse
            more_in_sse = in_sse - in_state_flow

            if self.sse:
                for target_abb in more_in_state_flow:
                    # Found in the dataflow analysis but not by the sse

                    # FIXME: Jumps from computation might be the result of
                    # sporadic actions, but those are not explicitly
                    # drawed in the RunningTaskGraph
                    if not source_abb.isA([S.kickoff, S.computation]):
                        edge = Edge(source_abb, target_abb)
                        logging.debug("  + saved edge from %s -> %s", source_abb, target_abb)
                        self.removed_edges.append(edge)

            for target_abb in more_in_sse:
                # Returns from or to interrupts are not part of the system_level flow
                if not source_abb.function.is_system_function and \
                   (bool(source_abb.function.subtask.is_isr) \
                    ^ bool(target_abb.function.subtask.is_isr)):
                    continue

                # There should not be more edges in the symbolic
                # execution, besides a few exceptions
                if self.state_flow:
                    panic("SSE has found more edges than RunningTask (%s -> %s)",
                          source_abb.path(), target_abb.path())
                else:
                    # If no state_flow analysis is done we use the
                    # edges build by symbolic execution
                    source_abb.add_cfg_edge(target_abb, E.system_level)

