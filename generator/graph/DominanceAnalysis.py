from generator.graph.Analysis           import Analysis
from generator.graph.common             import dfs, GraphObject, Edge, GraphObjectContainer
from generator.tools                    import stack
from generator.graph.AtomicBasicBlock   import E,S
import logging

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
        _all = GraphObjectContainer.from_dict("DominatorTree[All]", "red",
                                              self.dominator_tree().tree)
        _syscall = GraphObjectContainer.from_dict("DominatorTree[Syscall]", "red",
                                                  self.syscall_dominator_tree().tree)
        _all.set_color("green")
        _syscall.set_color("green")

        ret = [_all, _syscall]
        regions = self.syscall_dominance_regions()
        max_region = max([len(x) for x in regions])
        for region in regions:
            if len(region) in (1, max_region):
                continue
            _region = GraphObjectContainer.from_dict(repr(region), "red",
                                                     region.tree)
            _region.set_color("green")
            ret.append(_region)

        logging.info(" + Found %d syscall regions (interesting: %d)",
                     len(regions), len(ret) - 2)
        return ret

    def __reverse_tree(self, _tree):
        tree = {}
        root = None
        for _from, _to in _tree.items():
            tree.setdefault(_from, [])

            if _to != None:
                tree.setdefault(_to, [])
                tree[_to].append(_from)
            else:
                assert root == None
                root = _from
        return root, tree

    def dominator_tree(self):
        root, tree = self.__reverse_tree(self.immdom_tree)
        return DominatorTree(root, tree)

    def syscall_dominator_tree(self):
        """The dominator tree filtered to only contian real syscalls"""
        syscall_immdom_tree = {}
        for _from in self.immdom_tree.keys():
            if _from.syscall_type.isRealSyscall() or \
               _from.isA(S.StartOS):
                _to = self.immdom_tree[_from]
                while _to:
                    if _to.syscall_type.isRealSyscall() or \
                       _to.isA(S.StartOS):
                        break
                    _to = self.immdom_tree[_to]
                syscall_immdom_tree[_from] = _to
        root, tree = self.__reverse_tree(syscall_immdom_tree)
        return DominatorTree(root, tree)

    def syscall_dominance_regions(self):
        """Returns all subtrees of the syscall_immdom_tree"""
        syscall_tree = self.syscall_dominator_tree()

        # Find all regions
        ws = stack()
        ws.push((syscall_tree.root, syscall_tree.tree))
        ret = []
        while not ws.isEmpty():
            root, tree = ws.pop()
            # Construct current region
            region = DominatorTree(root, tree)
            # For each chilren of root, we slice the subtree into a new dict
            for child in tree[root]:
                ws.push((child, tree))
            ret.append(region)
        return ret

class DominatorTree:
    def __init__(self, root, tree):
        self.root = root
        self.tree = self.__slice_subtree(tree)
        self.leaf = [k for k,v in self.tree.items() if v == []]

    def __slice_subtree(self, tree):
        "Slices all entries of the tree dict, that are below root"
        ret = {}
        ws = stack()
        ws.push(self.root)
        while not ws.isEmpty():
            cur = ws.pop()
            ret[cur]  = list(tree[cur])
            ws.extend(tree[cur])
        return ret

    def __len__(self):
        return len(self.tree)

    def __repr__(self):
        return "<DominanceRegion root:%s, size: %d>" % (self.root, len(self))

    def __contains__(self, abb):
        return abb in self.tree

