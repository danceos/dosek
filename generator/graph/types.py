from generator.graph.common import Node, Edge, EdgeType, NodeType
from generator.tools import IntEnum, unique

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
    CheckAlarm = 4
    iret = 5

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

    SetEvent = 37
    ClearEvent = 38
    WaitEvent = 39
    GetEvent = 40

    def isRealSyscall(self):
        return self.value >= SyscallType.kickoff

    def isImplementedSyscall(self):
        return self.isRealSyscall() or self.value == SyscallType.iret


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
