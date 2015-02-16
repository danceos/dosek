from generator.graph.verifier_tools import *

def after_ConstructGlobalCFG(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS) = \
        get_functions(analysis.system_graph, ["H1", "H2", "H3", "Idle", "StartOS"])

    t = ConstructGlobalCFGToolbox(analysis)

    # Where is H2 marked as RUNNING?
    activating = t.activate([H1], H3)
    assert len(activating) == 1, "More than one system call can lead to H2:kickoff"
    assert list(activating)[0].isA(S.ActivateTask), "It is not ActivateTask that leads to H3:kickoff"
    t.mark_syscall(list(activating)[0])

    # Wait Event suspends, since the event was cleared after the
    # activate task
    WE = t.reachability(H3, "WaitEvent", None, # =>
                        [H1])

    # Set event does directly dispatch to the WE successor
    SEs = t.syscalls(H1, "SetEvent", None)
    SE = WE.definite_after(E.task_level).definite_before(E.system_level)
    assert SE in SEs
    assert SE.isA(S.SetEvent)

    # First Set event does not dispatch anywere
    SEs = set(SEs) - {SE}
    first_SE = list(set(SEs) - {SE})[0]
    t.reachability_abbs(first_SE, [first_SE.definite_after(E.task_level)])

    # Terminate Task does return to H1
    TT = t.syscall(H3, "TerminateTask", [])
    t.reachability_abbs(TT, [SE.definite_after(E.task_level)])
