from generator.graph.verifier_tools import *

def after_SystemStateFlow(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS, bar) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "H4", "H5", 
                                       "Idle", "StartOS", "bar"])
    (RES_SCHEDULER,) = get_objects(analysis.system, ["RES_SCHEDULER"])

    t = RunningTaskToolbox(analysis)
    t.mark_syscalls_in_function(H4)

    t.reachability(StartOS, "StartOS", [], # =>
                   [H5])

    t.reachability(H5, "ActivateTask", [H1], # =>
                   [H1])

    t.reachability(H5, "ChainTask", [H1], # =>
                   [H1])

    t.reachability(bar, "ActivateTask", [H2], # =>
                   [H1])

    t.reachability(H1, "ActivateTask", [H3], # =>
                   [H1])


    # There are two terminate tasks in H1
    for syscall in H1.get_syscalls():
        if not syscall.isA("TerminateTask"):
            continue
        t.reachability_abbs(syscall,
                            [H2.entry_abb])
        t.mark_syscall(syscall)

    t.reachability(H3, "TerminateTask", [], # =>
                   [H5, Idle] )

    t.reachability(H2, "TerminateTask", [], # =>
                   [H3, H5, Idle] )

    t.reachability(Idle, "Idle", [], # =>
         [Idle])

    t.promise_all_syscalls_checked()

def after_ConstructGlobalCFG(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "H4", "H5",
                                       "Idle", "StartOS"])
    assert len(analysis.removed_edges) == 2
    # The edge from TerminateTask/H4 to H5.entry is removed
    assert analysis.removed_edges[0].target == H5.entry_abb
    assert analysis.removed_edges[1].target == H5.entry_abb
    assert analysis.removed_edges[0].source.isA("TerminateTask")
    assert analysis.removed_edges[1].source.isA("TerminateTask")


