from generator.graph.verifier_tools import *

def after_RunningTaskAnalysis(analysis):
    # Find all three systemcall handlers
    (Handler11, Handler12, Handler13, Idle, StartOS, bar) = \
       get_functions(analysis.system, ["Handler11", "Handler12", "Handler13", "Idle", "StartOS", "bar"])

    t = RunningTaskToolbox(analysis)

    t.reachability(StartOS, "StartOS", [], # =>
         [Handler11])

    t.reachability(Handler11, "ChainTask", [Handler13], # =>
         [Handler13])

    t.reachability(Handler13, "ActivateTask", [Handler12], # =>
         [Handler13])

    t.reachability(Handler13, "TerminateTask", [], # =>
         [Handler12, Handler11])

    t.reachability(Handler12, "ChainTask", [Handler11], # =>
         [Handler11])

    t.reachability(bar, "ActivateTask", [Handler13], # =>
         [Handler13])

    # Idle handler is never left
    t.reachability(Idle, "Idle", [], # =>
         [])

    t.promise_all_syscalls_checked()
