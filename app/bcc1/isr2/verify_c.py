from generator.graph.verifier_tools import *

def after_RunningTaskAnalysis(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "Idle", "StartOS"])

    t = RunningTaskToolbox(analysis)

    # In H2:
    AT3 = t.reachability(H2, "ActivateTask", [H3], # =>
                         [H2])
    state_before_AT3 = analysis.for_abb(AT3)
    state_after_AT3  = analysis.for_abb(AT3.definite_after('local'))
    # Could be entered by H3 or Idle loop
    assert state_before_AT3.is_unsure_ready_state(H3)
    assert state_after_AT3.is_surely_ready(H3)

    ## Before ActivateTask(H1) the state of H3 is known
    AT1 = t.reachability(H2, "ActivateTask", [H1], # =>
                         [H1])
    state_before_AT1 = analysis.for_abb(AT1)
    assert state_before_AT1.is_surely_ready(H3)


    TT3 = t.reachability(H2, "TerminateTask", [], # =>
                         [H3])
    returned_nodes = TT3.get_outgoing_nodes('global')
    assert len(returned_nodes) == 2
    # When H3 was not preempted, then we start in the entry node
    assert H3.entry_abb in returned_nodes
    # When H3 was interrupted by ISR1, then it was preempted, and
    # should continue after the computation block
    assert H3.entry_abb.definite_after('local') in returned_nodes

    t.reachability(StartOS, "StartOS", [], # =>
                   [Idle])

    t.activate([Idle, H3], # =>
               H2)

    # Idle handler is never left
    t.reachability(Idle, "Idle", [], # =>
                   [Idle])

