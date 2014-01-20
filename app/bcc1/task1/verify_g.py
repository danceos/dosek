from generator.graph.common import *

def after_RunningTaskAnalysis(analysis):
    # Find all three systemcall handlers
    (Handler11, Handler12, Handler13, Idle, StartOS, bar) = \
       get_functions(analysis.system, ["Handler11", "Handler12", "Handler13", "Idle", "StartOS", "bar"])

    syscalls = set()
    def test(func, syscall, args, expected_subtasks):
        abb = reachability_test(analysis, func, syscall, args, expected_subtasks)
        syscalls.add(abb)

    test(StartOS, "StartOS", [], # =>
         [Handler11])

    test(Handler11, "ChainTask", [Handler13], # =>
         [Handler13])

    test(Handler13, "ActivateTask", [Handler12], # =>
         [Handler13])

    test(Handler13, "TerminateTask", [], # =>
         [Handler12, Handler11])

    test(Handler12, "ChainTask", [Handler11], # =>
         [Handler11])

    test(bar, "ActivateTask", [Handler13], # =>
         [Handler13])

    # Idle handler is never left
    test(Idle, "Idle", [], # =>
         [])

    assert set(analysis.system.get_syscalls()) == syscalls, "missing %s" \
        %(set(analysis.system.get_syscalls()) - syscalls)
