from generator.analysis.verifier_tools import *

def computation_blocks(analysis, function):
    provider = analysis.global_abb_information_provider()

    ret = []
    for abb in function.abbs:
        if not abb.isA(S.computation):
            continue
        abb_info = provider.for_abb(abb)
        if not abb_info:
            continue
        ret.append((abb, abb_info))
    return ret

def count_protected_abbs(analysis, function, others):
    provider = analysis.global_abb_information_provider()
    count = 0
    for abb, info in computation_blocks(analysis, function):
        if abb.interrupt_block:
            count += 1
            assert set(info.tasks_after.keys()) == set([function]),\
                "Interrupt blockade not ensured"
        else:
            assert set(info.tasks_after.keys()) == set([function] + others), \
                "Too much blocked"
    return count

def after_ConstructGlobalCFG(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS) = \
       get_functions(analysis.system_graph, ["H1", "H2", "H3", "H4", "H5", "Idle", "StartOS"])

    assert count_protected_abbs(analysis, H5, [H3]) == 1, \
        "The should be one protected block"

    assert count_protected_abbs(analysis, H3, []) == 0, \
        "The should be one protected block"

