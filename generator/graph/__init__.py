__doc__ = """The graph module abstracts from all kind of Tasks, SubTasks,
AtomicBasicBlocks and BasicBlocks, that make up an System."""

assert __name__ == 'generator.graph'

from generator.graph.Task import Task
from generator.graph.Subtask import Subtask
from generator.graph.AtomicBasicBlock import AtomicBasicBlock
from generator.graph.Function import Function
from generator.graph.Analysis import *
from generator.graph.RunningTask import *
from generator.graph.common import GraphObject
from generator.graph.Sporadic import Alarm
from generator.graph.Resource import Resource
from generator.graph.DynamicPriorityAnalysis import DynamicPriorityAnalysis




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
        self.max_abb_id = 0
        self.system = None
        self.rtsc = None
        self.alarms = []
        self.verifiers = {}
        self.resources = {}

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
        abbs = []
        for function in self.functions.values():
            for abb in function.abbs:
                if abb.abb_id == abb_id:
                    abbs.append(abb)
        assert len(abbs) == 1
        return abbs[0]

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

    def get_subtask(self, name):
        for x in self.tasks:
            for subtask in x.subtasks:
                if subtask.name == name:
                    return subtask


    def find_syscall(self, function, type, arguments, multiple = False):
        abbs = []
        for abb in function.abbs:
            if abb.type == type \
               and abb.arguments == arguments:
                abbs.append(abb)
        if multiple:
            return abbs
        assert len(abbs) == 1, "System call %s::%s(%s) is ambigious" %(function, type, arguments)
        return abbs[0]

    def get_syscalls(self):
        return [x for x in self.get_abbs()
                if x.type != "computation"]

    def scheduler_priority(self):
        """The scheduler priority is higher than the highest task"""
        return max([x.static_priority for x in self.get_subtasks()]) + 1

    def read_system_description(self, system):
        """Reads in the system description and builds the tasks and subtask
        objects and connects them"""
        self.system = system
        for task_desc in system.getTasks():
            task = Task(self, "Task:by-event:" + task_desc.event[0])
            task.set_event(task_desc.event)
            self.tasks.append(task)
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

                subtask.set_deadline(deadline)
                if isISR:
                    isr_osek = system.getISR(subtask_name)
                    subtask.set_static_priority(isr_osek.priority)
                    # Assumption: Our subtasks are non-preemptable basic-tasks
                    subtask.set_preemptable(False)
                    subtask.set_basic_task(True)
                    subtask.set_max_activations(1)
                    subtask.set_autostart(False)
                    subtask.set_is_isr(True)
                else:
                    subtask_osek = system.getSubTask(subtask_name)
                    assert subtask_osek.static_priority != 0, "No user thread can have the thread ID 0, it is reserved for the Idle thread"
                    subtask.set_static_priority(subtask_osek.static_priority)
                    subtask.set_preemptable(subtask_osek.preemptable)
                    subtask.set_basic_task(subtask_osek.is_basic)
                    subtask.set_max_activations(subtask_osek.max_activations)
                    subtask.set_autostart(subtask_osek.autostart)
                    subtask.set_is_isr(False)

        for alarm in system.getAlarms():
            # FIXME: when events are supported
            assert alarm.event == None
            task = self.functions["OSEKOS_TASK_" + alarm.task]
            self.alarms.append(Alarm(self, alarm.name, task))

        for res in system.getResources():
            self.resources[res.name] = Resource(self, res.name, res.tasks)

    def read_rtsc_analysis(self, rtsc):
        self.rtsc = rtsc
        self.max_abb_id = 0

        # Add all atomic basic blocks
        for abb_xml in rtsc.get_abbs():
            abb = AtomicBasicBlock(self, abb_xml.id)
            self.max_abb_id = max(self.max_abb_id, abb_xml.id)

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
            source = self.find_abb(dep.source)
            target = self.find_abb(dep.target)
            source.add_cfg_edge(target)

        # Find all return blocks for functions
        for function in self.functions.values():
            ret_abbs = []
            for abb in function.abbs:
                if len(abb.get_outgoing_edges('local')) == 0:
                    ret_abbs.append(abb)

            if len(ret_abbs) == 0:
                logging.info("Endless loop in %s", function)
            elif len(ret_abbs) > 1:
                # Add an artificial exit block
                abb = self.new_abb()
                function.add_atomic_basic_block(abb)
                for ret in ret_abbs:
                    ret.add_cfg_edge(abb)
                function.set_exit_abb(abb)
            else:
                function.set_exit_abb(ret_abbs[0])


        # Add all 'normal' function call edges
        for call in self.rtsc.get_calls():
            calling_block = self.find_abb(call.abb)
            function = self.functions[call.function]
            called_block  = function.entry_abb
            returned_block = calling_block.definite_after('local')
            return_block = function.exit_abb
            assert calling_block != None, "Could not find CallingBlock ABB%d" % call.abb
            assert return_block != None, "Could not find FunctionCall return block"

            calling_block.remove_cfg_edge(returned_block, 'local')
            calling_block.add_cfg_edge(called_block, 'local')
            return_block.add_cfg_edge(returned_block, 'local')

        # Add all system calls
        for syscall in self.rtsc.syscalls():
            abb = self.find_abb(syscall.abb)
            assert abb.type == 'computation'
            abb.make_it_a_syscall(syscall.name, syscall.arguments)
            assert abb.type != 'computation'
            assert abb in self.get_abbs()
        assert len(self.get_syscalls()) == len(self.rtsc.syscalls())


    def read_verify_script(self, path):
        if not path:
            return
        import imp
        module = imp.load_source('generator.verifier', path)
        for x in dir(module):
            if x.startswith('after') or x.startswith('before'):
                self.verifiers[x] = getattr(module, x)
        logging.info("Loaded %d verifier functions" % len(self.verifiers))

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
        subtask = Subtask(self, "Idle", "Idle")
        self.functions["Idle"] = subtask
        subtask.set_static_priority(0)
        subtask.set_preemptable(True)
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

    def analyze(self, basefilename):
        verifiers_called = set()
        pass_number = 0

        # Dump graph as dot output
        with open("%s_%d_RTSC.dot" %(basefilename, pass_number), "w+") as fd:
            fd.write(self.dump_as_dot())
            pass_number += 1

        while len(self.analysis_pipe) > 0:
            front = self.analysis_pipe[0]
            required = [self.passes[x] for x in front.requires()]
            invalid = [x for x in required if not x.valid]
            if len(invalid) > 0:
                self.analysis_pipe = invalid + self.analysis_pipe
                continue
            # Remove analysis from analysation pipeline
            del self.analysis_pipe[0]
            # Call before analyzer
            verifier_name = "before_" + front.name()
            if verifier_name in self.verifiers:
                self.verifiers[verifier_name](front)
                logging.info("Run %s verifier" % verifier_name)
                verifiers_called.add(verifier_name)

            # Call analyzer pass
            front.analyze()

            # Check graph integrity
            self.fsck()

            # Dump graph as dot output
            with open("%s_%d_%s.dot" %(basefilename, pass_number, front.name()), "w+") as fd:
                fd.write(self.dump_as_dot())

            # Call afteranalyzer
            verifier_name = "after_" + front.name()
            if verifier_name in self.verifiers:
                self.verifiers[verifier_name](front)
                logging.info("Run %s verifier" % verifier_name)
                verifiers_called.add(verifier_name)


            pass_number += 1

        assert verifiers_called == set(self.verifiers.keys()), "Not all verifieres were called (missing %s)" % \
            (set(self.verifiers.keys()) - set(verifiers_called))

    def for_abb(self, abb):
        """Get various informations about an atomic basic block"""
        ret = {}
        for name, p in self.passes.items():
            value = p.for_abb(abb)
            if value:
                assert not name in ret
                ret[name] = value
        return ret

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
