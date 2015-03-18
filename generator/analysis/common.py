import sys
from generator.tools import wrap_in_list, stack, IntEnum, unique
import collections
import logging

class GraphObject:
    """Any Object that is used within the graph an can be dumped as dot"""
    def __init__(self, label, color = "black", root = False):
        self.__label = label
        self.__color = color
        self.__root = root

    def set_color(self, color):
        self.__color = color

    def graph_dot_id(self):
        return "cluster"+self.__class__.__name__ + "_%x"%(id(self))

    def graph_subobjects(self):
        return []

    def graph_edges(self):
        """Returns edges that originate in this object"""
        return []

    def graph_description(self):
        if hasattr(self, "dump"):
            data = self.dump()
            if data != None:
                if type(data) == str:
                    return data.replace("\n", "\\l")
                lines = sorted(["%s: %s" % x for x in data.items()])
                return "\\l".join(lines) + "\\l"
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
            if not hasattr(subobject, "dump_as_dot"):
                continue
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

@unique
class NodeType(IntEnum):
    unspecified = -1

@unique
class EdgeType(IntEnum):
    unspecified = -1

class Node(GraphObject):
    def __init__(self, edge_factory, label, color, root = False):
        GraphObject.__init__(self, label, color, root)
        self.outgoing_edges = []
        self.incoming_edges = []
        self.edge_factory   = edge_factory
        self.aux = None

    current_edge_filter = None
    @classmethod
    def set_edge_filter(cls, edge_filter):
        cls.current_edge_filter = edge_filter

    def check_edge_filter(self, level):
        assert isinstance(level, IntEnum) or isinstance(level, collections.Iterable)
        assert not self.current_edge_filter \
            or level in self.current_edge_filter\
            or (isinstance(level, collections.Iterable) \
                and set(level).issubset(self.current_edge_filter)),\
            "Tried to access edge of type %s, but is prohibited by edge filter"\
            % (self.current_edge_filter)

    def graph_edges(self):
        if self.current_edge_filter:
            return [edge for edge in self.outgoing_edges
                    if edge.level in self.current_edge_filter]
        return self.outgoing_edges

    def add_cfg_edge(self, target, level):
        self.check_edge_filter(level)
        assert not target in self.get_outgoing_edges(level), \
            "Cannot add edge of the same type twice"
        edge = self.edge_factory(self, target, level)
        self.outgoing_edges.append(edge)
        target.incoming_edges.append(edge)

    def get_outgoing_edges(self, level):
        self.check_edge_filter(level)
        return [x for x in self.outgoing_edges if x.isA(level)]

    def get_incoming_edges(self, level):
        self.check_edge_filter(level)
        return [x for x in self.incoming_edges if x.isA(level)]

    def get_outgoing_nodes(self, level):
        self.check_edge_filter(level)
        return [x.target for x in self.outgoing_edges if x.isA(level)]

    def get_incoming_nodes(self, level):
        self.check_edge_filter(level)
        return [x.source for x in self.incoming_edges if x.isA(level)]

    def get_neighbours(self, level):
        self.check_edge_filter(level)
        pred = set([x.source for x in self.incoming_edges if x.isA(level)])
        succ = set([x.target for x in self.outgoing_edges if x.isA(level)])
        return (pred | succ) - set([self])

    def has_edge_to(self, abb, level):
        """Returns the edge of level to an specific abb"""
        self.check_edge_filter(level)

        for edge in self.outgoing_edges:
            if edge.isA(level) and edge.target == abb:
                return edge

    def definite_after(self, level):
        nodes = self.get_outgoing_nodes(level)
        assert len(nodes) == 1
        return nodes[0]

    def definite_before(self, level):
        nodes = self.get_incoming_nodes(level)
        assert len(nodes) == 1
        return nodes[0]

    def has_single_successor(self, level):
        es = self.get_outgoing_edges(level)
        return len(es) == 1

    def has_single_predecessor(self, level):
        es = self.get_incoming_edges(level)
        return len(es) == 1

    def remove_cfg_edge(self, to_abb, level):
        self.check_edge_filter(level)
        for edge in self.outgoing_edges:
            if id(edge.target) == id(to_abb) and edge.isA(level):
                self.outgoing_edges.remove(edge)
                to_abb.incoming_edges.remove(edge)
                return edge

    def fsck(self):
        for edge in self.outgoing_edges:
            assert edge.source == self
            assert edge in edge.target.incoming_edges
        for edge in self.incoming_edges:
            assert edge.target == self
            assert edge in edge.source.outgoing_edges


class Edge:
    def __init__(self, source, target, level=EdgeType.unspecified, label='', 
                 color = 'black'):
        assert hasattr(source, "graph_dot_id"), source
        assert hasattr(target, "graph_dot_id"), target
        self.source = source
        self.target = target
        self.label = label
        self.color = color
        self.level = level
        self.aux = None

    def dump_as_dot(self):
        ret = ""
        ret += "Node_%s -> Node_%s[minlen=3,ltail=%s,lhead=%s,label=\"%s\",color=%s];" %(
            self.source.graph_dot_id(),
            self.target.graph_dot_id(),
            self.source.graph_dot_id(),
            self.target.graph_dot_id(),
            self.label,
            self.color,
        )
        return ret

    def isA(self, edge_level):
        if self.level == edge_level:
            return True
        if isinstance(edge_level, collections.Iterable):
            return self.level in edge_level
        return False

    def __repr__(self):
        return "<%s %s -> %s (%s)>"%(self.__class__.__name__, self.source,
                                     self.target, self.level.name)

def dfs(block_functor, take_edge_functor, start_abbs):
    """Performs a depth first search. It first executes block_functor on a
       block, then collects all outgoing edges, that satisfy the
       take_edge_functor. All child blocks are visited in the
       same manner. No block is visited more than once. The DFS
       starts with the list of start_abs blocks.

       The block_functor takes an _edge_ that leads to a _block_
    """
    visited = set()
    # First in start_abs is the first to be popped
    working_stack = stack()
    for abb in start_abbs:
        working_stack.append(tuple([None, abb]))

    while working_stack:
        leading_edge, current_block = working_stack.pop()
        # Call the block_functor
        block_functor(leading_edge, current_block)
        out_edges = sorted(current_block.outgoing_edges,
                           key = lambda e: e.target.abb_id)
        for edge in reversed(out_edges):
        #for edge in out_edges:
            child = edge.target
            # Already visited or in working_stack
            if child in visited:
                continue
            # Check if edge satisfies condition
            if not take_edge_functor(edge):
                continue
            # PUSH item onto stack
            working_stack.push((edge, child))
            visited.add(child)

class FixpointIteration:
    def __init__(self, starting_objects):
        # Start fixpoint iteration with those objects
        self.working_stack = list(reversed(starting_objects))
        self.stopped = False

    def __contains__(self, item):
        return item in self.working_stack

    def enqueue_soon(self, item = None, items = None):
        if item and not item in self.working_stack:
            self.working_stack.append(item)
        if items:
            for x in items:
                self.enqueue_soon(x)

    def enqueue_later(self, item = None, items = None):
        if item and not item in self.working_stack:
            self.working_stack = [item] + self.working_stack
        if items:
            for x in items:
                self.enqueue_later(x)

    def stop(self):
        self.stopped = True

    def do(self, functor):
        """Functor is called with the fixpoint iteration and the current object."""
        steps = 0
        while len(self.working_stack) > 0 and not self.stopped:
            item = self.working_stack.pop()
            functor(self, item)
            steps += 1
            if steps % 1000 == 0:
                logging.info(" %d steps (%d in queue)", steps, len(self.working_stack))



class GraphObjectContainer(GraphObject):
    def __init__(self, label, color, subobjects = None, edges = None, data = None, root = False):
        GraphObject.__init__(self, label, color, root)
        if not edges:
            edges = []
        if not subobjects:
            subobjects = []
        self.data = data
        self.subobjects = subobjects
        self.edges = edges

    def dump(self):
        return self.data

    def graph_subobjects(self):
        return self.subobjects

    def graph_edges(self):
        return self.edges

    @staticmethod
    def from_dict(label, color, edge_dict, reverse = False):
        subobject = GraphObjectContainer(label = label, color="black")
        objs = {}
        # Construct the control flow edges
        for _from, _ in edge_dict.items():
            objs[_from] = GraphObjectContainer(label = str(_from),
                                             color = color,
                                             data = _from.dump())
        for _from, targets in edge_dict.items():
            if targets is None:
                continue
            targets = wrap_in_list(targets)
            for _to in targets:
                edge = Edge(objs[_from], objs[_to])
                if reverse:
                    edge.source, edge.target = edge.target, edge.source
                subobject.edges.append(edge)

        subobject.subobjects = objs.values()
        return subobject


