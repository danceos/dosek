from generator.graph.common import Node, Edge, EdgeType, NodeType
from generator.tools import IntEnum, unique
import collections

@unique
class ControlFlowEdgeLevel(IntEnum):
    """All used edge types"""
    basicblock_level = 0
    function_level = 1
    task_level = 2
    system_level = 3
    irq_level = 4

    state_transition = 10

    state_flow = 20
    state_flow_irq = 21


    @classmethod
    def color(cls, level):
        ret = {cls.basicblock_level: 'yellow',
               cls.function_level: 'black',
               cls.task_level: 'green',
               cls.system_level: 'blue',
               cls.irq_level: 'red',
               cls.state_transition: 'black',
               cls.state_flow: 'darkorchid2',
               cls.state_flow_irq: 'gold1',
        }
        return ret[level]

E = ControlFlowEdgeLevel

class ControlFlowEdge(Edge):
    """Task level control flow edges are possible control flow transitions
       that stay on the task level (aka. always on the same stack/same task
       context)"""

    def __init__(self, source, target, level = E.task_level):
        Edge.__init__(self, source, target, level, color = E.color(level))

@unique
class SyscallType(IntEnum):
    # User code
    computation = 1

    # This are artificial ABBs
    StartOS = 2
    Idle = 3
    iret = 4

    # real system calls
    kickoff = 19
    ActivateTask = 20
    TerminateTask = 21
    ChainTask = 22
    SetRelAlarm = 23
    CancelAlarm = 24
    GetResource = 25
    ReleaseResource = 26

    DisableAllInterrupts = 27
    EnableAllInterrupts  = 28
    SuspendAllInterrupts = 29
    ResumeAllInterrupts  = 30
    SuspendOSInterrupts  = 31
    ResumeOSInterrupts   = 32

    GetAlarm = 33
    AdvanceCounter = 34
    AcquireCheckedObject = 35
    ReleaseCheckedObject = 36

    def isRealSyscall(self):
        return self.value >= SyscallType.kickoff

    def doesKickoffTask(self):
        if self == SyscallType.kickoff:
            return True
        return False

    def doesTerminateTask(self):
        if self in (SyscallType.TerminateTask, SyscallType.ChainTask):
            return True
        return False

    @classmethod
    def fromString(cls, name):
        if name.startswith("OSEKOS_"):
            name = name[len("OSEKOS_"):]

        # Check if call is something else than a computiation block
        for enumname,member in S.__members__.items():
            if enumname == name:
                return cls[name]

        # if not a syscall, it is a computation block
        return cls["computation"]

S = SyscallType

class AtomicBasicBlock(Node):
    current_edge_filter = None

    def __init__(self, system_graph, abb_id, llvmbbs = []):
        Node.__init__(self, ControlFlowEdge, "ABB%d" %(abb_id), color="red")
        self.abb_id = abb_id
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
        self.function.has_syscall = True
        args = []
        # Make the string arguments references to system objects
        for x in arguments:
            if type(x) == str:
                if x.startswith("OSEKOS_TASK_Struct_"):
                    handler_name = x[len("OSEKOS_TASK_Struct_"):]
                    x = self.system_graph.functions["OSEKOS_TASK_" + handler_name]
                elif x.startswith("OSEKOS_COUNTER_Struct_"):
                    name = x[len("OSEKOS_COUNTER_Struct_"):]
                    x = name
                elif x.startswith("OSEKOS_RESOURCE_Struct_"):
                    res_name = x[len("OSEKOS_RESOURCE_Struct_"):]
                    x = self.system_graph.resources[res_name]
                elif x.startswith("OSEKOS_ALARM_Struct_"):
                    alarm_name = x[len("OSEKOS_ALARM_Struct_"):]
                    x = alarm_name
            args.append(x)
        self.arguments = args

    def fsck(self):
        Node.fsck(self)
        assert self.system_graph.find_abb(self.abb_id) == self
        assert self.function != None
        assert self in self.function.abbs

        for edge in self.outgoing_edges:
            # Target Edge can be found
            assert self.system_graph.find_abb(edge.target.abb_id) == edge.target
            if edge.isA(E.task_level):
                assert edge.target.function.has_syscall, str(edge)
        for edge in self.incoming_edges:
            # Source abb can be found
            assert self.system_graph.find_abb(edge.source.abb_id) == edge.source, \
                "%s -> %s" %(edge, self)

    def id(self):
        return self.abb_id

    def dump(self):
        task = None
        if self.function.subtask:
            task = self.function.subtask.name

        ret = {"id": repr(self),
               "prio": str(self.dynamic_priority),
               "task": task}

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
