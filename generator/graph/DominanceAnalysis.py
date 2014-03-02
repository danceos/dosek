from generator.graph.Analysis           import Analysis
from generator.graph.common             import dfs, GraphObject, Edge, GraphObjectContainer
from generator.graph.AtomicBasicBlock   import E


class DominanceAnalysis(Analysis, GraphObject):
    """Implements a dominator analysis on the system level control flow
    graph. At the moment Lengauer/Tarjan is implemented (A fast
    algorithm for finding dominators in a flowgraph,
    langauer:79:toplas)

    """
    pass_alias = "dom-tree-system"

    def __init__(self, edge_levels = [E.system_level]):
        Analysis.__init__(self)
        GraphObject.__init__(self, "DominatorTree for [%s]" % repr(edge_levels), root=True)
        self.edge_levels = edge_levels

        self.blocks = None
        self.semi_dominators = None
        self.imm_dominators = None
        self.ancestor = None
        self.parents = None
        self.buckets = None
        self.dfs_count = None
        self.dfs_block_to_number = None

        self.immdom_tree = None

    def requires(self):
        return ["ConstructGlobalCFG"]

    def get_edge_filter(self):
        return self.edge_levels

    def dfs_visitor(self, to_edge, block):
        v = self.dfs_count
        self.dfs_count += 1
        # The parent in the dfs tree
        if to_edge:
            self.parents[v] = self.dfs_block_to_number[to_edge.source]
        else:
            self.parents[v] = 0
        self.blocks[v] = block
        self.dfs_block_to_number[block] = v
        self.semi_dominators[v] = v

    def __eval(self, v):
        a = self.ancestor[v]
        while a != 0:
            if self.semi_dominators[v] > self.semi_dominators[a]:
                v = a
            a = self.ancestor[a]
        return v

    def __link(self, v, w):
        self.ancestor[w] = v

    def do(self):
        # Initialize structures
        count = len(self.system_graph.get_abbs()) + 1
        self.blocks = [None] * count
        self.semi_dominators = [None] * count
        self.imm_dominators =  [0] * count
        self.ancestor = [0] * count
        self.parents = [None] * count
        self.buckets = [[] for _ in range (0, count)]
        self.dfs_count = 1  # Start from 1
        self.dfs_block_to_number = {}
        self.immdom_tree = {}

        StartOS = self.system_graph.find_function("StartOS").entry_abb
        # Get a DFS number for every ABB
        dfs(self.dfs_visitor, lambda edge: edge.isA(self.edge_levels),
            [StartOS])

        for w in reversed(range(2, self.dfs_count)):
            abb_w = self.blocks[w]
            for pred in abb_w.get_incoming_nodes(self.edge_levels):
                v = self.dfs_block_to_number[pred]
                u = self.__eval(v)
                if self.semi_dominators[w] > self.semi_dominators[u]:
                    self.semi_dominators[w] = self.semi_dominators[u]
            # Link block to the semi_dominator candidate
            self.buckets[self.semi_dominators[w]].append(w)
            self.__link(self.parents[w], w)

            for B in self.buckets[self.parents[w]]:
                u = self.__eval(B)
                if self.semi_dominators[u] < self.semi_dominators[B]:
                    self.imm_dominators[B] = u
                else:
                    self.imm_dominators[B] = self.parents[w]
            self.buckets[self.parents[w]] = []

        for w in range(1, self.dfs_count):
            if self.imm_dominators[w] != self.semi_dominators[w]:
                self.imm_dominators[w] = self.imm_dominators[self.imm_dominators[w]]

            self.immdom_tree[self.blocks[w]] = self.blocks[self.imm_dominators[w]]


    # Accessors
    def graph_subobjects(self):
        # All visited Atomic Basic Blocks
        subobject = GraphObjectContainer(label = "Container", color="green")
        abbs = {}
        # Construct the control flow edges
        for abb, immdom in self.immdom_tree.items():
            abbs[abb] = GraphObjectContainer(label = str(abb),
                                             color = 'red',
                                             data = abb.dump())
        for abb, immdom in self.immdom_tree.items():
            if immdom is None:
                continue
            edge = Edge(abbs[immdom], abbs[abb])
            subobject.edges.append(edge)

        subobject.subobjects = abbs.values()
        return [subobject]


