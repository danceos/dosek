from generator.graph.Function import Function

class Subtask(Function):
    subtask_id_counter = 0
    def __init__(self, system_graph, name, function_name):
        Function.__init__(self, function_name)
        self.subtask_id = Subtask.subtask_id_counter
        Subtask.subtask_id_counter += 1
        self.system_graph = system_graph
        self.name = name
        self.task = None
        self.subtask = self
        self.deadline = None
        self.static_priority = -1
        self.preemptable = False
        self.basic_task = True
        self.max_activations = 1
        self.autostart = False
        self.is_isr = False
        self.isr_device = None

    def set_deadline(self, deadline):
        """Takes tuple (type, relative, deadline)"""
        self.deadline = dict(list(zip(["type", "relative", "deadline"], deadline)))

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

    def set_is_isr(self, value, device = None):
        self.is_isr = value
        self.isr_device = device

    def is_real_thread(self):
        """Returns True for user threads, and False for the Idle Thread"""
        return self.static_priority != 0 and not self.is_isr

    def get_stack_size(self):
        """Returns the size of the user stack"""
        return str(4096) # FIXME: Should be user configurable

    def fsck(self):
        assert self.task in self.system_graph.tasks

    def dump(self):
        from_function = Function.dump(self)
        fields = ["static_priority", "preemptable", "basic_task", "max_activations", "autostart"]
        from_subtask = dict([(x, getattr(self, x)) for x in fields])
        from_function.update(from_subtask)
        return from_function

    def __repr__(self):
        isr = ""
        if self.is_isr:
            isr = " ISR"
        return "<Subtask %s%s>" %(self.name, isr)

