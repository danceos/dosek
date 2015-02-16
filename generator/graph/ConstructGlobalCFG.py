from generator.graph.Analysis import Analysis
from generator.graph.AtomicBasicBlock import E, S
from generator.tools import panic, stack
from generator.graph.common import Edge
from generator.graph.SymbolicSystemExecution import StateTransition, SavedStateTransition
import logging


class ConstructGlobalCFG(Analysis):
    """The global control flow graph contains all transitions that the
       real hardware can execute assisted by the operating
       system. This pass combines different sources of information to
       construct this global cfg.

    """

    pass_alias = "gcfg"

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

    def edges_in_sse(self, source_abb, edge_type = StateTransition):
        """Returns the system_level edges that were discoverd by the symbolic
        execution

        """
        if self.sse:
            followup_abbs    = set()
            if not source_abb in self.sse.states_by_abb:
                return []
            for state in self.sse.states_by_abb[source_abb]:
                for next_state in state.get_outgoing_nodes(edge_type):
                    followup_abbs.add(next_state.current_abb)
            return followup_abbs
        return []


    def do(self):
        self.removed_edges = []
        edge_count_in_ssf = 0
        edge_count_in_sse = 0

        for source_abb in self.system_graph.abbs:
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
                   (bool(source_abb.subtask.conf.is_isr) \
                    ^ bool(target_abb.subtask.conf.is_isr)):
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

        self.edge_count_in_ssf = edge_count_in_ssf
        self.edge_count_in_sse = edge_count_in_sse

        logging.info(" + removed %d edges", len(self.removed_edges))


    def statistics(self):
        ################################################################
        # Statistics
        ################################################################

        # Count the number of ABBs in the system the analysis works on
        is_relevant = self.system_graph.passes["AddFunctionCalls"].is_relevant_function

        # In Statistic section, we want to generate data for the
        # following problem: How much better does the GCFG, which is
        # context sensitive, compare to a graph that is not context
        # sensitive? There are three different types of Graphs that we
        # could construct easily:
        #
        #  a) Full: The graph that has no information about the application
        #     structure. The control flow could jump from every from
        #     every block to every other block (including itself).
        #
        #  b) structure: We have only the application structure, but no
        #     information about the system's configuration.
        #
        #  c) OIL: We have the priorities of the tasks, we can only
        #     jump "upwards". For this we can use the static or the
        #     dynamic priorities. Task-Group annotations are also
        #     handled here.
        #
        #  d) SSE: The edges the symbolic system executution has for the GCFG graph
        #     (without the ISR cutting)

        # Record the number of (possible) from lower to higher priority subtask
        edges = {
            "full": 0,
            "structure": 0,
            "oil-static": 0,
            "sse-uncut": 0,
            "ssf-uncut": 0,
            "sse-cut":   self.edge_count_in_sse,
            "ssf-cut":   self.edge_count_in_ssf,
        }

        abbs = [x for x in self.system_graph.abbs if is_relevant(x.function)]


        # How many sporadic sources exist in the system
        isr_count = len(list(self.system_graph.isrs)+list(self.system_graph.alarms))

        # We have blocks that do not belong to a subtask (StartOS)
        # and we have blocks that are unreachable
        natural_blocks = [x for x in abbs if x.subtask \
                          and x.get_incoming_edges(E.system_level)]
        self.stats.add_data(self, "abb-count", len(natural_blocks), scalar = True)

        # how many computation blocks are there:
        computation_blocks = [x for x in natural_blocks if x.isA(S.computation)]
        kickoff_blocks     = [x for x in natural_blocks if x.isA(S.kickoff) and x.subtask.is_real_thread()]

        for abb1 in natural_blocks:
            # Full: every block can jump to every other block
            edges["full"] += (len(natural_blocks))

            # structure:
            # - computation blocks:
            #   - proceed to ICFG successor
            #   - every ISR entry method
            # - syscalls:
            #   - every other computation block
            #   - every kickoff

            if abb1.isA(S.computation):
                edges["structure"] += len(abb1.get_outgoing_nodes(E.task_level))
                edges["structure"] += isr_count
            else: # Syscall
                edges["structure"] += len(computation_blocks)
                edges["structure"] += len(kickoff_blocks)

            # oil-static:
            # - computation blocks:
            #   - proceed to ICFG successor
            #   - activatable IRQs
            # - terminating system calls:
            #   - Computation and kickoff blocks of all other tasks
            # - non-terminating system calls
            #   - every other computation block (with higher priority)
            #   - every kickoff  (with higher priority)
            if abb1.isA(S.computation):
                edges["oil-static"] += len(abb1.get_outgoing_nodes(E.task_level))
                edges["oil-static"] += abb1.sporadic_trigger_count
            elif abb1.syscall_type.doesTerminateTask(): # Terminating syscall
                edges["oil-static"] += len([x for x in computation_blocks + kickoff_blocks
                                            if x.subtask.static_priority != abb1.subtask.static_priority])
            else:
                edges["oil-static"] += len(abb1.get_outgoing_nodes(E.task_level))
                edges["oil-static"] += len([x for x in computation_blocks + kickoff_blocks
                                            if x.subtask.static_priority > abb1.subtask.static_priority])
            # ssf-uncut
            # - computation blocks:
            #   - proceed to ICFG successor
            #   - every ISR entry method
            # - iret blocks:
            #   - Return to every computation block
            # - syscalls:
            #   - every other computation block
            #   - every kickoff

            if self.state_flow:
                if abb1.isA(S.computation):
                    # Interrupt activation
                    edges["ssf-uncut"] += abb1.sporadic_trigger_count
                # GCFG Edges (irq and non-irq)
                edges["ssf-uncut"] += len(self.edges_in_state_flow(abb1))

            if self.sse:
                # SSE-uncut
                edges["sse-uncut"] += len(self.edges_in_sse(abb1, SavedStateTransition))

        # Record Edge Count
        for k, v in edges.items():
            self.stats.add_data(self, "edge-count:%s" % k, v, scalar=True)

        # Record the number of subtasks that can be reached
        subtask_count = 0
        for subtask in self.system_graph.subtasks:
            if subtask.is_real_thread() and \
               len(subtask.entry_abb.get_incoming_edges(E.system_level)) > 0:
                subtask_count += 1
        self.system_graph.stats.add_data(self, "subtask-count", subtask_count, scalar = True)

        # ISR Count
        self.stats.add_data(self, "isr-count", isr_count, scalar = True)

        # Describe the removed edges
        self.stats.add_data(self, "removed-edges", []) # empty List
        for edge in self.removed_edges:
            self.stats.add_data(self, "removed-edges",
                                (edge.source.syscall_type.name, edge.target.syscall_type.name))
