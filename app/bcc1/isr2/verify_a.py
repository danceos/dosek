from generator.graph.common import *

def after_RunningTaskAnalysis(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS, ISR1) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "Idle", "StartOS", "ISR1"])

    syscalls = set()
    syscalls.update(set(H1.get_syscalls()))
    syscalls.update(set(H3.get_syscalls()))
    syscalls.update(set(ISR1.get_syscalls()))



    def test(func, syscall, args, expected_subtasks):
        abb = reachability_test(analysis, func, syscall, args, expected_subtasks)
        syscalls.add(abb)

    test(StartOS, "StartOS", [], # =>
         [Idle])

    test(H2, "TerminateTask", [], # =>
         [Idle])

    activated_test(analysis, [Idle], # =>
                   H2)

    # Idle handler is never left
    test(Idle, "Idle", [], # =>
         [Idle])

    assert set(analysis.system.get_syscalls()) == syscalls, "%s != %s" \
        %(analysis.system.get_syscalls(), syscalls)
