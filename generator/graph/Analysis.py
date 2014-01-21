import logging
import sys
from generator.graph.common import *
from generator.graph.Subtask import Subtask

class Analysis:
    def __init__(self):
        self.valid = False
        self.debug = self.__log_void
        pass

    def __log_void(self, *args, **kwargs):
        pass

    def __log_debug(self, *args, **kwargs):
        logging.debug(*args, **kwargs)

    def set_debug(self, enabled = True):
        if enabled:
            self.debug = self.__log_debug
        else:
            self.debug = self.__log_void

    def set_system(self, system):
        self.system = system

    @classmethod
    def name(cls):
        return cls.__name__

    def requires(self):
        """Returns a list of analysis pass names"""
        return []

    def get_analysis(self, name):
        a = self.system.passes[name]
        assert a.valid
        return a

    def analyze(self):
        if not self.valid:
            logging.info("Running %s analysis" %(self.name()))
            assert self.system != None
            self.do()
            self.valid = True
        else:
            logging.info("Is stil valid: %s analysis" %(self.name()))

    def do(self):
        pass

    def panic(self, msg):
        logging.error(msg)
        sys.exit(-1)

class EnsureComputationBlocks(Analysis):
    """This pass ensures that every system call is surrounded by a
    computation block. This is nessecary to model alarms/interupts and
    other sporadic events, since they can only be take place in those blocks"""

    def __init__(self):
        Analysis.__init__(self)

    def add_before(self, abb):
        nessecary = False
        for node in abb.get_incoming_nodes('local'):
            if node.type != 'computation':
                nessecary = True
        if abb.function.entry_abb == abb:
            nessecary = True
        if not nessecary:
            return
        new = self.system.new_abb()
        new.type = 'computation'
        abb.function.add_atomic_basic_block(new)
        for edge in abb.incoming_edges:
            edge.source.remove_cfg_edge(abb, edge.type)
            edge.source.add_cfg_edge(new, edge.type)
        if abb.function.entry_abb == abb:
            abb.function.entry_abb = new
        new.add_cfg_edge(abb, 'local')

    def add_after(self, abb):
        nessecary = False
        for node in abb.get_outgoing_nodes('local'):
            if node.type != 'computation':
                nessecary = True
        if not nessecary:
            return
        new = self.system.new_abb()
        new.type = 'computation'
        abb.function.add_atomic_basic_block(new)
        for edge in abb.outgoing_edges:
            abb.remove_cfg_edge(edge.target, edge.type)
            new.add_cfg_edge(edge.target, edge.type)

        abb.add_cfg_edge(new, 'local')

    def do(self):
        for syscall in self.system.get_syscalls():
            if syscall.type == "StartOS":
                continue# Do not sourround StartOS with computation blocks
            elif syscall.type == "Idle":
                abb = self.system.new_abb()
                abb.type = 'computation'
                syscall.function.add_atomic_basic_block(abb)
                abb.add_cfg_edge(syscall, 'local')
                syscall.add_cfg_edge(abb, 'local')
                # Do start the idle loop with an computation node
                abb.function.entry_abb = abb
            elif syscall.type in ["ChainTask", "TerminateTask"]:
                # This two syscalls immediatly return the control flow
                # to the system
                self.add_before(syscall)
            else:
                # For all other syscall ABBs add a computation block
                # before and after
                self.add_before(syscall)
                self.add_after(syscall)

class CurrentRunningSubtask(Analysis):
    """This pass does a local control flow propagation of the currently
    running subtask. When a function is called from two subtasks its
    subtask set contains those two subtasks. This is forbidden by the
    generator.
    """
    def __init__(self):
        Analysis.__init__(self)

    def requires(self):
        return [EnsureComputationBlocks.name()]

    def for_abb(self, abb):
        x = list(self.values.get(abb, []))
        if len(x) == 0:
            return None
        elif len(x) == 1:
            return x[0]
        else:
            self.panic("For %s (%s) it is not unambiguous, which task " +
                       "is running at that very moment. This is not " +
                       "supported by the system"%(abb, abb.function))

    def block_functor(self, fixpoint, abb):
        # Gather all task objects from incoming edges
        possible_running_tasks = set(self.values.get(abb, []))
        changed = False
        for incoming in abb.get_incoming_nodes('local'):
            # Possible running task from incoming edges
            for x in self.values.get(incoming, []):
                if not x in possible_running_tasks:
                    changed = True
                    possible_running_tasks.add(x)
        if changed:
            self.values[abb] = possible_running_tasks
            # New task have been added -> revisit child blocks
            fixpoint.enqueue_soon(items = abb.get_outgoing_nodes('local'))

    def do(self):
        start_basic_blocks = []
        # AtomicBasicBlock -> set([Subtask])
        self.values = {}
        # All Atomic basic blocks have a start value
        for task in self.system.tasks:
            for subtask in task.subtasks:
                # Start DFS at all entry nodes
                self.values[subtask.entry_abb] = set([subtask])
                start_basic_blocks.extend(subtask.abbs)


        fixpoint = FixpointIteraton(start_basic_blocks)
        fixpoint.do(self.block_functor)

class MoveFunctionsToTask(Analysis):
    """This pass uses the results of the CurrentRunningSubtask analysis to
    move loose functions to the Task the only calling Subtask belongs
    to. This ensures that every ABB belongs exactly to a single
    Task/Subtask by calling CurrentRunningSubtask.for_abb()
    """
    def __init__(self):
        Analysis.__init__(self)

    def requires(self):
        return [CurrentRunningSubtask.name()]

    def do(self):
        subtask_analysis = self.get_analysis("CurrentRunningSubtask")
        for abb in self.system.get_abbs():
            subtask = subtask_analysis.for_abb(abb)
            # The function belongs to a single subtask. If it is a
            # normal function and not yet moved to a task, move it there.
            if abb.function.task == None \
               and subtask != None:
                subtask.task.add_function(abb.function)
                logging.debug("Moving %s to %s" %(abb.function, subtask.task))



