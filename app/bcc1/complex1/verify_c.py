from generator.graph.common import *

def after_RunningTaskAnalysis(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS, ISR1) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "Idle", "StartOS", "ISR1"])

    syscalls = set()
    syscalls.update(set(H1.get_syscalls()))
    syscalls.update(set(ISR1.get_syscalls()))

    def test(func, syscall, args, expected_subtasks):
        abb = reachability_test(analysis, func, syscall, args, expected_subtasks)
        syscalls.add(abb)
        return abb

    test(StartOS, "StartOS", [], # =>
         [Idle])

    test(H2, "TerminateTask", [], # =>
         [Idle, H3]) # H3 could be activated by ISR1

    test(H3, "ChainTask", [H1], # =>
         [H1])

    test(H1, "TerminateTask", [], # =>
         [H2, # Could be activated by Alarm
          H3, # Could be activated by ISR
          Idle, # Nothing could have happended
      ])

    activated_test(analysis, [Idle, H3, H1], # =>
                   H2)

    activated_test(analysis, [H3], # =>
                   H1)


    # H2.entry can be reached by H3.entry, when alarm was running
    assert H2.entry_abb in H3.entry_abb.get_outgoing_nodes('global')

    test(Idle, "Idle", [], # =>
         [Idle])

    assert set(analysis.system.get_syscalls()) == syscalls, "%s != %s" \
        %(analysis.system.get_syscalls(), syscalls)
