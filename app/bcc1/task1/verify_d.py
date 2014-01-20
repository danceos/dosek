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

    syscalls = set()
    def test(func, syscall, args, expected_subtasks):
        abb = reachability_test(analysis, func, syscall, args, expected_subtasks)
        syscalls.add(abb)


    test(StartOS, "StartOS", [], # =>
         [Handler11])

    test(Handler11, "ActivateTask", [Handler12], # =>
         [Handler11])

    test(bar, "ActivateTask", [Handler13], # =>
         [Handler13])

    test(Handler11, "ActivateTask", [Handler13], # =>
         [Handler13])

    test(Handler13, "TerminateTask", [], # =>
         [Handler11])

    test(Handler11, "TerminateTask", [], # =>
         [Handler12, Idle])

    test(Handler12, "TerminateTask", [], # =>
         [Idle])

    # Idle handler is never left
    test(Idle, "Idle", [], # =>
         [Idle])

    assert set(analysis.system.get_syscalls()) == syscalls
