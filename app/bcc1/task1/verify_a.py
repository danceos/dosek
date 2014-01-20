from generator.graph.common import *

def after_RunningTaskAnalysis(analysis):
    # Find all three systemcall handlers
    (Handler11, Handler12, Handler13, Idle, StartOS) = \
       get_functions(analysis.system, ["Handler11", "Handler12", "Handler13", "Idle", "StartOS"])

    syscalls = set()
    def test(func, syscall, args, expected_subtasks):
        abb = reachability_test(analysis, func, syscall, args, expected_subtasks)
        syscalls.add(abb)

    # Handler11 has higher priority than Handler12
    test(StartOS, "StartOS", [], # =>
         [Handler11])

    # Handler11 has higher priority than Handler12
    test(Handler11, "ActivateTask", [Handler12], # =>
         [Handler11])

    # Handler13 is directly started
    test(Handler11, "ActivateTask", [Handler13], # =>
         [Handler13])

    # Handler12 is always activated afterwards
    test(Handler13, "TerminateTask", [], # =>
         [Handler11])

    # Handler12 is always activated afterwards
    test(Handler11, "TerminateTask", [], # =>
         [Handler12])

    # Handler12 is always activated afterwards
    test(Handler12, "TerminateTask", [], # =>
         [Idle])

    # Idle handler is never left
    test(Idle, "Idle", [], # =>
         [Idle])

    assert set(analysis.system.get_syscalls()) == syscalls, "missing %s" \
        %(set(analysis.system.get_syscalls()) - syscalls)

