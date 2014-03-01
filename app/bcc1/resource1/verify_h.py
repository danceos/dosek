from generator.graph.verifier_tools import *

def after_SystemStateFlow(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS) = \
       get_functions(analysis.system_graph, ["H1", "H2", "H3", "H4", "H5",
                                       "Idle", "StartOS"])
    (RES_SCHEDULER, R345, R234) = \
        get_objects(analysis.system_graph, ["RES_SCHEDULER", "R345", "R234"])

    t = RunningTaskToolbox(analysis)
    t.mark_syscalls_in_function(H3);

    t.reachability(StartOS, "StartOS", [], # =>
                   [H5])

    t.reachability(H5, "ActivateTask", [H4], # =>
                   [H4])
    t.reachability(H5, "ChainTask", [H4], # =>
                   [H4])

    t.reachability(H4, "ReleaseResource", [R234], # =>
                   [H2])

    ChainTask = t.reachability(H1, "ChainTask", [H2], # =>
                   [H2, H4])


    # Find the two ActivateTask(H1) calls
    ATs = []
    for syscall in H4.get_syscalls():
        if syscall.isA("ActivateTask"):
            ATs.append(syscall)
    (ActivateTask, RES_ActivateTask) = list(sorted(ATs, key = lambda x: x.dynamic_priority))
    assert ActivateTask.dynamic_priority < RES_ActivateTask.dynamic_priority
    # Both ActivateTasks directly dispatch
    t.reachability_bare(ActivateTask, [H1])
    t.reachability_bare(RES_ActivateTask, [H1])

    # The ChainTask in H1 can schedule to the protected block, but not
    # the unprotected one, and to the entry block of H2
    t.reachability_abbs(ChainTask, [RES_ActivateTask.definite_after(E.task_level),
                                    H2.entry_abb])

    t.reachability(H4, "TerminateTask", [], # =>
                   [H5, Idle])

    t.reachability(H2, "TerminateTask", [], # =>
                   [H4])



    t.reachability(Idle, "Idle", [], # =>
         [Idle])

    t.promise_all_syscalls_checked()
