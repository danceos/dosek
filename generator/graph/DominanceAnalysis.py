from generator.graph.Analysis           import Analysis
from generator.graph.common             import dfs, GraphObject, Edge, GraphObjectContainer
from generator.tools                    import stack
from generator.graph.AtomicBasicBlock   import E,S
import logging
from functools import reduce

class DominanceAnalysis(Analysis, GraphObject):
    """Implements a dominator analysis on the system level control flow
    graph. A quadradic algorithm for determining the immdoms is used.

    """
    pass_alias = "dom-tree-system"

    def __init__(self, edge_levels = [E.system_level]):
        Analysis.__init__(self)
        GraphObject.__init__(self, "DominatorTree for [%s]" % repr(edge_levels), root=True)
        self.edge_levels = edge_levels

        self.blocks = None
        self.semi = None
        self.idom = None
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

    def find_dominators(self):
        # Each node is mapped to the set of its dominators
        dom = {}
        start_nodes = set()
        for abb in self.system_graph.get_abbs():
            # The start node dominates itself
            if len(abb.get_incoming_nodes(self.edge_levels)) == 0 and\
                len(abb.get_outgoing_nodes(self.edge_levels)) > 0:
                dom[abb] = set([abb])
                start_nodes.add(abb)
            else:
                dom[abb] = set(self.system_graph.get_abbs())

        changes = True
        while changes:
            changes = False
            for abb in self.system_graph.get_abbs():
                if abb in start_nodes:
                    continue
                dominators = [dom[x] for x in abb.get_incoming_nodes(self.edge_levels)]
                if dominators:
                    intersection = reduce(lambda x, y: x & y, dominators)
                else:
                    intersection = set()
                new = set([abb]) | intersection
                if new != dom[abb]:
                    changes = True
                    dom[abb] = new
        return dom

    def find_imdom(self, abb, dominators, visited, cur):
        imdom = None
        visited.add(cur)
        for pred in cur.get_incoming_nodes(self.edge_levels):
            if pred in dominators:
                return pred
        for pred in cur.get_incoming_nodes(self.edge_levels):
            if pred in visited:
                continue
            ret = self.find_imdom(abb, dominators, visited, pred)
            # There are loops in the system
            if ret != abb or ret == None:
                return ret

    def do(self):
        start_node = self.system_graph.find_function("StartOS").entry_abb
        dom = self.find_dominators()
        self.immdom_tree = {start_node: None}
        add_function = self.system_graph.get_pass("AddFunctionCalls")
        for abb in self.system_graph.get_abbs():
            if abb == start_node:
                continue
            visited = set()
            imdom = self.find_imdom(abb, dom[abb] - set([abb]), visited, abb)
            assert abb != imdom
            if imdom:
                self.immdom_tree[abb] = imdom
            else:
                if add_function.is_relevant_function(abb.function):
                    self.immdom_tree[abb] = start_node


    # Accessors
    def graph_subobjects(self):
        domtree = self.dominator_tree()
        # All visited Atomic Basic Blocks
        _all = GraphObjectContainer.from_dict("DominatorTree[All]", "red",
                                              domtree.tree)
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
        return DominatorTree(root, tree, self.edge_levels, sparse=False)

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
        return DominatorTree(root, tree, self.edge_levels)

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
            region = DominatorTree(root, tree, self.edge_levels)
            # For each chilren of root, we slice the subtree into a new dict
            for child in tree[root]:
                ws.push((child, tree))
            ret.append(region)
        return ret


class DominatorTree:
    def __init__(self, root, tree, edge_levels, sparse=True):
        self.root = root
        self.tree = self.__slice_subtree(tree)
        self.leaf = [k for k,v in self.tree.items() if v == []]
        self.edge_levels = edge_levels
        self.sparse = sparse
        self.__dominance_border = {}

        # dict that maps a child to its parent (same information as .tree)
        self.__back_tree = {}
        for parent, children in self.tree.items():
            for child in children:
                self.__back_tree[child] = parent

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
        return "<DominatorTree root:%s, size: %d>" % (self.root, len(self))

    def __contains__(self, abb):
        return abb in self.tree

    def get_imm_dom(self, abb):
        """Get the ImmDom of abb"""
        return self.__back_tree[abb]

    def get_imm_dominated(self, abb):
        """Get all blocks that are directly dominated by abb"""
        return self.tree[abb]

    def dominance_border(self, abb):
        """Get the dominance border of tree"""
        assert not self.sparse, "Can compute dominance border only on none sparse dominator tree"
        # Return cached dominance border
        if abb in self.__dominance_border:
            return self.__dominance_border[abb]

        dc = set()
        for succ in abb.get_outgoing_nodes(self.edge_levels):
            # All direct neighbours that are not directly dominated by us
            if self.get_imm_dom(succ) != abb:
                dc.add(succ)

        for direct_dom in self.get_imm_dominated(abb):
            for candidate in self.dominance_border(direct_dom):
                if self.get_imm_dom(candidate) != abb and candidate != abb:
                    dc.add(candidate)

        # Cache the result
        self.__dominance_border[abb] = dc

        return dc
