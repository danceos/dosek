from generator.graph.common import GraphObject, Edge

class Function(GraphObject):
    def __init__(self, functionname):
        GraphObject.__init__(self, functionname, color = "brown")
        self.function_name = functionname
        self.task = None
        self.subtask = None
        self.abbs = []
        self.entry_abb = None
        self.exit_abb = None


    def graph_subobjects(self):
        return self.abbs

    def graph_edges(self):
        return [Edge(self, self.entry_abb, 'entry')]

    def dump(self):
        return {"function_name": self.function_name }

    def get_syscalls(self):
        return [x for x in self.abbs
                if x.type != 'computation']

    def add_atomic_basic_block(self, abb):
        abb.function = self
        self.abbs.append(abb)

    def set_entry_abb(self, abb):
        assert(abb in self.abbs)
        self.entry_abb = abb

    def set_exit_abb(self, abb):
        assert(abb in self.abbs)
        self.exit_abb = abb

    def remove_abb(self, abb):
        # Remove ABB from list of atomic basic blocks
        self.abbs = [x for x in self.abbs if x != abb]
        # Remove all outgoing edge
        for out in abb.outgoing_edges:
            assert out.source == abb
            target = out.target
            abb.remove_cfg_edge(target)

        # Remove all incoming edges
        for incoming in abb.incoming_edges:
            assert incoming.target == abb
            source = incoming.source
            source.remove_cfg_edge(abb)


    def __repr__(self):
        return "<Function %s>" %self.function_name
