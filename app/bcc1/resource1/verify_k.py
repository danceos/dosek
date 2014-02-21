from generator.graph.verifier_tools import *

def after_SystemStateFlow(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "H4", "H5",
                                       "Idle", "StartOS"])
    (RES_SCHEDULER, R345, R234) = \
        get_objects(analysis.system, ["RES_SCHEDULER", "R345", "R234"])

    t = RunningTaskToolbox(analysis)
    t.mark_syscalls_in_function(H1);
    t.mark_syscalls_in_function(H4);


    t.reachability(StartOS, "StartOS", [], # =>
                   [H5])

    t.reachability(H5, "ActivateTask", [H2], # =>
                   [H2])
    t.reachability(H2, "ActivateTask", [H5], # =>
                   [H2])
    t.reachability(H2, "ActivateTask", [H3], # =>
                   [H2])
    t.reachability(H2, "TerminateTask", [], # =>
                   [H5])

    t.reachability(H5, "ReleaseResource", [R345], # =>
                   [H3])

    t.reachability(H3, "TerminateTask", [], # =>
                   [H5])

    t.reachability(H5, "TerminateTask", [], # =>
                   [Idle])


    t.reachability(Idle, "Idle", [], # =>
         [Idle])

    t.promise_all_syscalls_checked()
