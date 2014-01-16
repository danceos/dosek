__doc__ = """The graph module abstracts from all kind of Tasks, SubTasks,
AtomicBasicBlocks and BasicBlocks, that make up an System."""

assert __name__ == 'generator.graph'

from generator.graph.Task import Task
from generator.graph.Subtask import Subtask
from generator.graph.AtomicBasicBlock import AtomicBasicBlock
from generator.graph.Function import Function
from generator.graph.Analysis import *
from generator.graph.RunningTask import RunningTaskAnalysis
from generator.graph.common import GraphObject


class SystemGraph(GraphObject):
    """A system graph makes up an whole system, including the to be
       produces system blocks"""

    def __init__(self):
        GraphObject.__init__(self, "SystemGraph", root = True)
        self.tasks = []
        self.functions = {}
        self.label = "SystemGraph"
        self.passes = {}
        self.analysis_pipe = []

    def graph_subobjects(self):
        objects = []
        sub_objects = set()
        for task in self.tasks:
            objects.append(task)
            sub_objects.update(set(task.graph_subobjects()))

        for function in self.functions.values():
            if not function in sub_objects:
                objects.append(function)
        return objects

    def find_function(self, name):
        return self.functions[name]

    def find_abb(self, abb_id):
        for function in self.functions.values():
            for abb in function.abbs:
                if abb.abb_id == abb_id:
                    return abb

    def get_abbs(self):
        abbs = []
        for function in self.functions.values():
            for abb in function.abbs:
                abbs.append(abb)
        return abbs
    def get_subtasks(self):
        subtasks = []
        for x in self.tasks:
            subtasks.extend(x.subtasks)
        return subtasks

    def read_system_description(self, system):
        """Reads in the system description and builds the tasks and subtask
        objects and connects them"""
        self.system = system
        for task_desc in system.getTasks():
            task = Task(self, "Task:by-event:" + task_desc.event[0])
            task.set_event(task_desc.event)
            self.tasks.append(task)
            for subtask_name, deadline in task_desc.subtasks.items():
                subtask = Subtask(self, "OSEKOS_TASK_" + subtask_name)
                # Every subtask belongs to a task
                task.add_subtask(subtask)
                # Every subtask is also an function
                self.functions[subtask.function_name] = subtask

                subtask.set_deadline(deadline)

                subtask_osek = system.getSubTask(subtask_name)
                subtask.set_static_priority(subtask_osek.getStaticPriority())
                subtask.set_preemptable(subtask_osek.isPreemptable())
                subtask.set_basic_task(subtask_osek.isBasicSubTask())
                subtask.set_max_activations(subtask_osek.getMaxActivations())
                subtask.set_autostart(subtask_osek.isAutostart())

    def read_rtsc_analysis(self, rtsc):
        self.rtsc = rtsc
        self.max_abb_id = 0

        # Add all atomic basic blocks
        for abb_xml in rtsc.get_abbs():
            abb = AtomicBasicBlock(self, abb_xml.id)
            self.max_abb_id = max(self.max_abb_id, abb_xml.id)
            abb.set_guard(abb_xml.guard)

            # Get function for abb
            function = self.functions.get(abb_xml.in_function)
            if function == None:
                # Not existing yet, just add it
                function = Function(abb_xml.in_function)
                self.functions[abb_xml.in_function] = function
            function.add_atomic_basic_block(abb)
            if abb_xml.func_entry:
                function.set_entry_abb(abb)

        # Add all implicit intra function control flow graphs
        for dep in self.rtsc.get_edges():
            if dep.type == 'ControlFlowABBDependency':
                source = self.find_abb(dep.source)
                target = self.find_abb(dep.target)
                source.add_cfg_edge(target)

        # Add all 'normal' function call edges
        edges = self.rtsc.get_edges()
        for dep in edges:
            if dep.type == 'ExplicitControlFlowABBDependency':
                calling_block = self.find_abb(dep.source)
                called_block  = self.find_abb(dep.target)
                # Subtask Functions cannot be called directly
                if not isinstance(called_block.function, Subtask):
                    # Only entry blocks can be called
                    assert called_block.function.entry_abb == called_block
                    # Only one intra func edge to the middle block
                    local_edges = calling_block.get_outgoing_edges('local')
                    assert len(local_edges) == 1
                    # There is some kind of aritifical middle block,
                    # that is always there. We will identify it and
                    # delete it
                    middle_block = local_edges[0].target
                    local_edges = middle_block.get_outgoing_edges('local')
                    assert len(local_edges) == 1
                    assert middle_block.get_incoming_edges('local')
                    # The Returning block is the block that is the
                    # target for the ret
                    returned_block = local_edges[0].target
                    for ret_edge in edges:
                        if ret_edge.type != 'ExplicitControlFlowABBDependency':
                            continue
                        if ret_edge.target != returned_block.abb_id:
                            continue
                        ret_block = self.find_abb(ret_edge.source)
                        # Adding the Control flow return!
                        ret_block.add_cfg_edge(returned_block)

                    # Add the calling edge
                    calling_block.add_cfg_edge(called_block)
                    # Remove the artificial middle block
                    middle_block.function.remove_abb(middle_block)

        # Add all system calls
        for syscall in self.rtsc.syscalls():
            abb = self.find_abb(syscall.abb)
            abb.make_it_a_syscall(syscall.name, syscall.arguments)

    def new_abb(self):
        self.max_abb_id += 1
        return AtomicBasicBlock(self, self.max_abb_id)

    def add_system_objects(self):
        def system_function(name):
            function = Function(name)
            self.functions[name] = function
            abb = self.new_abb()
            function.add_atomic_basic_block(abb)
            function.set_entry_abb(abb)
            abb.make_it_a_syscall(name, [])
            return function



        # Add Idle Task
        system_task = Task(self, "OSEK")
        self.tasks.append(system_task)
        subtask = Subtask(self, "Idle")
        self.functions["Idle"] = subtask
        subtask.set_static_priority(-1)
        system_task.add_subtask(subtask)
        abb = self.new_abb()
        subtask.add_atomic_basic_block(abb)
        subtask.set_entry_abb(abb)
        subtask.set_autostart(True)
        abb.make_it_a_syscall("Idle", [])
        # System Functions
        StartOS = system_function("StartOS")
        system_task.add_function(StartOS)


    def register_analysis(self, analysis):
        analysis.set_system(self)
        self.passes[analysis.name()] = analysis

    def enqueue_analysis(self, analysis):
        assert analysis in self.passes.values()
        self.analysis_pipe.append(analysis)

    def register_and_enqueue_analysis(self, analysis):
        self.register_analysis(analysis)
        self.enqueue_analysis(analysis)

    def analyze(self):
        while len(self.analysis_pipe) > 0:
            front = self.analysis_pipe[0]
            required = [self.passes[x] for x in front.requires()]
            invalid = [x for x in required if not x.valid]
            if len(invalid) > 0:
                self.analysis_pipe = invalid + self.analysis_pipe
                continue
            del self.analysis_pipe[0]
            front.analyze()
            self.fsck()

    def fsck(self):
        functions = set()
        abbs = set()
        for task in self.tasks:
            task.fsck()
            assert task.system == self
            for subtask in task.subtasks:
                subtask.fsck()
                assert subtask.system == self
                functions.add(subtask)
                abbs.update(set(subtask.abbs))

        assert functions.issubset(set(self.functions.values()))
        for func in self.functions.values():
            if func in functions:
                continue
            abbs.update(set(func.abbs))
        for abb in abbs:
            abb.fsck()


