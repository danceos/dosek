from .SystemObject import SystemObject

class Event(SystemObject):
    def __init__(self, system_graph, name, task, event_id, conf):
        """Constructs a event that belongs to system (SystemGraph), that
           has a name and is owned by one task"""
        SystemObject.__init__(self, name, conf)
        self.system_graph = system_graph
        self.name = name
        self.task = task
        self.event_id = event_id
        self.__event_mask = (1 << event_id)

    @property
    def event_mask(self):
        return self.__event_mask

    @event_mask.setter
    def event_mask(self, value):
        self.__event_mask = value

    def __repr__(self):
        return "<Event %s task:%s>" %(self.name, self.task)

    @staticmethod
    def combine_event_masks(event_list):
        """Generate a event mask"""
        x = 0
        for event in event_list:
            x |= event.event_mask
        return x

