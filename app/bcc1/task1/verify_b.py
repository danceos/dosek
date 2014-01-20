from generator.graph.common import *

def after_CurrentRunningSubtask(analysis):
    (Handler11,  bar) = \
       get_functions(analysis.system, ["Handler11", "bar"])

    # bar belongs to Handler11
    bar_subtask = analysis.for_abb(bar.entry_abb)
    assert bar_subtask == Handler11
    # But is not yet moved to the Task of Handler11
    assert not bar in Handler11.task.functions

def after_MoveFunctionsToTask(analysis):
    (Handler11,  bar) = \
       get_functions(analysis.system, ["Handler11", "bar"])

    # But is not yet moved to the Task of Handler11
    assert bar in Handler11.task.functions

def after_RunningTaskAnalysis(analysis):
    # Find all three systemcall handlers
    (Handler11, Handler12, Handler13, bar, Idle, StartOS) = \
       get_functions(analysis.system, ["Handler11", "Handler12", "Handler13", "bar", "Idle", "StartOS"])

    def reachability(function, syscall_name, arguments, possible_subtasks):
        syscall = analysis.system.find_syscall(function, syscall_name, arguments)
        assert syscall
        reachable_subtasks = analysis.reachable_subtasks_from_abb(syscall)
        assert(set(reachable_subtasks) == set(possible_subtasks)), "%s:%s(%s)::: %s != %s" %(
            function.function_name, syscall_name, arguments, list(possible_subtasks), list(reachable_subtasks))

    # Handler11 has higher priority than Handler12
    reachability(StartOS, "StartOS", [],
                 # =>
                 [Handler11])

    # Handler11 has higher priority than Handler12
    reachability(Handler11, "ActivateTask", [Handler12],
                 # =>
                 [Handler11])

    # Handler13 is directly started
    reachability(Handler11, "ChainTask", [Handler13],
                 # =>
                 [Handler13])

    # bar is called by Handler11
    reachability(bar, "ActivateTask", [Handler12],
                 # =>
                 [Handler11])


    # Handler 13 does always lead to the activated handler 12
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

