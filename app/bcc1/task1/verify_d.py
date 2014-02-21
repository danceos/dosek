from generator.graph.verifier_tools import *

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

def after_SystemStateFlow(analysis):
    # Find all three systemcall handlers
    (Handler11, Handler12, Handler13, bar, Idle, StartOS) = \
       get_functions(analysis.system, ["Handler11", "Handler12", "Handler13", "bar", "Idle", "StartOS"])

    t = RunningTaskToolbox(analysis)

    t.reachability(StartOS, "StartOS", [], # =>
         [Handler11])

    t.reachability(Handler11, "ActivateTask", [Handler12], # =>
         [Handler11])

    t.reachability(bar, "ActivateTask", [Handler13], # =>
         [Handler13])

    t.reachability(Handler11, "ActivateTask", [Handler13], # =>
         [Handler13])

    t.reachability(Handler13, "TerminateTask", [], # =>
         [Handler11])

    t.reachability(Handler11, "TerminateTask", [], # =>
         [Handler12, Idle])

    t.reachability(Handler12, "TerminateTask", [], # =>
         [Idle])

    # Idle handler is never left
    t.reachability(Idle, "Idle", [], # =>
         [Idle])

    t.promise_all_syscalls_checked()
