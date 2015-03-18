from generator.analysis.verifier_tools import *

def after_ConstructGlobalCFG(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS) = \
        get_functions(analysis.system_graph, ["H1", "H2", "H3", "Idle", "StartOS"])

    t = ConstructGlobalCFGToolbox(analysis)

    # Since the alarm can also fire before the Wait event, we have two
    # edges at the wait event: to the idle thread when blocking, and
    # to successor block of the wait event
    WE = t.reachability(H3, "WaitEvent", None, #->
                   [H3, H1])
    WE_successor = WE.definite_after(E.task_level)
    assert WE_successor in set(WE.get_outgoing_nodes(E.system_level))
