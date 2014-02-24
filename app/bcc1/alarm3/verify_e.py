from generator.graph.verifier_tools import *
from verify_a import *

def after_ConstructGlobalCFG(analysis):
    # Find all three systemcall handlers
    (H1, H2, H3, H4, H5, Idle, StartOS) = \
       get_functions(analysis.system, ["H1", "H2", "H3", "H4", "H5", "Idle", "StartOS"])

    assert count_protected_abbs(analysis, H5, [H3]) == 1, \
        "The should be 3 protected block"

    assert count_protected_abbs(analysis, H3, []) == 0, \
        "The should be one protected block"

