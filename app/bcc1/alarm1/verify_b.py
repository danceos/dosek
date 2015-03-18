from generator.analysis.verifier_tools import *

def after_SystemStateFlow(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS) = \
       get_functions(analysis.system_graph, ["H1", "H2", "H3", "Idle", "StartOS"])

    t = RunningTaskToolbox(analysis)

    # H3 are not activated
    t.mark_syscalls_in_function(H3)

    t.reachability(StartOS, "StartOS", [], # =>
         [Idle])

    t.activate([Idle], # =>
               H2)

    t.reachability(H2, "ActivateTask", [H1], # =>
         [H1])

    t.reachability(H2, "TerminateTask", [], # =>
         [Idle])

    t.reachability(H1, "TerminateTask", [], # =>
         [H2])

    t.reachability(Idle, "Idle", [], # =>
         [Idle])

    t.promise_all_syscalls_checked()
