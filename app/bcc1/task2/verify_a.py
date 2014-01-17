from generator.graph.common import *

def after_RunningTaskAnalysis(analysis):
    # Find all three systemcall handlers
    (Handler11, Handler12, Handler13, Idle, StartOS) = \
       get_functions(analysis.system, ["Handler11", "Handler12", "Handler13", "Idle", "StartOS"])

    def reachability(function, syscall, arguments, reaching_subtasks):
        syscall = analysis.system.find_syscall(function, syscall, arguments)
        assert syscall
        reachable_tasks = analysis.reachable_subtasks_from_abb(syscall)
        assert(reachable_tasks == set(reachable_tasks))

    # Handler11 has higher priority than Handler12
    reachability(StartOS, "StartOS", [],
                 # =>
                 [Handler11])

    # Handler11 has higher priority than Handler12
    reachability(Handler11, "ActivateTask", [Handler12],
                 # =>
                 [Handler11])

    # Handler11 is preemptable
    reachability(Handler11, "ActivateTask", [Handler13],
                 # =>
                 [Handler11])

    # Handler12 is always activated afterwards
    reachability(Handler11, "TerminateTask", [],
                 # =>
                 [Handler13])

    # Handler12 is always activated afterwards
    reachability(Handler13, "TerminateTask", [],
                 # =>
                 [Handler12])

    # Handler12 is always activated afterwards
    reachability(Handler12, "TerminateTask", [],
                 # =>
                 [Idle])

    # Idle handler is never left
    reachability(Idle, "Idle", [],
                 # =>
                 [])

