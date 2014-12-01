import logging
from generator.graph.Task import Task
from generator.graph.Subtask import Subtask
from generator.graph.AtomicBasicBlock import AtomicBasicBlock, E, S
from generator.graph.Function import Function
from generator.graph.PassManager import PassManager
from generator.graph.Sporadic import Alarm, ISR
from generator.graph.Resource import Resource
from generator.graph.common import GraphObject
from generator.statistics import Statistics
from collections import namedtuple
import functools


class SystemGraph(GraphObject, PassManager):
    """A system graph makes up an whole system, including the to be
       produces system blocks"""

    def __init__(self):
        GraphObject.__init__(self, "SystemGraph", root = True)
        PassManager.__init__(self, self)
        self.counters = {}
        self.tasks = []
        self.functions = {}
        self.all_abbs = {}
        self.label = "SystemGraph"
        self.max_abb_id = 0
        self.system = None
        self.rtsc = None
        self.llvmpy = None
        self.alarms = []
        self.isrs = []
        self.resources = {}
        self.stats = Statistics(self)

    def graph_subobjects(self):
        objects = []
        sub_objects = set()
        for task in self.tasks:
            objects.append(task)
            sub_objects.update(set(task.graph_subobjects()))

        for function in self.functions.values():
            if not self.passes["AddFunctionCalls"].is_relevant_function(function):
                continue
            if not function in sub_objects:
                objects.append(function)
        return objects

    def find_function(self, name):
        """

        :rtype : generator.graph.Function
        """
        return self.functions.get(name, None)

    def find_abb(self, abb_id):
        return self.all_abbs[abb_id]

    def remove_abb(self, abb_id):
        del self.all_abbs[abb_id]

    def get_abbs(self):
        return self.all_abbs.values()

    @functools.lru_cache(maxsize=None)
    def get_subtasks(self):
        subtasks = []
        for x in self.tasks:
            subtasks.extend(x.subtasks)
        return sorted(subtasks, key=lambda t: t.name)

    def get_subtask(self, name):
        for x in self.tasks:
            for subtask in x.subtasks:
                if subtask.name == name:
                    return subtask


    def find_syscall(self, function, syscall_type, arguments, multiple = False):
        abbs = []
        for abb in function.abbs:
            if abb.isA(syscall_type) \
               and abb.arguments == arguments:
                abbs.append(abb)
        if multiple:
            return abbs
        assert len(abbs) == 1, "System call %s::%s(%s) is ambigious" %(function, type, arguments)
        return abbs[0]

    def get_syscalls(self):
        return [x for x in self.get_abbs()
                if not x.isA(S.computation)]

    def scheduler_priority(self):
        """The scheduler priority is higher than the highest task"""
        return max([x.static_priority for x in self.get_subtasks()]) + 1


    def read_oil_system_description(self, system):
        """Reads in the system description out of an OIL file and builds the tasks and subtask
        objects and connects them"""
        maxprio = 0  #  Maximum task prio according to OIL file
        for task_desc in system.getTasks():
            taskname = task_desc.name
            task = Task(self, "Task:" + taskname)
            self.tasks.append(task)
            self.stats.add_child(self, "task", task)
            subtask = Subtask(self, taskname, "OSEKOS_TASK_" + taskname)
            # Every subtask belongs to a task
            task.add_subtask(subtask)
            # Every subtask is also a function
            self.functions[subtask.function_name] = subtask
            self.stats.add_child(task, "subtask", subtask)
            assert task_desc.priority != 0, \
                    "No user thread can have the priority 0, reserved for the idle thread"
            subtask.set_static_priority(task_desc.priority)

            if task_desc.priority > maxprio:
                maxprio = task_desc.priority

            subtask.set_preemptable(task_desc.preemptable)
            subtask.set_basic_task(True)
            subtask.set_max_activations(task_desc.max_activations)
            subtask.set_autostart(task_desc.autostart)
            subtask.set_is_isr(False)
            self.stats.add_data(subtask, "is_isr", False, scalar = True)

        #  ISR
        isr_prio = maxprio + 1  # ISR get priorities above maximum task prio
        for isr_desc in system.getISRs():
            task = Task(self, "ISRTask:" + isr_desc.name)
            self.tasks.append(task)
            self.stats.add_child(self, "task", task)
            subtask = Subtask(self, isr_desc.name, "OSEKOS_ISR_" + isr_desc.name)
            task.add_subtask(subtask)
            self.functions[subtask.function_name] = subtask
            self.stats.add_child(task, "subtask", subtask)

            prio = isr_desc.PRIORITY
            if prio == -1:
                prio = isr_prio
                isr_prio = isr_prio + 1 # increment isr prio

            subtask.set_static_priority(prio)

            # Assumption: Our subtasks are non-preemptable basic-tasks
            subtask.set_preemptable(False)
            subtask.set_basic_task(True)
            subtask.set_max_activations(1)
            subtask.set_autostart(False)
            subtask.set_is_isr(True, isr_desc.device)
            self.stats.add_data(subtask, "is_isr", True, scalar = True)

            self.isrs.append(ISR(self, subtask))

        #  Counters
        Counter = namedtuple("Counter", ["name", "maxallowedvalue", "ticksperbase", "mincycle",
                                         "softcounter"])
        for ctr in system.getCounters():
            self.counters[ctr.name] = Counter(name = ctr.name,
                                          maxallowedvalue = ctr.MAXALLOWEDVALUE,
                                          ticksperbase = ctr.TICKSPERBASE,
                                          mincycle = ctr.MINCYCLE,
                                          softcounter = ctr.SOFTCOUNTER)

        #  Alarms
        for alarm in system.getAlarms():
            assert alarm.activated_task() != None, "Alarm does not activate any task! (maybe callback?)"
            activated_subtask = self.functions["OSEKOS_TASK_" + alarm.activated_task()]
            belongs_to_task = activated_subtask.task

            #  Generate an Alarm Handler SubTask
            name = "OSEKOS_ALARM_HANDLER_" + alarm.name
            subtask = Subtask(self, alarm.name, name)
            subtask.set_static_priority(1<<31)
            subtask.set_preemptable(False)
            subtask.set_basic_task(True)
            subtask.set_max_activations(1)
            subtask.set_autostart(False)
            subtask.set_is_isr(True)

            #  And add it to the task where the activated task belongs to
            belongs_to_task.add_subtask(subtask)
            self.functions[subtask.function_name] = subtask

            self.alarms.append(Alarm(self, subtask, alarm, activated_subtask))

        #  Resources
        for res in system.getResources():
            self.resources[res.name] = Resource(self, res.name, res.tasks)

        if not "RES_SCHEDULER" in self.resources:
            sched = "RES_SCHEDULER"
            subtasks = [x.name for x in self.get_subtasks()
                        if not x.is_isr]
            self.resources[sched] = Resource(self, sched, subtasks)


    def read_xml_system_description(self, system):
        """Reads in the system description out of an XML file and builds the tasks and subtask
        objects and connects them"""

        for task_desc in system.getTasks():
            task = Task(self, "Task:by-event:" + task_desc.event[0])
            task.set_event(task_desc.event)
            task.set_promises(task_desc.promises)
            self.tasks.append(task)
            self.stats.add_child(self, "task", task)
            for subtask_name, deadline in task_desc.subtasks.items():
                isISR = system.isISR(subtask_name)
                if isISR:
                    subtask = Subtask(self, subtask_name, "OSEKOS_ISR_" + subtask_name)
                else:
                    subtask = Subtask(self, subtask_name, "OSEKOS_TASK_" + subtask_name)
                # Every subtask belongs to a task
                task.add_subtask(subtask)
                # Every subtask is also an function
                self.functions[subtask.function_name] = subtask
                self.stats.add_child(task, "subtask", subtask)


                subtask.set_deadline(deadline)
                if isISR:
                    isr_osek = system.getISR(subtask_name)
                    subtask.set_static_priority(isr_osek.priority)
                    # Assumption: Our subtasks are non-preemptable basic-tasks
                    subtask.set_preemptable(False)
                    subtask.set_basic_task(True)
                    subtask.set_max_activations(1)
                    subtask.set_autostart(False)
                    subtask.set_is_isr(True, isr_osek.device)
                    self.stats.add_data(subtask, "is_isr", True, scalar = True)

                    self.isrs.append(ISR(self, subtask))
                else:
                    subtask_osek = system.getSubTask(subtask_name)
                    assert subtask_osek.static_priority != 0,  \
                        "No user thread can have the thread ID 0, it is reserved for the Idle thread"
                    subtask.set_static_priority(subtask_osek.static_priority)
                    subtask.set_preemptable(subtask_osek.preemptable)
                    subtask.set_basic_task(subtask_osek.is_basic)
                    subtask.set_max_activations(subtask_osek.max_activations)
                    subtask.set_autostart(subtask_osek.autostart)
                    subtask.set_is_isr(False)
                    self.stats.add_data(subtask, "is_isr", False, scalar = True)



        self.counters = {x.name: x for x in system.getHardwareCounters()}

        for alarm in system.getAlarms():
            activated_subtask = self.functions["OSEKOS_TASK_" + alarm.task]
            belongs_to_task = activated_subtask.task

            # Generate a Alarm Handler SubTask
            name = "OSEKOS_ALARM_HANDLER_" + alarm.name
            subtask = Subtask(self, alarm.name, name)
            subtask.set_static_priority(1<<31)
            subtask.set_preemptable(False)
            subtask.set_basic_task(True)
            subtask.set_max_activations(1)
            subtask.set_autostart(False)
            subtask.set_is_isr(True)


            # And add it to the task where the activated task belongs to
            belongs_to_task.add_subtask(subtask)
            self.functions[subtask.function_name] = subtask

            self.alarms.append(Alarm(self, subtask, alarm, activated_subtask))

        for res in system.getResources():
            self.resources[res.name] = Resource(self, res.name, res.tasks)
        if not "RES_SCHEDULER" in self.resources:
            sched = "RES_SCHEDULER"
            subtasks = [x.name for x in self.get_subtasks()
                       if not x.is_isr]
            self.resources[sched] = Resource(self, sched, subtasks)


    def read_llvmpy_analysis(self, llvmpy):
        self.llvmpy = llvmpy
        self.max_abb_id = 0

        # Gather functions
        for llvmfunc,llvmbbs in self.llvmpy.functions.items():
            function = self.functions.get(llvmfunc.name)
            if function == None:
                # Not existing yet, just add it...
                function = Function(llvmfunc.name)
                self.functions[llvmfunc.name] = function

            # Add llvm function object
            function.set_llvm_function(llvmfunc)
            # Add ABBs
            for bb in llvmbbs:
              abb = self.new_abb([bb])

              function.add_atomic_basic_block(abb)
              # and set entry abb
              if bb.llvmbb is llvmfunc.entry_basic_block:
                  function.set_entry_abb(abb)

              # make it a syscall and add arguments
              if bb.is_syscall():
                  abb.make_it_a_syscall(bb.get_syscall(), bb.get_syscall_arguments())
                  # Rename syscall in llvm IR, appending ABB id
                  bb.rename_syscall(abb, llvmpy.get_source())


        # Generate an ActivateTask for every alarm
        for alarm in self.alarms:
            activate_task = self.new_abb()
            alarm.handler.add_atomic_basic_block(activate_task)
            alarm.handler.set_entry_abb(activate_task)
            activate_task.make_it_a_syscall(S.ActivateTask, [alarm.subtask])
            alarm.carried_syscall = activate_task

            # Statistic generation
            self.stats.add_child(alarm.handler.task, "subtask", alarm.handler)

        # Add all implicit intra function control flow graphs
        for functionname, func in self.functions.items():
            for abb in func.abbs:
                exit_bb = abb.get_exit_bb()
                if not exit_bb:
                    #logging.info("llvmpy_analysis, intra function CFG -> skipping: %s", abb.dump())
                    continue

                nextbbs = exit_bb.get_outgoing_nodes(E.basicblock_level)
                for bb in nextbbs:
                    nextabb = bb.get_parent_ABB()
                    abb.add_cfg_edge(nextabb, E.function_level)

        # Find all return blocks for functions
        for function in self.functions.values():
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
            if isinstance(function, Subtask) and function.is_isr:
                # All ISR function get an additional iret block
                iret = self.new_abb()
                function.add_atomic_basic_block(iret)
                iret.make_it_a_syscall(S.iret, [function])
                function.exit_abb.add_cfg_edge(iret, E.function_level)
                function.set_exit_abb(iret)

        # Gather all called Functions in the ABBs, this has to be done, after all ABBs are present
        for abb in self.get_abbs():
            called_funcs = set()
            # Visit all BBs and gather all called Functions
            for bb in abb.get_basic_blocks():
                if bb.calls_function():
                    callee = self.find_function(bb.calledFunc.name)
                    if callee:
                        called_funcs.add(callee)
                        abb.called_functions.add(callee)
            # Populate function level set of called functions, needed in ABBMergePass
            abb.function.called_functions.update(called_funcs)

    def read_rtsc_analysis(self, rtsc):
        self.rtsc = rtsc
        self.max_abb_id = 0

        # Add all atomic basic blocks
        for abb_xml in rtsc.get_abbs():
            abb = AtomicBasicBlock(self, abb_xml.id)
            self.max_abb_id = max(self.max_abb_id, abb_xml.id)
            ## add to global abb dict for faster search
            self.all_abbs[abb.get_id()] = abb

            # Get function for abb
            function = self.functions.get(abb_xml.in_function)
            if function == None:
                # Not existing yet, just add it
                function = Function(abb_xml.in_function)
                self.functions[abb_xml.in_function] = function
            function.add_atomic_basic_block(abb)
            if abb_xml.func_entry:
                function.set_entry_abb(abb)

        # Generate an ActivateTask for every alarm
        for alarm in self.alarms:
            activate_task = self.new_abb()
            alarm.handler.add_atomic_basic_block(activate_task)
            alarm.handler.set_entry_abb(activate_task)
            activate_task.make_it_a_syscall(S.ActivateTask, [alarm.subtask])
            alarm.carried_syscall = activate_task

            # Statistic generation
            self.stats.add_child(alarm.handler.task, "subtask", alarm.handler)
            self.stats.add_data(alarm.handler, "is_isr", True, scalar = True)


        # Add all implicit intra function control flow graphs
        for dep in self.rtsc.get_edges():
            source = self.find_abb(dep.source)
            target = self.find_abb(dep.target)
            source.add_cfg_edge(target, E.function_level)

        # Find all return blocks for functions
        for function in self.functions.values():
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
            if isinstance(function, Subtask) and function.is_isr:
                # All ISR function get an additional iret block
                iret = self.new_abb()
                function.add_atomic_basic_block(iret)
                iret.make_it_a_syscall(S.iret, [function])
                function.exit_abb.add_cfg_edge(iret, E.function_level)
                function.set_exit_abb(iret)

        # Add all system calls
        for syscall in self.rtsc.syscalls():
            abb = self.find_abb(syscall.abb)
            assert abb.isA(S.computation)
            abb.make_it_a_syscall(S.fromString(syscall.name), syscall.arguments)
            assert not abb.isA(S.computation)
            assert abb in self.get_abbs()
        assert len(self.get_syscalls()) >= len(self.rtsc.syscalls())

    def new_abb(self, bbs=[]):
        self.max_abb_id += 1
        abb =  AtomicBasicBlock(self, self.max_abb_id, bbs)
        self.all_abbs[abb.get_id()] = abb
        return abb


    def add_system_objects(self):
        def system_function(syscall_type):
            function = Function(syscall_type.name)
            self.functions[syscall_type.name] = function
            abb = self.new_abb()
            function.add_atomic_basic_block(abb)
            function.set_entry_abb(abb)
            abb.make_it_a_syscall(syscall_type, [])
            return function

        # Add Idle Task
        system_task = Task(self, "OSEK")
        self.system_task = system_task
        self.tasks.append(system_task)
        idle_subtask = Subtask(self, "Idle", "Idle")
        self.functions["Idle"] = idle_subtask
        self.idle_subtask = idle_subtask
        idle_subtask.set_static_priority(0)
        idle_subtask.set_preemptable(True)
        system_task.add_subtask(idle_subtask)
        # The idle systemcall
        abb = self.new_abb()
        idle_subtask.add_atomic_basic_block(abb)
        idle_subtask.set_entry_abb(abb)
        idle_subtask.set_autostart(True)
        abb.make_it_a_syscall(S.Idle, [])
        # System Functions
        StartOS = system_function(S.StartOS)
        system_task.add_function(StartOS)

        # Structure for Statistics logging
        self.stats.add_child(self, "task", system_task)
        self.stats.add_child(system_task, "subtask", idle_subtask)

    def who_has_prio(self, priority):
        # We Inherit PassManager!
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

        assert functions.issubset(set(self.functions.values()))
        for func in self.functions.values():
            if func in functions:
                continue
            abbs.update(set(func.abbs))
        for abb in abbs:
            abb.fsck()

        for system_pass in self.passes.values():
            if system_pass.valid and hasattr(system_pass, "fsck"):
                system_pass.fsck()
