from generator.graph.verifier_tools import *

def after_SystemStateFlow(analysis):
    pass
    # Find all three systemcall handlers
    # (Handler11, Handler12, Handler13, Idle, StartOS) = \
    #      get_functions(analysis.system_graph, ["Handler11", "Handler12", "Handler13", "Idle", "StartOS"])

    # t = RunningTaskToolbox(analysis)

    # # Handler11 has higher priority than Handler12
    # t.reachability(StartOS, "StartOS", [], # =>
    #                [Handler11])

    # # Handler11 has higher priority than Handler12
    # t.reachability(Handler11, "ActivateTask", [Handler12], # =>
    #                [Handler11])

    # # Handler13 is directly started
    # t.reachability(Handler11, "ActivateTask", [Handler13], # =>
    #                [Handler13])

    # # Handler12 is always activated afterwards
    # t.reachability(Handler13, "TerminateTask", [], # =>
    #                [Handler11])

    # # Handler12 is always activated afterwards
    # t.reachability(Handler11, "TerminateTask", [], # =>
    #                [Handler12])

    # # Handler12 is always activated afterwards
    # t.reachability(Handler12, "TerminateTask", [], # =>
    #                [Idle])

    # # Idle handler is never left
    # t.reachability(Idle, "Idle", [], # =>
    #                [Idle])

    # t.promise_all_syscalls_checked()
