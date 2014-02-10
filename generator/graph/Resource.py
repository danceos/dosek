class Resource:
    def __init__(self, system, name, tasks):
        """Constructs a resource that belongs to system (SystemGraph), that
           has a name and the tasks can obtain this resource"""
        self.system = system
        self.name = name
        self.subtasks = []
        for t in tasks:
            subtask = self.system.get_subtask(t)
            assert subtask, "Subtask %s not found, that uses resource %s" % (t, name)
            self.subtasks.append(subtask)
        # FIXME: Revalidate this when supporting more than one resource
        assert self.name == "RES_SCHEDULER", "Only RES_SCHEDULER is supported at the very moment"
        self.static_priority = max([t.static_priority for t in self.subtasks]) + 1

    def __repr__(self):
        return "<Res %s pri:%d>" %(self.name, self.static_priority)
