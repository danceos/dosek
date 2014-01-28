import sys

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
            if data != None:
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

def dfs(block_functor, take_edge_functor, start_abbs):
    """Performs a depth first search. It first executes block_functor on a
       block, then collects all outgoing edges, that satisfy the
       take_edge_functor. All child blocks are visitied in the
       same manner. No block is visited more than once. The DFS
       starts with the list of start_abs blocks.

       The block_functor takes an _edge_ that leads to a _block_
    """
    visited = set()
    # First in start_abs is the first to be popped
    working_stack = []
    for abb in start_abbs:
        working_stack.append(tuple([None, abb]))

    while len(working_stack) > 0:
        leading_edge, current_block = working_stack.pop()
        # Call the block_functor
        block_functor(leading_edge, current_block)
        for edge in current_block.outgoing_edges:
            child = edge.target
            # Already visited or in working_stack
            if child in visited:
                continue
            # Check if edge satisfies condition
            if not take_edge_functor(edge):
                continue
            # PUSH item onto stack
            working_stack.append((edge, child))
            visited.add(child)

class FixpointIteraton:
    def __init__(self, starting_objects):
        # Start fixpoint iteration with those objects
        self.working_stack = list(reversed(starting_objects))
        self.stopped = False

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
        while len(self.working_stack) > 0 and not self.stopped:
            item = self.working_stack.pop()
            functor(self, item)

def is_local_edge(edge):
    return edge.is_local()


# Hook for coloured tracebacks on the console :-)
def myexcepthook(type, value, tb):
    import traceback
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import TerminalFormatter

    tbtext = ''.join(traceback.format_exception(type, value, tb))
    lexer = get_lexer_by_name("pytb", stripall=True)
    formatter = TerminalFormatter()
    sys.stderr.write(highlight(tbtext, lexer, formatter))

sys.excepthook = myexcepthook
