from generator.graph.common import *

def after_RunningTaskAnalysis(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS, ISR1) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "Idle", "StartOS", "ISR1"])

    syscalls = set()

    def test(func, syscall, args, expected_subtasks):
        abb = reachability_test(analysis, func, syscall, args, expected_subtasks)
        syscalls.add(abb)

    test(H1, "TerminateTask", [], # =>
         [H3, # If interrupt was triggered
          Idle, # If Interrupt wasn't triggered
          ])

    isr_entry_state = analysis.for_abb(ISR1.entry_abb)
    for st in (H1, H2, H3):
        assert isr_entry_state.is_unsure_ready_state(st)
