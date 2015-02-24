from generator.graph.verifier_tools import *

def after_ConstructGlobalCFG(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, Idle, StartOS) = \
        get_functions(analysis.system_graph, ["H1", "H2", "H3", "Idle", "StartOS"])

    t = ConstructGlobalCFGToolbox(analysis)

    # Since the alarm can also fire before the Wait event, we have two
    # edges at the wait event: to the idle thread when blocking, and
    # to successor block of the wait event
    WE = t.reachability(H1, "WaitEvent", None, #->
                   [H2, H1])
    WE_successor = WE.definite_after(E.task_level)
    assert WE_successor in set(WE.get_outgoing_nodes(E.system_level))


    for H2_block in H2.abbs:
        if H2_block.isA(S.TerminateTask):
            t.reachability_abbs(H2_block, [WE_successor, Idle.entry_abb])
        else:
            for succs in H2_block.get_outgoing_nodes(E.system_level):
                assert succs in H2.abbs

    # If the event was already there, H2 will be executed 
    TT = t.reachability(H1, "TerminateTask", [], #->
                   [H2, Idle])
