from generator.graph.common import GraphObject

class Task(GraphObject):
    """A Task represents a whole set of SubTasks. All subtasks belong logically together"""
    def __init__(self, system, label):
        GraphObject.__init__(self, label, color = "blue")
        self.system = system
        self.label = label
        self.subtasks = []

    def graph_subobjects(self):
        return self.subtasks

    def set_event(self, event):
        assert event[1] == "periodic"
        self.event = dict(zip(["name", "periodic", "period", "phase", "jitter"], event))

    def add_subtask(self, subtask):
        subtask.task = self
        self.subtasks.append(subtask)

    def dump(self):
        return self.event

    def fsck(self):
        assert self in self.system.tasks

    def __repr__(self):
        return "<" + str(self.__class__) + " " + self.label + ">"
