from generator.analysis.verifier_tools import *

def after_SystemStateFlow(analysis):
    # Find all three systemcall handlers
    (Handler11, Handler12, Handler13, Idle, StartOS) = \
       get_functions(analysis.system_graph, ["Handler11", "Handler12", "Handler13", "Idle", "StartOS"])

    t = RunningTaskToolbox(analysis)

    t.reachability(StartOS, "StartOS", [], # =>
         [Handler11])

    t.reachability(Handler11, "ChainTask", [Handler13], # =>
         [Handler13])

    t.reachability(Handler11, "TerminateTask", [], # =>
                   [Idle])

    t.reachability(Handler13, "ActivateTask", [Handler12], # =>
         [Handler13])

    t.reachability(Handler13, "TerminateTask", [], # =>
         [Handler12])

    t.reachability(Handler12, "ChainTask", [Handler11], # =>
         [Handler11])

    # Idle handler is never left
    t.reachability(Idle, "Idle", [], # =>
                   [Idle])

    t.promise_all_syscalls_checked()
