from .Analysis import Analysis, FixpointIteration
from .AtomicBasicBlock import E, S
from generator.tools import panic

from collections import namedtuple


class InterruptControlAnalysis(Analysis):
    """This pass decides for each computation abb, whether interrupts are
       enabled during its execution or not.
    """
    def __init__(self):
        Analysis.__init__(self)
        self.values = None
        self.__res = None

    def requires(self):
        return ["MoveFunctionsToTask"]

    def get_edge_filter(self):
        return set([E.task_level])

    BlockingCounter = namedtuple("BlockingCounter", ["All", "OS"])

    def block_functor(self, fixpoint, abb):
        # We do an forward analysis, we start with an blocking counter
        # of 0
        state_before = self.BlockingCounter(0, 0)
        # Merge Incoming
        for incoming in abb.get_incoming_nodes(E.task_level):
            # Possible taken resources from incoming edges
            in_state = self.values[incoming]
            All = max(in_state.All, state_before.All)
            OS  = max(in_state.OS, state_before.OS)
            state_before = self.BlockingCounter(All = All, OS = OS)
        

        All, OS = state_before

        if abb.isA(S.DisableAllInterrupts):
            assert All == 0, "Cannot nest Disable/EnableAllinterrupts"
            All += 1
        elif abb.isA(S.EnableAllInterrupts):
            assert All == 1, "Cannot nest Disable/EnableAllinterrupts"
            All -= 1
        elif abb.isA(S.SuspendAllInterrupts):
            All += 1
        elif abb.isA(S.ResumeAllInterrupts):
            All -= 1
        elif abb.isA(S.SuspendOSInterrupts):
            OS += 1
        elif abb.isA(S.ResumeOSInterrupts):
            OS -= 1
        elif abb.syscall_type.isRealSyscall():
            assert All == 0 and OS == 0, "No API calls are allowed with disabled interrupts. OSEK Spec."

        state = self.BlockingCounter(All = All, OS = OS)

        if state != self.values[abb]:
            self.values[abb] = state
            fixpoint.enqueue_soon(items = abb.get_outgoing_nodes(E.task_level))

    def do(self):
        start_basic_blocks = []
        # AtomicBasicBlock -> BlockingCounter
        self.values = {}
        # All Atomic basic blocks have a start value
        for abb in self.system_graph.abbs:
            # The default is that interrupts are allowed
            self.values[abb] = self.BlockingCounter(0, 0)
            if "Interrupts" in abb.syscall_type.name:
                start_basic_blocks.append(abb)

        fixpoint = FixpointIteration(start_basic_blocks)
        fixpoint.do(self.block_functor)

        for abb in self.system_graph.abbs:
            states_incoming = [self.values[x] for x in abb.get_incoming_nodes(E.task_level)]
            if len(states_incoming) > 0:
                first = states_incoming[0]
                for n in states_incoming:
                    if not n == first:
                        panic("""At %s the interrupt blocking level is
                        ambigious for the interrupts level. (%s != %s)""" % \
                              (abb.path(), first, n))
            All, OS = self.values[abb]
            if not abb.isA(S.computation):
                All = 1
                OS  = 1
            abb.interrupt_block_all = All > 0
            abb.interrupt_block_os  = OS > 0 

