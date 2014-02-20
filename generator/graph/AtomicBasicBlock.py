from generator.graph.common import GraphObject, Edge

class E:
    """All used edge types"""
    function_level = 1
    task_level = 2
    system_level = 3
    irq_level = 4

    state_transition = 10

    @classmethod
    def to_string(cls, level):
        ret = {1: 'function_level',
               2: 'task_level',
               3: 'system_level',
               4: 'irq_level',
               10: 'state_transition'}
        return ret[level]

    @classmethod
    def color(cls, level):
        ret = {1: 'green',
               2: 'black',
               3: 'blue',
               4: 'red',
               10: 'black'}
        return ret[level]


class ControlFlowEdge(Edge):
    """Task level control flow edges are possible control flow transitions
       that stay on the task level (aka. always on the same stack/same task
       context)"""

    def __init__(self, source, target, level = E.task_level):
        Edge.__init__(self, source, target, color = E.color(level))
        self.level = level

    def __repr__(self):
        return "<%s %s -> %s (%s)>"%(self.__class__.__name__, self.source,
                                     self.target, E.to_string(self.level))

class AtomicBasicBlock(GraphObject):
    def __init__(self, system, abb_id):
        GraphObject.__init__(self, "ABB%d" %(abb_id), color="red")
        self.abb_id = abb_id
        self.system = system
        self.function = None
        self.artificial = False
        self.outgoing_edges = []
        self.incoming_edges = []

        self.type = "computation"
        self.arguments = []
        # This is set by the DynamicPriorityAnalysis
        self.dynamic_priority = None

    def graph_edges(self):
        return self.outgoing_edges

    def add_cfg_edge(self, target, level):
        assert isinstance(level, int)
        assert not target in self.get_outgoing_edges(level), \
            "Cannot add edge of the same type twice"
        edge = ControlFlowEdge(self, target, level)
        self.outgoing_edges.append(edge)
        target.incoming_edges.append(edge)

    def get_outgoing_edges(self, level):
        assert isinstance(level, int)
        return [x for x in self.outgoing_edges if x.level == level]

    def get_incoming_edges(self, level):
        assert isinstance(level, int)
        return [x for x in self.incoming_edges if x.level == level]

    def get_outgoing_nodes(self, level):
        assert isinstance(level, int)
        return [x.target for x in self.outgoing_edges if x.level == level]

    def get_incoming_nodes(self, level):
        assert isinstance(level, int)
        return [x.source for x in self.incoming_edges if x.level == level]

    def definite_after(self, level):
        nodes = self.get_outgoing_nodes(level)
        assert len(nodes) == 1
        return nodes[0]

    def definite_before(self, level):
        nodes = self.get_incoming_nodes(level)
        assert len(nodes) == 1
        return nodes[0]


    def remove_cfg_edge(self, to_abb, level):
        assert isinstance(level, int)
        for edge in self.outgoing_edges:
            if edge.target == to_abb and edge.level == level:
                self.outgoing_edges.remove(edge)
                to_abb.incoming_edges.remove(edge)
                return edge

    def make_it_a_syscall(self, call, arguments):
        if call.startswith("OSEKOS_"):
            call = call[len("OSEKOS_"):]
        self.type = call
        args = []
        # Make the string arguments references to system objects
        for x in arguments:
            if type(x) == str:
                if x.startswith("OSEKOS_TASK_Struct_"):
                    handler_name = x[len("OSEKOS_TASK_Struct_"):]
                    x = self.system.functions["OSEKOS_TASK_" + handler_name]
                elif x.startswith("OSEKOS_RESOURCE_Struct_"):
                    res_name = x[len("OSEKOS_RESOURCE_Struct_"):]
                    x = self.system.resources[res_name]
                elif x.startswith("OSEKOS_ALARM_Struct_"):
                    alarm_name = x[len("OSEKOS_ALARM_Struct_"):]
                    x = alarm_name
            args.append(x)
        self.arguments = args

    def fsck(self):
        assert self.system.find_abb(self.abb_id) == self
        assert self.function != None
        assert self in self.function.abbs
        for edge in self.outgoing_edges:
            assert edge.source == self
            assert edge in edge.target.incoming_edges
            # Target Edge can be found
            assert self.system.find_abb(edge.target.abb_id) == edge.target
        for edge in self.incoming_edges:
            assert edge.target == self
            assert edge in edge.source.outgoing_edges
            # Source abb can be found
            assert self.system.find_abb(edge.source.abb_id) == edge.source

    def dump(self):
        task = None
        if self.function.subtask:
            task = self.function.subtask.name

        if self.type == "computation":
            return {"id": repr(self),
                    "prio": str(self.dynamic_priority),
                    'task': task}
        return {'id': repr(self),
                'arguments': repr(self.arguments),
                'prio': str(self.dynamic_priority),
                'task': task}

    def __repr__(self):
        if self.type == "computation":
            return "ABB%d" % (self.abb_id)
        return "ABB%d/%s"%(self.abb_id, self.type)

    def path(self):
        """Returns a string that should be enable the user to find the atomic
           basic block"""
        return "%s/%s/ABB%s/%s" %(self.function.subtask, self.function,
                                  self.abb_id, self.type)


