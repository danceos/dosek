from generator.analysis.verifier_tools import *

def after_SystemStateFlow(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS) = \
       get_functions(analysis.system_graph, ["H1", "H2", "H3", "Idle", "StartOS"])

    t = RunningTaskToolbox(analysis)


    t.reachability(StartOS, "StartOS", [], # =>
         [Idle])

    t.activate([Idle, H1, H3], # =>
               H2)

    t.reachability(H1, "ActivateTask", [H3], # =>
         [H1])

    t.reachability(H2, "ChainTask", [H1], # =>
         [H1])

    t.reachability(H1, "TerminateTask", [], # =>
         [H2, H3])

    t.reachability(H3, "TerminateTask", [], # =>
         [Idle])

    t.reachability(Idle, "Idle", [], # =>
         [Idle])

    t.promise_all_syscalls_checked()
