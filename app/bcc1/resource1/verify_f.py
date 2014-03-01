from generator.graph.verifier_tools import *

def after_SystemStateFlow(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS) = \
       get_functions(analysis.system_graph, ["H1", "H2", "H3", "H4", "H5",
                                       "Idle", "StartOS"])
    (RES_SCHEDULER, R345, R234) = \
        get_objects(analysis.system_graph, ["RES_SCHEDULER", "R345", "R234"])

    t = RunningTaskToolbox(analysis)

    t.reachability(StartOS, "StartOS", [], # =>
                   [H5])

    t.reachability(H5, "ChainTask", [H4], # =>
                   [H4])

    t.reachability(H4, "ActivateTask", [H3], # =>
                   [H4])
    t.reachability(H4, "ActivateTask", [H2], # =>
                   [H4])
    t.reachability(H4, "ActivateTask", [H1], # =>
                   [H1])

    t.reachability(H4, "ReleaseResource", [R234], # =>
                   [H2])
    t.reachability(H4, "ReleaseResource", [R345], # =>
                   [H3])

    t.reachability(H1, "TerminateTask", [], # =>
                   [H4])
    t.reachability(H2, "TerminateTask", [], # =>
                   [H4])
    t.reachability(H3, "TerminateTask", [], # =>
                   [H4])
    t.reachability(H4, "TerminateTask", [], # =>
                   [Idle])

    t.reachability(Idle, "Idle", [], # =>
         [Idle])

    t.promise_all_syscalls_checked()
