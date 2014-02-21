from generator.graph.verifier_tools import *

def after_SystemStateFlow(analysis):
    # Find all three systemcall handlers
    (Handler11, Handler12, Handler13, Idle, StartOS) = \
       get_functions(analysis.system, ["Handler11", "Handler12", "Handler13", "Idle", "StartOS"])

    t = RunningTaskToolbox(analysis)

    # Handler11 has higher priority than Handler12
    t.reachability(StartOS, "StartOS", [],
                 # =>
                 [Handler11])

    # Handler11 has higher priority than Handler12
    t.reachability(Handler11, "ActivateTask", [Handler12],
                 # =>
                 [Handler11])

    # Handler11 is preemptable
    t.reachability(Handler11, "ActivateTask", [Handler13],
                 # =>
                 [Handler11])

    # Handler12 is always activated afterwards
    t.reachability(Handler11, "TerminateTask", [],
                 # =>
                 [Handler13])

    # Handler12 is always activated afterwards
    t.reachability(Handler13, "TerminateTask", [],
                 # =>
                 [Handler12])

    # Handler12 is always activated afterwards
    t.reachability(Handler12, "TerminateTask", [],
                 # =>
                 [Idle])

    # Idle handler is never left
    t.reachability(Idle, "Idle", [],
                   # =>
                   [Idle])

    t.promise_all_syscalls_checked()

