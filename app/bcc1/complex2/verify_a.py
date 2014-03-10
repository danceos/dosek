from generator.graph.verifier_tools import *

def after_ConstructGlobalCFG(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS, ISR1) = \
       get_functions(analysis.system_graph, ["H1", "H2", "H3", "H4", "H5",
                                             "Idle", "StartOS", "ISR1"])

    t = ConstructGlobalCFGToolbox(analysis)
    t.mark_syscalls_in_function(H2)
    t.mark_syscalls_in_function(H4)
    t.mark_syscalls_in_function(ISR1)

    t.reachability(StartOS, "StartOS", [], # =>
                   [H5])

    t.reachability(H5, "ActivateTask", [H3], # =>
                   [H3])

    t.reachability(H5, "TerminateTask", [], # =>
                   [Idle])

    t.reachability(H1, "TerminateTask", [], # =>
                   [H5, Idle])

    t.reachability(H3, "TerminateTask", [], # =>
                   [H1, H5])

    t.reachability(Idle, "Idle", [], # =>
         [Idle])

    t.promise_all_syscalls_checked()
