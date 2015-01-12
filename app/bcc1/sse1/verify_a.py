from generator.graph.verifier_tools import *

def after_SystemStateFlow(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS) = \
       get_functions(analysis.system_graph, ["H1", "H2", "H3", "H4", "H5", 
                                       "Idle", "StartOS"])
    (RES_SCHEDULER,) = get_objects(analysis.system_graph, ["RES_SCHEDULER"])

    t = RunningTaskToolbox(analysis)
    t.mark_syscalls_in_function(H1)
    t.mark_syscalls_in_function(H2)
    t.mark_syscalls_in_function(H3)
    t.reachability(StartOS, "StartOS", [], # =>
                   [H5])

    AT = t.reachability(H5, "ActivateTask", [H4], # =>
                        [H4])

    t.reachability(H5, "ChainTask", [H4], # =>
                   [H4])

    TT = t.reachability(H4, "TerminateTask", [], # =>
                   [H5, Idle])

    # The dataflow analysis wrongly calculates this edge
    assert H5.entry_abb in TT.get_outgoing_nodes(E.state_flow)

    t.reachability(Idle, "Idle", [], # =>
         [Idle])

    t.promise_all_syscalls_checked()

def after_ConstructGlobalCFG(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS) = \
       get_functions(analysis.system_graph, ["H1", "H2", "H3", "H4", "H5", 
                                       "Idle", "StartOS"])
    if analysis.sse and analysis.state_flow:
        assert len(analysis.removed_edges) == 1
        # The edge from TerminateTask/H4 to H5.entry is removed
        assert analysis.removed_edges[0].target == H5.entry_abb
        assert analysis.removed_edges[0].source.isA("TerminateTask")
