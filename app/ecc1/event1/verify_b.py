from generator.graph.verifier_tools import *

def after_ConstructGlobalCFG(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS) = \
        get_functions(analysis.system_graph, ["H1", "H2", "H3", "Idle", "StartOS"])

    t = ConstructGlobalCFGToolbox(analysis)

    # Where is H2 marked as RUNNING?
    activating = t.activate([H1], H2)
    assert len(activating) == 1, "More than one system call can lead to H2:kickoff"
    assert list(activating)[0].isA(S.WaitEvent), "It is not WaitEvent that leads to H2:kickoff"
    t.mark_syscall(list(activating)[0])

    wait_events = set(t.syscalls(H1, "WaitEvent"))
    assert len(wait_events) == 2
    second_wait_event = list(wait_events - activating)[0]

    # SetEvent does activate H1
    SE = t.reachability(H2, "SetEvent", None, # =>
                        [H1])

    # Second Wait Event does not block!
    t.reachability_bare(second_wait_event, [H1])

    # Terminate Task does dispatch to successor of SetEvent
    TT = t.reachability(H1, "TerminateTask", [], # =>
                        [H2])
    t.reachability_abbs(TT, [SE.definite_after(E.task_level)])

    # The chain task, restarts the tasks
    t.reachability(H2, "ChainTask", [H1], # =>
                   [H1])
