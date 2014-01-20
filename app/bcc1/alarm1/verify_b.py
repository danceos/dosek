from generator.graph.common import *

def after_RunningTaskAnalysis(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "Idle", "StartOS"])

    syscalls = set()
    def test(func, syscall, args, expected_subtasks):
        abb = reachability_test(analysis, func, syscall, args, expected_subtasks)
        syscalls.add(abb)

    # H3 are not activated
    syscalls.update(set(H3.get_syscalls()))

    test(StartOS, "StartOS", [], # =>
         [Idle])

    activated_test(analysis, [Idle], # =>
                   H2)

    test(H2, "ActivateTask", [H1], # =>
         [H1])

    test(H2, "TerminateTask", [], # =>
         [Idle])

    test(H1, "TerminateTask", [], # =>
         [H2])

    test(Idle, "Idle", [], # =>
         [Idle])

    assert set(analysis.system.get_syscalls()) == syscalls, "missing %s" \
        %(set(analysis.system.get_syscalls()) - syscalls)

