from generator.graph.Function import Function

class Subtask(Function):
    def __init__(self, system, name):
        Function.__init__(self, name)
        self.system = system
        self.task = None

    def set_deadline(self, deadline):
        """Takes tuple (type, relative, deadline)"""
        self.deadline = dict(zip(["type", "relative", "deadline"], deadline))

    def set_static_priority(self, prio):
        self.static_priority = prio

    def set_preemptable(self, preemptable):
        self.preemptable = preemptable

    def set_basic_task(self, basic_task):
        assert basic_task == True
        self.basic_task = basic_task

    def set_max_activations(self, max_activations):
        assert max_activations == 1
        self.max_activations = max_activations

    def set_autostart(self, autostart):
        self.autostart = autostart

    def fsck(self):
        assert self.task in self.system.tasks

    def dump(self):
        from_function = Function.dump(self)
        fields = ["static_priority", "preemptable", "basic_task", "max_activations", "autostart"]
        from_subtask = dict([(x, getattr(self, x)) for x in fields])
        from_function.update(from_subtask)
        return from_function


