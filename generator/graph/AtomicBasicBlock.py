from generator.graph.common import GraphObject, Edge

class AtomicBasicBlock(GraphObject):
    def __init__(self, system, abb_id):
        GraphObject.__init__(self, "ABB%d" %(abb_id), color="red")
        self.abb_id = abb_id
        self.system = system
        self.function = None
        self.outgoing_edges = []
        self.incoming_edges = []


    def graph_edges(self):
        return self.outgoing_edges

    def set_guard(self, guard):
        self.guard = guard

    def add_cfg_edge(self, target):
        edge = ControlFlowEdge(self, target)
        self.outgoing_edges.append(edge)
        target.incoming_edges.append(edge)

    def get_outgoing_edges(self, type):
        return [x for x in self.outgoing_edges if x.type == type]

    def get_incoming_edges(self, type):
        return [x for x in self.incoming_edges if x.type == type]

    def remove_cfg_edge(self, to_abb):
        for edge in self.outgoing_edges:
            if edge.target == to_abb:
                self.outgoing_edges.remove(edge)
                to_abb.incoming_edges.remove(edge)

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


    def __repr__(self):
        return "ABB%d"%(self.abb_id)


class ControlFlowEdge(Edge):
    """Task level control flow edges are possible control flow transitions
       that stay on the task level (aka. always on the same stack/same task
       context)"""

    def __init__(self, source, target, type = 'local'):
        Edge.__init__(self, source, target, color='black')
        self.type = type

