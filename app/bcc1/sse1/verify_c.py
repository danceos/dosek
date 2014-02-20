from generator.graph.verifier_tools import *

def after_RunningTaskAnalysis(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS, bar) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "H4", "H5", 
                                       "Idle", "StartOS", "bar"])
    (RES_SCHEDULER,) = get_objects(analysis.system, ["RES_SCHEDULER"])

    t = RunningTaskToolbox(analysis)
    # There are two terminate tasks in H1
    for syscall in H4.get_syscalls():
        if not syscall.type == "ReleaseResource":
            continue
        t.reachability_abbs(syscall,
                            [H2.entry_abb, H3.entry_abb])
        # Change at these two points is equal
        assert len(syscall.get_outgoing_nodes(E.system_level)) == 2

    t.reachability(H3, "TerminateTask", [], # =>
                   [H4] )

    t.reachability(H2, "TerminateTask", [], # =>
                   [H3] )


    # WE DO NOT PROMISE THSI!
    # t.promise_all_syscalls_checked()

def after_Combine_RunningTask_SSE(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "H4", "H5",
                                       "Idle", "StartOS"])
    assert len(analysis.removed_edges) == 3
    # There are two terminate tasks in H1
    syscalls_found = [False, False]
    for syscall in H4.get_syscalls():
        if not syscall.type == "ReleaseResource":
            continue
        # One ReleaseResource was executed with an ActivateTask
        # before, the other one was not.
        if syscall.definite_after(E.system_level) == H2.entry_abb:
            syscalls_found[0] = True
        if syscall.definite_after(E.system_level) == H3.entry_abb:
            syscalls_found[1] = True
    assert all(syscalls_found), "Not all ReleaseResource dispatches where found (to H2/H3)"
    

