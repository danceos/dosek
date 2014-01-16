import logging
import sys
from generator.graph.common import *
from generator.graph.Subtask import Subtask

class Analysis:
    def __init__(self):
        self.valid = False
        pass

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

class CurrentRunningSubtask(Analysis):
    def __init__(self):
        Analysis.__init__(self)

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


