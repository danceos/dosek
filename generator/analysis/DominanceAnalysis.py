from .Analysis           import Analysis
from .common             import dfs, GraphObject, Edge, GraphObjectContainer
from generator.tools                    import stack
from .AtomicBasicBlock   import E,S
from .Function           import Function
import logging
from functools import reduce

class DominanceAnalysis(Analysis, GraphObject):
    """Implements a dominator analysis on the system level control flow
    graph. A quadradic algorithm for determining the immdoms is used.

    """
    pass_alias = "dom-tree-system"

    def __init__(self, forward=True, edge_levels = [E.system_level]):
        Analysis.__init__(self)
        GraphObject.__init__(self, "DominatorTree for [%s]" % repr(edge_levels), root=True)
        self.edge_levels = edge_levels

        self.immdom_tree = None
        self.forward = forward

    def requires(self):
        return ["ConstructGlobalCFG"]

    def get_edge_filter(self):
        return self.edge_levels

    def incoming(self, node):
        if self.forward:
            return node.get_incoming_nodes(self.edge_levels)
        else:
            return node.get_outgoing_nodes(self.edge_levels)

    def outgoing(self, node):
        if self.forward:
            return node.get_outgoing_nodes(self.edge_levels)
        else:
            return node.get_incoming_nodes(self.edge_levels)

    def find_dominators(self):
        # Each node is mapped to the set of its dominators
        dom = {}
        start_nodes = set()
        for abb in self.nodes:
            # The start node dominates itself
            if len(self.incoming(abb)) == 0 and\
                len(self.outgoing(abb)) > 0:
                dom[abb] = set([abb])
                start_nodes.add(abb)
            elif len(self.incoming(abb)) == 0 and len(self.outgoing(abb)) == 0:
                pass
            else:
                dom[abb] = set(self.nodes)

        changes = True
        while changes:
            changes = False
            for abb in self.nodes:
                if abb in start_nodes:
                    continue
                if not abb in dom:
                    continue
                dominators = [dom[x] for x in self.incoming(abb)]
                if dominators:
                    intersection = reduce(lambda x, y: x & y, dominators)
                else:
                    intersection = set()
                new = set([abb]) | intersection
                if new != dom[abb]:
                    changes = True
                    dom[abb] = new
        return start_nodes, dom

    def find_imdom(self, abb, dominators, visited, cur):
        imdom = None
        visited.add(cur)
        # Is one of the direct predecessors a dominator?
        # -> Return it
        for pred in self.incoming(cur):
            if pred in dominators:
                return pred

        # Otherwise: Depth-first search!
        for pred in self.incoming(cur):
            if pred in visited:
                continue
            ret = self.find_imdom(abb, dominators, visited, pred)
            # If we have found an immediate dominator, we return
            # it. Otherwise we use the next possible path.
            if ret:
                return ret
        # On this path we found a loop
        return None

    def do(self, nodes=None, is_entry = lambda x: x.isA(S.StartOS)):
        if nodes:
            self.nodes = nodes
        else:
            self.nodes = self.system_graph.abbs

        start_nodes, dom = self.find_dominators()

        StartOS = [x for x in start_nodes if is_entry(x)][0]
        assert StartOS
        self.immdom_tree = dict()
        for x in start_nodes:
            if x == StartOS:
                self.immdom_tree[x] = None
            else:
                self.immdom_tree[x] = StartOS

        for abb in dom:
            if abb in start_nodes:
                continue
            visited = set()
            dominators = dom[abb] - set([abb])
            imdom = self.find_imdom(abb, dominators, visited, abb)
            assert abb != imdom and imdom != None
            self.immdom_tree[abb] = imdom


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
            tree.setdefault(_from, list())

            if _to != None:
                tree.setdefault(_to, list())
                tree[_to].append(_from)
            else:
                assert root == None
                root = _from
        return root, tree

    def dominator_tree(self):
        root, tree = self.__reverse_tree(self.immdom_tree)
        assert root
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
