from .common import Node, Edge, EdgeType, NodeType
import collections
from .types import S, E, ControlFlowEdge, SyscallType
from .Sporadic import Counter, Alarm, ISR
from .Resource import Resource
from .Subtask import Subtask



class AtomicBasicBlock(Node):
    abb_id_counter = 1
    current_edge_filter = None

    def __init__(self, system_graph, llvmbbs = []):
        Node.__init__(self, ControlFlowEdge, "ABB%d" %(AtomicBasicBlock.abb_id_counter), color="red")
        self.abb_id = AtomicBasicBlock.abb_id_counter
        AtomicBasicBlock.abb_id_counter += 1

        self.system_graph = system_graph
        self.function = None

        self.syscall_type = S.computation
        self.arguments = []

        # This is set by InterruptControlAnalysis
        self.interrupt_block_all = None
        self.interrupt_block_os  = None

        # This is set by the DynamicPriorityAnalysis
        self.dynamic_priority = None

        # MH stuff, TODO: senseful comment
        self.called_functions = set()
        self.basic_blocks = llvmbbs

        # How many sporadic events can fire from here. This field will
        # be filled by SSE and SSF.
        self.sporadic_trigger_count = 0

        # entry_bb and exit_bb are not used anymore after read_llvmpy_analysis
        self.entry_bb =  None
        self.exit_bb  = None
        if self.basic_blocks:
            self.entry_bb = self.basic_blocks[0] #TODO MUSTFIX!
            self.exit_bb  = self.basic_blocks[-1] #TODO MUSTFIX!
            for bb in self.basic_blocks:
                bb.set_parent_ABB(self)

    def isA(self, syscall_type):
        if isinstance(syscall_type, str):
            syscall_type = SyscallType.fromString(syscall_type)
        if isinstance(syscall_type, collections.Iterable):
            return self.syscall_type in syscall_type
        return self.syscall_type == syscall_type

    def is_mergeable(self):
        ''' An ABB is mergeable if it is a computation block AND any called function does not call some syscall'''
        #return self.isA(S.computation) and len([x for x in self.relevant_callees if x.has_syscall]) == 0
        return self.isA(S.computation) and len(self.relevant_callees) == 0

    @property
    def relevant_callees(self):
        return [x for x in self.called_functions if x.has_syscall]


    @property
    def interrupt_block(self):
        return self.interrupt_block_all or self.interrupt_block_os

    def get_id(self):
        return self.abb_id

    def get_basic_blocks(self):
        return self.basic_blocks

    def get_exit_bb(self):
        return self.exit_bb

    def set_entry_bb(self, bb):
        assert(bb in self.basic_blocks)
        self.entry_abb = bb

    def set_exit_bb(self, bb):
        assert(bb in self.basic_blocks)
        self.exit_abb = bb

    def make_it_a_syscall(self, syscall_type, arguments):
        assert isinstance(syscall_type, SyscallType)
        self.syscall_type = syscall_type
        # Mark the parent function accordingly
        if self.function:
            self.function.has_syscall = True
        args = []
        # ATTENTION!: The Event Masks are extracted in the MoveToSubtask Pass!
        # Make the string arguments references to system objects
        for x in arguments:
            if type(x) == str:
                if x.startswith("OSEKOS_TASK_"):
                    handler_name = x[len("OSEKOS_TASK_"):]
                    x = self.system_graph.get(Subtask, handler_name)
                elif x.startswith("OSEKOS_COUNTER_"):
                    name = x[len("OSEKOS_COUNTER_"):]
                    x = self.system_graph.get(Counter, name)
                elif x.startswith("OSEKOS_RESOURCE_"):
                    res_name = x[len("OSEKOS_RESOURCE_"):]
                    x = self.system_graph.get(Resource, res_name)
                elif x.startswith("OSEKOS_ALARM_"):
                    alarm_name = x[len("OSEKOS_ALARM_"):]
                    x = self.system_graph.get(Alarm, alarm_name)
            args.append(x)
        self.arguments = args

    def fsck(self):
        Node.fsck(self)
        assert self.system_graph.find(AtomicBasicBlock, self.abb_id) == self
        assert self.function != None
        assert self in self.function.abbs

        for edge in self.outgoing_edges:
            # Target Edge can be found
            assert self.system_graph.find(AtomicBasicBlock,  edge.target.abb_id) == edge.target
            if edge.isA(E.task_level):
                assert edge.target.function.has_syscall, str(edge)
        for edge in self.incoming_edges:
            # Source abb can be found
            assert self.system_graph.find(AtomicBasicBlock, edge.source.abb_id) == edge.source, \
                "%s -> %s" %(edge, self)

    def id(self):
        return self.abb_id

    def dump(self):
        task = None
        if self.function.subtask:
            task = self.function.subtask.name

        ret = {"id": repr(self),
               "prio": str(self.dynamic_priority),
               "task": task,
               "relevant": len(self.relevant_callees) > 0}

        if self.arguments:
            ret["arguments"] = str(self.arguments)
        if self.interrupt_block_os or self.interrupt_block_all:
            x = []
            if self.interrupt_block_os:
                x += ["OS"]
            if self.interrupt_block_all:
                x += ["All"]
            ret["block-irq"] = "|".join(x)

        return ret

    def __repr__(self):
        if self.isA(S.computation):
            return "ABB%d" % (self.abb_id)
        return "ABB%d/%s"%(self.abb_id, self.syscall_type.name)

    def path(self):
        """Returns a string that should be enable the user to find the atomic
           basic block"""
        return "%s/%s/ABB%s/%s" %(self.function.subtask, self.function,
                                  self.abb_id, self.syscall_type.name)


    def generated_function_name(self):
        generated_function = "OSEKOS_%s__ABB%d" %(self.syscall_type.name, self.abb_id)
        return generated_function

    @property
    def subtask(self):
        return self.function.subtask
