from generator.graph.common import GraphObject, Edge

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

    def graph_edges(self):
        return self.outgoing_edges

    def add_cfg_edge(self, target, type = 'local'):
        edge = ControlFlowEdge(self, target, type = type)
        self.outgoing_edges.append(edge)
        target.incoming_edges.append(edge)

    def get_outgoing_edges(self, type):
        return [x for x in self.outgoing_edges if x.type == type]

    def get_incoming_edges(self, type):
        return [x for x in self.incoming_edges if x.type == type]

    def get_outgoing_nodes(self, type):
        return [x.target for x in self.outgoing_edges if x.type == type]

    def get_incoming_nodes(self, type):
        return [x.source for x in self.incoming_edges if x.type == type]

    def definite_after(self, type):
        nodes = self.get_outgoing_nodes(type)
        assert len(nodes) == 1
        return nodes[0]

    def definite_before(self, type):
        nodes = self.get_incoming_nodes(type)
        assert len(nodes) == 1
        return nodes[0]


    def remove_cfg_edge(self, to_abb, type = 'local'):
        for edge in self.outgoing_edges:
            if edge.target == to_abb and edge.type == type:
                self.outgoing_edges.remove(edge)
                to_abb.incoming_edges.remove(edge)

    def make_it_a_syscall(self, type, arguments):
        if type.startswith("OSEKOS_"):
            type = type[len("OSEKOS_"):]
        self.type = type
        args = []
        # Make the string arguments references to system objects
        for x in arguments:
            if x.startswith("OSEKOS_TASK_Struct_"):
                handler_name = x[len("OSEKOS_TASK_Struct_"):]
                x = self.system.functions["OSEKOS_TASK_" + handler_name]
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
        if self.type == "computation":
            return {"type": self.type}
        return {'type': self.type,
                'arguments': repr(self.arguments)}

    def __repr__(self):
        return "ABB%d"%(self.abb_id)


class ControlFlowEdge(Edge):
    """Task level control flow edges are possible control flow transitions
       that stay on the task level (aka. always on the same stack/same task
       context)"""

    def __init__(self, source, target, type = 'local'):
        color = 'black'
        if type == 'global':
            color = 'blue'
        if type == 'irq':
            color = 'red'

        Edge.__init__(self, source, target, color=color)
        self.type = type

    def is_local(self):
        """Returns wheter this is a local edge. A local edge stays always on the task level"""
        return self.type == 'local'

    def __repr__(self):
        return "<%s %s -> %s (%s)>"%(self.__class__.__name__, self.source, self.target, self.type)
