import logging
from .Task import Task
from .Subtask import Subtask
from .AtomicBasicBlock import AtomicBasicBlock, E, S
from .Function import Function
from .PassManager import PassManager
from .Sporadic import Counter, Alarm, ISR, AlarmSubtask
from .Resource import Resource
from .Event import Event
from .common import GraphObject
from generator.statistics import Statistics
from generator.tools import panic
from collections import namedtuple
import functools

class SystemGraph(GraphObject, PassManager):
    """A system graph makes up an whole system, including the to be
       produces system blocks"""

    class MockSubtaskConfig:
        def __init__(self):
            self.static_priority = 0
            self.is_isr = False
            self.preemptable = True
            self.autostart = True
            self.basic_task = False
            self.max_activations = 0

    def __init__(self, configuration):
        GraphObject.__init__(self, "SystemGraph", root=True)
        PassManager.__init__(self, self)
        self.label = "SystemGraph"

        # System Objects
        self._counters = {}
        self._tasks = {}
        self._subtasks = {}
        self._alarms = {}
        self._isrs = {}
        self._resources = {}
        self._checkedObjects = {}
        self._events = {}

        # Application Objects
        self._functions = {}
        self._abbs = {}

        self.system = None
        self.llvmpy = None
        self.stats = Statistics(self)
        self.conf = configuration
        self.impl = None

    # Accessors for System Objects
    @property
    def tasks(self):
        return self._tasks.values()

    @property
    def subtasks(self):
        return self._subtasks.values()

    @property
    def user_subtasks(self):
        return [x for x in self.subtasks if x.is_user_thread()]

    @property
    def real_subtasks(self):
        return [x for x in self.subtasks if x.is_real_thread()]

    @property
    def resources(self):
        return self._resources.values()

    @property
    def alarms(self):
        return self._alarms.values()

    @property
    def counters(self):
        return self._counters.values()

    @property
    def isrs(self):
        return self._isrs.values()

    @property
    def checkedObjects(self):
        return self._checkedObjects.values()

    @property
    def events(self):
        return self._events.values()

    @property
    def functions(self):
        return self._functions.values()

    @property
    def abbs(self):
        return self._abbs.values()

    @property
    def syscalls(self):
        return [x for x in self.abbs
                if not x.isA(S.computation)]

    @property
    def real_syscalls(self):
        return [x for x in self.abbs
                if not x.isA(S.computation) and x.syscall_type.isRealSyscall()]

    @property
    def implemented_syscalls(self):
        within_app =  [x for x in self.abbs
                       if not x.isA(S.computation) and x.syscall_type.isImplementedSyscall()]
        return within_app


    def find(self, cls, name):
        """Get System object by class and name. If system object does not
           exist, this function will return None.

        """
        if issubclass(cls, Alarm):
            return self._alarms.get(name)
        if issubclass(cls, Counter):
            return self._counters.get(name)
        if issubclass(cls, Task):
            return self._tasks.get(name)
        if issubclass(cls, Resource):
            return self._resources.get(name)
        if issubclass(cls, ISR):
            return self._isrs.get(name)

        # Must be before Function, since Subtask inherits from Function
        if issubclass(cls, Subtask):
            return self._subtasks.get(name)

        if issubclass(cls, Function):
            return self._functions.get(name)

        if issubclass(cls, AtomicBasicBlock):
            return self._abbs.get(name)

        assert False, "cls(%s) not supported by SystemGraph.find()" % cls

    def get(self, cls, name):
        """Lile .find, but raises an exception if object does not exists"""
        x = self.find(cls, name)
        assert x is not None, "System Object not found (%s, %s)" %\
            (cls, name)
        return x

    def graph_subobjects(self):
        """Method used by GraphObject to draw the .dot files"""
        objects = []
        sub_objects = set()
        for task in self.tasks:
            objects.append(task)
            sub_objects.update(set(task.graph_subobjects()))

        for function in self.functions:
            if not self.passes["AddFunctionCalls"].is_relevant_function(function):
                continue
            if function not in sub_objects:
                objects.append(function)
        return objects



    def new_abb(self, bbs=[]):
        abb = AtomicBasicBlock(self, bbs)
        self._abbs[abb.get_id()] = abb
        return abb

    def remove_abb(self, abb_id):
        del self._abbs[abb_id]

    def find_syscall(self, function, syscall_type, arguments, multiple=False):
        abbs = []
        for abb in function.abbs:
            if abb.isA(syscall_type) \
               and (arguments == None or abb.arguments == arguments):
                abbs.append(abb)
        if multiple:
            return abbs
        assert len(abbs) == 1, "System call %s::%s(%s) is ambigious" %(function, type, arguments)
        return abbs[0]

    def add_system_objects(self):
        def system_function(syscall_type):
            function = Function(syscall_type.name)
            self._functions[syscall_type.name] = function
            abb = self.new_abb()
            function.add_atomic_basic_block(abb)
            function.set_entry_abb(abb)
            abb.make_it_a_syscall(syscall_type, [])
            return function

        # Add Idle Task
        system_task = Task(self, "OSEK")
        self.system_task = system_task
        self._tasks["OSEK"] = system_task

        idle_subtask = Subtask(self, "Idle", "Idle", self.MockSubtaskConfig())

        self._functions["Idle"] = idle_subtask
        self._subtasks["Idle"] = idle_subtask
        self.idle_subtask = idle_subtask
        system_task.add_subtask(idle_subtask)

        # The idle systemcall
        abb_computation = self.new_abb()
        idle_subtask.add_atomic_basic_block(abb_computation)
        idle_subtask.set_entry_abb(abb_computation)
        abb_idle = self.new_abb()
        idle_subtask.add_atomic_basic_block(abb_idle)
        abb_idle.make_it_a_syscall(S.Idle, [])
        # Edges
        abb_idle.add_cfg_edge(abb_computation, E.function_level)
        abb_computation.add_cfg_edge(abb_idle, E.function_level)

        # System Functions
        StartOS = system_function(S.StartOS)
        system_task.add_function(StartOS)

        # Structure for Statistics logging
        self.stats.add_child(self, "task", system_task)
        self.stats.add_child(system_task, "subtask", idle_subtask)

    def who_has_prio(self, priority):
        # We Inherit PassManager!
        # FIXME: Ugly hack
        assert self.passes["PrioritySpreadingPass"].valid
        return self.passes["PrioritySpreadingPass"].prio_to_participant[priority]

    def fsck(self):
        functions = set()
        abbs = set()
        for task in self.tasks:
            task.fsck()
            assert task.system_graph == self
            for subtask in task.subtasks:
                subtask.fsck()
                assert subtask.system_graph == self
                functions.add(subtask)
                abbs.update(set(subtask.abbs))

        assert functions.issubset(set(self.functions))
        for func in self.functions:
            abbs.update(set(func.abbs))
        for abb in abbs:
            abb.fsck()

        for system_pass in self.passes.values():
            if system_pass.valid and hasattr(system_pass, "fsck"):
                system_pass.fsck()
