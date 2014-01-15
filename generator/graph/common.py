class GraphObject:
    """Any Object that is used within the graph an can be dumped as dot"""
    def __init__(self, label, color = "black", root = False):
        self.__label = label
        self.__color = color
        self.__root = root

    def graph_dot_id(self):
        return "cluster"+self.__class__.__name__ + "_%x"%(abs(hash(self))% (1 << 24))

    def graph_subobjects(self):
        return []

    def graph_edges(self):
        """Returns edges that originate in this object"""
        return []

    def graph_description(self):
        if hasattr(self, "dump"):
            data = self.dump()
            lines = ["%s: %s" % x for x in data.items()]
            return "\\l".join(lines)
        return self.__class__.__name__

    def dump_as_dot(self, current_depth = 0):
        edges = []
        if self.__root:
            ret = "digraph foo {\n"
            ret += "  compound = true;\n"
        else:
            ret = ("  "*current_depth) + "subgraph " + self.graph_dot_id() + "{\n"

        ret += ("  "*(current_depth+1))+ "label = \""+self.__label + "\";\n"
        ret += ("  "*(current_depth+1))+ "color = "+self.__color + ";\n"

        ret += ("  "*(current_depth+1)) + "Node_"+self.graph_dot_id()\
               +"[label=\""+self.graph_description()+"\",shape=box];\n"
        # Collect all Edges from this object
        edges.extend(self.graph_edges())

        for subobject in self.graph_subobjects():
            text, edges_ = subobject.dump_as_dot(current_depth + 1)
            # Merge with edges from lower levels
            edges.extend(edges_)
            ret += text
            ret += "\n"

        if self.__root:
            for edge in edges:
                ret += ("  "*(current_depth+1)) + edge.dump_as_dot() + "\n"

        ret += ("  "*current_depth) + "}\n"

        if self.__root:
            return ret
        else:
            return ret, edges


class Edge:
    def __init__(self, source, target, label='', color = 'black'):
        assert hasattr(source, "graph_dot_id")
        assert hasattr(target, "graph_dot_id")
        self.source = source
        self.target = target
        self.label = label
        self.color = color

    def dump_as_dot(self):
        ret = "Node_%s -> Node_%s[ltail=%s,lhead=%s,label=\"%s\",color=%s];" %(
            self.source.graph_dot_id(),
            self.target.graph_dot_id(),
            self.source.graph_dot_id(),
            self.target.graph_dot_id(),
            self.label,
            self.color,
        )
        return ret

    def __repr__(self):
        return "<%s %s -> %s>"%(self.__class__.__name__, self.source, self.target)
