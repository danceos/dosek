from generator.graph.Function import Function
from generator.graph.SystemObject import SystemObject


class Subtask(Function, SystemObject):
    subtask_id_counter = 0
    def __init__(self, system_graph, name, function_name, config):
        Function.__init__(self, function_name)
        SystemObject.__init__(self, name, config)

        self.subtask_id = Subtask.subtask_id_counter
        Subtask.subtask_id_counter += 1
        self.system_graph = system_graph
        self.name = name
        self.task = None
        self.subtask = self

    def is_user_thread(self):
        """Returns True for user threads"""
        return not self.conf.is_isr

    def is_real_thread(self):
        """Returns True for user threads, and False for the Idle Thread"""
        return self.conf.static_priority != 0 and not self.conf.is_isr

    def get_stack_size(self):
        """Returns the size of the user stack"""
        return str(4096) # FIXME: Should be user configurable

    @property
    def static_priority(self):
        return self.conf.static_priority

    def fsck(self):
        assert self.task in self.system_graph.tasks

    def dump(self):
        from_function = Function.dump(self)
        fields = ["static_priority", "preemptable", "basic_task", "max_activations", "autostart"]
        from_subtask = dict([(x, getattr(self.conf, x)) for x in fields])
        from_function.update(from_subtask)
        return from_function

    def __repr__(self):
        isr = ""
        if self.conf.is_isr:
            isr = " ISR"
        return "<Subtask %s%s>" %(self.name, isr)

