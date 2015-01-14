class SystemObject:
    """An OSEK system object is something that is instantiated in the OIL
       file. Each system object has a configuration and an
       implementation. SystemObjects are tasks, subtasks, etc."""

    name = None
    """Each system object has a name, that is unique in its class of objects."""

    conf = None
    """Configuration stated in the OIL file"""

    impl = None
    """Some Object that instantiates this SystemObject in the resulting system."""

    def __init__(self, name, conf):
        self.name = name
        self.conf = conf
