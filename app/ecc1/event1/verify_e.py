from generator.analysis.verifier_tools import *

def after_ConstructGlobalCFG(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS) = \
        get_functions(analysis.system_graph, ["H1", "H2", "H3", "Idle", "StartOS"])

    t = ConstructGlobalCFGToolbox(analysis)

    AT_H3 = t.syscall(H1, "ActivateTask", [H3])

    H1_SE = t.syscall(H1, "SetEvent", None)
    H2_SE = t.syscall(H2, "SetEvent", None)

    WE = t.syscall(H3, "WaitEvent", None)

    # SetEvents will directly release the blocking state
    t.reachability_abbs(H1_SE, [WE.definite_after(E.task_level)])
    t.reachability_abbs(H2_SE, [WE.definite_after(E.task_level)])

    # The next WaitEvent will resume after the SE or the AT
    t.reachability_abbs(WE, [AT_H3.definite_after(E.task_level),
                             H1_SE.definite_after(E.task_level),
                             H2_SE.definite_after(E.task_level)])

    t.reachability(H2, "TerminateTask", [], # =>
                   [Idle])

