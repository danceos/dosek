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

    def read_oil_system_description(self, system):
        """Reads in the system description out of an OIL file and builds the
        tasks and subtask objects and connects them

        """
        maxprio = 0  # Maximum task prio according to OIL file
        for task_desc in system.getTasks():
            # Create or Get the Task (Group)
            task_group = task_desc.taskgroup
            taskname = task_desc.name
            if task_group not in self._tasks:
                task = Task(self, task_group)
                self._tasks[task_group] = task
                self.stats.add_child(self, "task", task)
            else:
                task = self._tasks[task_group]

            subtask = Subtask(self, taskname, "OSEKOS_TASK_FUNC_" + taskname, task_desc)
            self._subtasks[taskname] = subtask
            # Every subtask belongs to a task
            task.add_subtask(subtask)
            # Every subtask is also a function
            self._functions[subtask.function_name] = subtask
            self.stats.add_child(task, "subtask", subtask)
            # Shift all priorities by +1
            task_desc.static_priority += 1
            assert task_desc.static_priority >= 1, \
                    "No user thread can have the priority 0, reserved for the idle thread"

            if task_desc.static_priority > maxprio:
                maxprio = task_desc.static_priority

            self.stats.add_data(subtask, "is_isr", False, scalar = True)

            # We use event_ids that are only unique for a single
            # subtask.
            event_id = 0
            # Instantiate events for the current task
            for event in task_desc.events.values():
                event.used = True
                Ev = Event(self, "%s__%s"% (subtask.name, event.name), subtask, event_id, event)
                if event.MASK != "AUTO":
                    try:
                        Ev.event_mask = int(event.MASK)
                    except ValueError as Ex:
                        panic("Event Mask not readable: %s", str(Ex))
                    assert len([x for x in bin(Ev.event_mask) if x == "1"]) == 1, "Exactly one bit must be set in event_mask %s" % E


                subtask._events[event.name] = Ev
                subtask.event_mask_valid |= Ev.event_mask
                self._events[Ev.name] = Ev
                event_id += 1
                assert event_id < 32, "No more than 32 Events per Subtask"

        # Events: Assert that every event was used at least once
        for event in system.getEvents():
            assert hasattr(event, "used") and event.used, "Event %s was not used" % event.name

        #  ISR
        isr_prio = maxprio + 1  # ISR get priorities above maximum task prio
        for isr_desc in system.getISRs():
            task_group = isr_desc.taskgroup
            taskname = isr_desc.name
            if task_group not in self._tasks:
                task = Task(self, task_group)
                self._tasks[task_group] = task
                self.stats.add_child(self, "task", task)
            else:
                task = self._tasks[task_group]

            # Generate Subtask for ISR
            subtask = Subtask(self, isr_desc.name, "OSEKOS_ISR_" + isr_desc.name,
                              isr_desc)
            self._subtasks[isr_desc.name] = subtask
            task.add_subtask(subtask)
            self._functions[subtask.function_name] = subtask
            self.stats.add_child(task, "subtask", subtask)

            prio = isr_desc.PRIORITY
            if prio == -1:
                prio = isr_prio
                isr_prio = isr_prio + 1 # increment isr prio

            subtask.conf.static_priority = prio
            self.stats.add_data(subtask, "is_isr", True, scalar=True)

            self._isrs[isr_desc.name] = ISR(self, subtask)

        # Now, after all Task (Groups) are created, now we catch the
        # task group configurations.
        for taskgroup_desc in system.getTaskGroups():
            task_group = self.get(Task, taskgroup_desc.name)
            task_group.promises.update(taskgroup_desc.promises)

        # Counters
        for conf in system.getCounters():
            self._counters[conf.name] = Counter(conf.name, conf)


        # Alarms
        hardware_alarms = []
        for conf in system.getAlarms():
            conf.subtask = self.get(Subtask, conf.subtask)
            assert conf.subtask != None, "Alarm does not activate any task! (maybe callback?)"
            conf.event = conf.subtask.find(Event, conf.event)
            conf.counter = self.get(Counter, conf.counter)

            alarm_object = Alarm(self, conf)

            # Every hardware alarm carries a system call
            if conf.counter.conf.softcounter:
                # For softcounters we use an unregistered ABB
                inner_syscall = AtomicBasicBlock(self.system_graph)
                self.stats.add_child(self, "ABB", inner_syscall)
            else:
                inner_syscall = self.new_abb()
            if conf.event:
                inner_syscall.make_it_a_syscall(S.SetEvent, [conf.subtask, [conf.event]])
            else:
                inner_syscall.make_it_a_syscall(S.ActivateTask, [conf.subtask])
            alarm_object.carried_syscall = inner_syscall

            # Add it to the list of all alarms, and to the list of hardware alarms
            self._alarms[alarm_object.name] = alarm_object
            if not conf.counter.conf.softcounter:
                hardware_alarms.append(alarm_object)

        if len(hardware_alarms) > 0:
            # Generate Alarm Checker subtask
            subtask = AlarmSubtask(self)

            # And add it to the system task
            self.system_task.add_subtask(subtask)
            self.stats.add_child(task, "subtask", subtask)

            # Register Subtask
            self._functions[subtask.function_name] = subtask
            self._subtasks[subtask.name] = subtask

            pred_cc = None
            pred_syscall = None
            for alarm_object in sorted(hardware_alarms, key = lambda a: a.conf.subtask.static_priority):
                subtask.alarms.append(alarm_object)

                # Chain to last CheckCounter
                cc = self.new_abb()
                subtask.add_atomic_basic_block(cc)
                cc.make_it_a_syscall(S.CheckAlarm, [alarm_object])
                if pred_cc:
                    pred_cc.add_cfg_edge(cc, E.function_level)
                    pred_syscall.add_cfg_edge(cc, E.function_level)
                else:
                    subtask.set_entry_abb(cc)

                subtask.add_atomic_basic_block(alarm_object.carried_syscall)
                cc.add_cfg_edge(alarm_object.carried_syscall, E.function_level)
                pred_cc, pred_syscall = cc, alarm_object.carried_syscall

            iret = self.new_abb()
            subtask.add_atomic_basic_block(iret)
            iret.make_it_a_syscall(S.iret, [subtask])
            subtask.set_exit_abb(iret)
            pred_cc.add_cfg_edge(iret, E.function_level)
            pred_syscall.add_cfg_edge(iret, E.function_level)

            self.AlarmHandlerSubtask = subtask
        else:
            # No hardware alarms
            self.AlarmHandlerSubtask = None

        #  Resources
        for res in system.getResources():
            subtasks = [self.get(Subtask, x) for x in res.tasks]
            self._resources[res.name] = Resource(self, res.name, subtasks, res)

        if self.find(Resource, "RES_SCHEDULER") is None:
            sched = "RES_SCHEDULER"
            class ResourceConfig:
                def __init__(self):
                    self.static_priority = None

            subtasks = [x for x in self.subtasks if not x.conf.is_isr]
            self._resources[sched] = Resource(self, sched, subtasks, ResourceConfig())

        for obj in system.getCheckedObjects():
            self._checkedObjects[obj.name] = obj

    def read_llvmpy_analysis(self, llvmpy):
        self.llvmpy = llvmpy

        # Gather functions
        for llvmfunc,llvmbbs in self.llvmpy.functions.items():
            function = self.find(Function, llvmfunc.name)
            if function == None:
                # Not existing yet, just add it...
                function = Function(llvmfunc.name)
                self._functions[llvmfunc.name] = function

            # Add llvm function object
            function.set_llvm_function(llvmfunc)
            # Add ABBs
            for bb in llvmbbs:
              abb = self.new_abb([bb])

              function.add_atomic_basic_block(abb)
              # and set entry abb
              if bb.llvmbb is llvmfunc.entry_basic_block:
                  function.set_entry_abb(abb)

              # type If the flag dOSEK_IGNORE_INTERRUPT_SYSCALLS
              # is set, we make all interrupt control system
              # calls to computation blocks.
              if "dOSEK_IGNORE_INTERRUPT_SYSCALLS" in self.system_graph.conf:
                  if bb.syscall in [S.DisableAllInterrupts, S.EnableAllInterrupts,
                                      S.SuspendOSInterrupts, S.ResumeOSInterrupts,
                                      S.SuspendAllInterrupts, S.ResumeAllInterrupts]:
                      bb.syscall = S.computation


              # make it a syscall and add arguments
              if bb.is_syscall():
                  abb.make_it_a_syscall(bb.get_syscall(), bb.get_syscall_arguments())
                  # Rename syscall in llvm IR, appending ABB id
                  bb.rename_syscall(abb, llvmpy.get_source())

        # Add all implicit intra function control flow graphs
        for func in self.functions:
            for abb in func.abbs:
                exit_bb = abb.get_exit_bb()
                if not exit_bb:
                    #logging.info("llvmpy_analysis, intra function CFG -> skipping: %s", abb.dump())
                    continue

                nextbbs = exit_bb.get_outgoing_nodes(E.basicblock_level)
                for bb in nextbbs:
                    nextabb = bb.get_parent_ABB()
                    abb.add_cfg_edge(nextabb, E.function_level)
            # Remove Dangling Blocks that have no incoming blocks
            # edges, but aren't the entry block. It seems llvm does
            # generate such blocks.
            for abb in func.abbs:
                if len(abb.get_incoming_nodes(E.function_level)) == 0 \
                   and abb != func.entry_abb:
                    func.remove_abb(abb)

        # Find all return blocks for functions
        for function in self.functions:
            ret_abbs = []
            for abb in function.abbs:
                if len(abb.get_outgoing_edges(E.function_level)) == 0:
                    ret_abbs.append(abb)

            if len(ret_abbs) == 0:
                logging.info("Endless loop in %s", function)
            elif len(ret_abbs) > 1:
                # Add an artificial exit block
                abb = self.new_abb()
                function.add_atomic_basic_block(abb)
                for ret in ret_abbs:
                    ret.add_cfg_edge(abb, E.function_level)
                function.set_exit_abb(abb)
            else:
                function.set_exit_abb(ret_abbs[0])

            if isinstance(function, Subtask) and function.conf.is_isr:
                if not function.exit_abb or not function.exit_abb.isA(S.iret):
                    # All ISR function get an additional iret block
                    iret = self.new_abb()
                    function.add_atomic_basic_block(iret)
                    iret.make_it_a_syscall(S.iret, [function])
                    function.exit_abb.add_cfg_edge(iret, E.function_level)
                    function.set_exit_abb(iret)

        # Gather all called Functions in the ABBs, this has to be done, after all ABBs are present
        for abb in self.abbs:
            called_funcs = set()
            # Visit all BBs and gather all called Functions
            for bb in abb.get_basic_blocks():
                if bb.calls_function():
                    callee = self.find(Function, bb.calledFunc.name)
                    if callee:
                        called_funcs.add(callee)
                        abb.called_functions.add(callee)
            # Populate function level set of called functions, needed in ABBMergePass
            abb.function.called_functions.update(called_funcs)

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
