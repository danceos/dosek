from generator.graph.common import GraphObject, Edge
from generator.tools import IntEnum, unique
import collections

@unique
class ControlFlowEdgeLevel(IntEnum):
    """All used edge types"""
    function_level = 1
    task_level = 2
    system_level = 3
    irq_level = 4

    state_transition = 10

    state_flow = 20
    state_flow_irq = 21


    @classmethod
    def color(cls, level):
        ret = {cls.function_level: 'green',
               cls.task_level: 'black',
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
        Edge.__init__(self, source, target, color = E.color(level))
        self.level = level

    def isA(self, edge_level):
        if isinstance(edge_level, collections.Iterable):
            return self.level in edge_level
        return self.level == edge_level


    def __repr__(self):
        return "<%s %s -> %s (%s)>"%(self.__class__.__name__, self.source,
                                     self.target, self.level.name)
@unique
class SyscallType(IntEnum):
    # User code
    computation = 1

    # This are artificial ABBs
    StartOS = 2
    kickoff = 3
    Idle = 4
    iret = 5

    # real system calls
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

    def isRealSyscall(self):
        return self.value >= SyscallType.ActivateTask

    def doesTerminateTask(self):
        if self in (SyscallType.TerminateTask, SyscallType.ChainTask):
            return True
        return False

    @classmethod
    def fromString(cls, name):
        if name.startswith("OSEKOS_"):
            name = name[len("OSEKOS_"):]
        return cls[name]

S = SyscallType

class AtomicBasicBlock(GraphObject):
    def __init__(self, system_graph, abb_id):
        GraphObject.__init__(self, "ABB%d" %(abb_id), color="red")
        self.abb_id = abb_id
        self.system_graph = system_graph
        self.function = None
        self.outgoing_edges = []
        self.incoming_edges = []

        self.syscall_type = S.computation
        self.arguments = []
        # This is set by the DynamicPriorityAnalysis
        self.dynamic_priority = None

        # This is set by InterruptControlAnalysis
        self.interrupt_block_all = None
        self.interrupt_block_os  = None

    def isA(self, syscall_type):
        if isinstance(syscall_type, str):
            syscall_type = SyscallType.fromString(syscall_type)
        if isinstance(syscall_type, collections.Iterable):
            return self.syscall_type in syscall_type
        return self.syscall_type == syscall_type

    @property
    def interrupt_block(self):
        return self.interrupt_block_all or self.interrupt_block_os

    # Edge handling
    ################################################################

    current_edge_filter = None
    @classmethod
    def set_edge_filter(cls, edge_filter):
        cls.current_edge_filter = edge_filter

    def check_edge_filter(self, level):
        assert isinstance(level, E) or isinstance(level, collections.Iterable)
        assert not self.current_edge_filter \
            or level in self.current_edge_filter\
            or (isinstance(level, collections.Iterable) \
                and set(level).issubset(self.current_edge_filter)),\
            "Tried to access edge of type %s, but is prohibited by edge filter"\
            % (self.current_edge_filter)

    def graph_edges(self):
        if self.current_edge_filter:
            return [edge for edge in self.outgoing_edges
                    if edge.level in self.current_edge_filter]
        return self.outgoing_edges

    def add_cfg_edge(self, target, level):
        self.check_edge_filter(level)
        assert not target in self.get_outgoing_edges(level), \
            "Cannot add edge of the same type twice"
        edge = ControlFlowEdge(self, target, level)
        self.outgoing_edges.append(edge)
        target.incoming_edges.append(edge)

    def get_outgoing_edges(self, level):
        self.check_edge_filter(level)
        return [x for x in self.outgoing_edges if x.isA(level)]

    def get_incoming_edges(self, level):
        self.check_edge_filter(level)
        return [x for x in self.incoming_edges if x.isA(level)]

    def get_outgoing_nodes(self, level):
        self.check_edge_filter(level)
        return [x.target for x in self.outgoing_edges if x.isA(level)]

    def get_incoming_nodes(self, level):
        self.check_edge_filter(level)
        return [x.source for x in self.incoming_edges if x.isA(level)]

    def has_edge_to(self, abb, level):
        """Returns the edge of level to an specific abb"""
        self.check_edge_filter(level)

        for edge in self.outgoing_edges:
            if edge.isA(level) and edge.target == abb:
                return edge

    def definite_after(self, level):
        nodes = self.get_outgoing_nodes(level)
        assert len(nodes) == 1
        return nodes[0]

    def definite_before(self, level):
        nodes = self.get_incoming_nodes(level)
        assert len(nodes) == 1
        return nodes[0]


    def remove_cfg_edge(self, to_abb, level):
        assert isinstance(level, E)
        for edge in self.outgoing_edges:
            if edge.target == to_abb and edge.isA(level):
                self.outgoing_edges.remove(edge)
                to_abb.incoming_edges.remove(edge)
                return edge

    def make_it_a_syscall(self, syscall_type, arguments):
        assert isinstance(syscall_type, SyscallType)
        self.syscall_type = syscall_type
        args = []
        # Make the string arguments references to system objects
        for x in arguments:
            if type(x) == str:
                if x.startswith("OSEKOS_TASK_Struct_"):
                    handler_name = x[len("OSEKOS_TASK_Struct_"):]
                    x = self.system_graph.functions["OSEKOS_TASK_" + handler_name]
                elif x.startswith("OSEKOS_RESOURCE_Struct_"):
                    res_name = x[len("OSEKOS_RESOURCE_Struct_"):]
                    x = self.system_graph.resources[res_name]
                elif x.startswith("OSEKOS_ALARM_Struct_"):
                    alarm_name = x[len("OSEKOS_ALARM_Struct_"):]
                    x = alarm_name
            args.append(x)
        self.arguments = args

    def fsck(self):
        assert self.system_graph.find_abb(self.abb_id) == self
        assert self.function != None
        assert self in self.function.abbs
        for edge in self.outgoing_edges:
            assert edge.source == self
            assert edge in edge.target.incoming_edges
            # Target Edge can be found
            assert self.system_graph.find_abb(edge.target.abb_id) == edge.target
        for edge in self.incoming_edges:
            assert edge.target == self
            assert edge in edge.source.outgoing_edges
            # Source abb can be found
            assert self.system_graph.find_abb(edge.source.abb_id) == edge.source

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


