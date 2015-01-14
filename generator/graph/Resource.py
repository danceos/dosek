from .SystemObject import SystemObject

class Resource(SystemObject):
    def __init__(self, system_graph, name, subtasks, conf):
        """Constructs a resource that belongs to system (SystemGraph), that
           has a name and the tasks can obtain this resource"""
        SystemObject.__init__(self, name, conf)
        self.system_graph = system_graph
        self.name = name
        self.subtasks = subtasks

    def __repr__(self):
        return "<Res %s pri:%s>" %(self.name, self.conf.static_priority)
