from generator.analysis.verifier_tools import *
from verify_a import *

def after_ConstructGlobalCFG(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS) = \
       get_functions(analysis.system_graph, ["H1", "H2", "H3", "H4", "H5", "Idle", "StartOS"])

    assert count_protected_abbs(analysis, H5, [H3]) == 5, \
        "The should be 5 protected block"

    assert count_protected_abbs(analysis, H3, []) == 0, \
        "The should be one protected block"

