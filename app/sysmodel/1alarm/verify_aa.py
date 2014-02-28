from generator.graph.verifier_tools import *

def after_ConstructGlobalCFG(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "H4", "H5", "Idle", "StartOS"])

    t = ConstructGlobalCFGToolbox(analysis)

    # H1 and H3 are not activated
    t.mark_syscalls_in_function(H1)
    t.mark_syscalls_in_function(H4)
    t.mark_syscalls_in_function(H5)

    t.activate([Idle], # =>
               H3)

    assert len(t.self_loop_abbs(H3, E.system_level)) == 0
    assert len(t.self_loop_abbs(H2, E.system_level)) == 0


    t.reachability(H3, "ChainTask", [H2], # =>
                   [H2])

    t.reachability(H2, "TerminateTask", [], # =>
                   [Idle])

    t.reachability(Idle, "Idle", [], # =>
         [Idle])

    t.promise_all_syscalls_checked()
