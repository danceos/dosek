from generator.graph.common import *

def after_RunningTaskAnalysis(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "Idle", "StartOS"])

    syscalls = set()
    def test(func, syscall, args, expected_subtasks):
        abb = reachability_test(analysis, func, syscall, args, expected_subtasks)
        syscalls.add(abb)

    test(StartOS, "StartOS", [], # =>
         [Idle])

    activated_test(analysis, [Idle, H1, H3], # =>
                   H2)

    test(H1, "ActivateTask", [H3], # =>
         [H1])

    test(H2, "ChainTask", [H1], # =>
         [H1])

    test(H1, "TerminateTask", [], # =>
         [H2, H3])

    test(H3, "TerminateTask", [], # =>
         [Idle])

    test(Idle, "Idle", [], # =>
         [Idle])

    assert set(analysis.system.get_syscalls()) == syscalls, "missing %s" \
        %(set(analysis.system.get_syscalls()) - syscalls)

