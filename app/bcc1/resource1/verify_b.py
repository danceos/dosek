from generator.graph.verifier_tools import *

def after_RunningTaskAnalysis(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "H4", "H5", 
                                       "Idle", "StartOS"])
    (RES_SCHEDULER,) = get_objects(analysis.system, ["RES_SCHEDULER"])

    t = RunningTaskToolbox(analysis)
    t.mark_syscalls_in_function(H2)
    t.mark_syscalls_in_function(H3)
    t.mark_syscalls_in_function(H4)

    t.reachability(StartOS, "StartOS", [], # =>
                   [H5])

    t.reachability(H5, "ActivateTask", [H1], # =>
                   [H5])

    # Not protected by resource
    t.reachability(H5, "ActivateTask", [H2], # =>
                   [H2])
    t.reachability(H2, "TerminateTask", [], # =>
                   [H5])

    t.reachability(H5, "ReleaseResource", [RES_SCHEDULER], # =>
                   [H1])

    t.reachability(H1, "TerminateTask", [], # =>
                   [H5])

    t.reachability(H5, "TerminateTask", [], # =>
                   [Idle])

    t.reachability(Idle, "Idle", [], # =>
         [Idle])

    t.promise_all_syscalls_checked()
