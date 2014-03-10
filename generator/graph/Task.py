from generator.graph.common import GraphObject

class Task(GraphObject):
    """A Task represents a whole set of SubTasks. All subtasks belong logically together"""
    def __init__(self, system_graph, label):
        GraphObject.__init__(self, label, color = "blue")
        self.system_graph = system_graph
        self.label = label
        self.subtasks = []
        self.functions = []
        self.event = {}
        self.promises = {'serialized': False}

    def graph_subobjects(self):
        return self.subtasks + self.functions

    def set_event(self, event):
        if event[1] == "periodic":
            self.event = dict(list(zip(["name", "type", "period", "phase", "jitter"], event)))
        elif event[1] == "nonperiodic":
            self.event = dict(list(zip(["name", "type", "interarrivaltime"], event)))
        elif event[1] == "once":
            self.event = dict(list(zip(["name", "type"], event)))
        else:
            assert False

    def set_promises(self, promises):
        assert list(promises.keys()) == list(self.promises.keys())
        self.promises = promises

    def does_promise(self, promise):
        return self.promises[promise]

    def add_subtask(self, subtask):
        subtask.task = self
        self.subtasks.append(subtask)

    def add_function(self, function):
        function.task = self
        self.functions.append(function)
        if not function in list(self.system_graph.functions.values()):
            self.system_graph.functions[function.function_name] = function


    def dump(self):
        return self.event

    def fsck(self):
        assert self in self.system_graph.tasks

    def __repr__(self):
        return "<" + str(self.__class__) + " " + self.label + ">"
