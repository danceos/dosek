from generator.graph.verifier_tools import *

def after_SystemStateFlow(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS, ISR1) = \
       get_functions(analysis.system_graph, ["H1", "H2", "H3", "Idle", "StartOS", "ISR1"])

    t = RunningTaskToolbox(analysis)
    t.mark_syscalls_in_function(H1)
    t.mark_syscalls_in_function(ISR1)

    t.reachability(StartOS, "StartOS", [], # =>
         [Idle])

    t.reachability(H2, "TerminateTask", [], # =>
         [Idle, H3]) # H3 could be activated by ISR1

    t.reachability(H3, "TerminateTask", [], # =>
         [Idle])

    t.activate([Idle, H3], # =>
                   H2)

    # H2.entry can be reached by H3.entry, when alarm was running
    assert H2.entry_abb in H3.entry_abb.definite_after(E.function_level)\
                                       .get_outgoing_nodes(E.state_flow)

    t.reachability(Idle, "Idle", [], # =>
         [Idle])

    t.promise_all_syscalls_checked()
