import logging
from .Analysis import Analysis, FixpointIteration
from .AtomicBasicBlock import E, S
from .Function import Function
from .DominanceAnalysis import DominanceAnalysis
from generator.tools import panic, stack
from collections import namedtuple

class ABBMergePass(Analysis):
    """This pass simplifies the CFG, mergeing ABBs."""
    class MergeStatistics:
        """ Just a simple statistics helper"""
        def __init__(self):
            self.initial_abb_count = 0
            self.after_linear_merge = 0
            self.after_branch_merge = 0
            self.after_loop_merge  = 0
            self.after_dominance_merge = 0

        def __str__(self):
            s = "Linear merge: %d / %d" % (self.initial_abb_count - self.after_linear_merge, self.initial_abb_count)
            s += " | Branch merge: %d / %d " % (self.after_linear_merge - self.after_branch_merge, self.after_linear_merge)
            s += " | Loop merge: %d / %d " % (self.after_branch_merge - self.after_loop_merge, self.after_branch_merge)

            return s

    def __init__(self):
        Analysis.__init__(self)
        self.merge_stats = self.MergeStatistics()

    MergeCandidates = namedtuple('MergeCandidates', 'entry_abb exit_abb inner_abbs')


    def requires(self):
        return ["EnsureComputationBlocks"]


    class DFSContainer:
        def __init__(self, item, dfsG):
            self.item = item
            self.visit_state = 0
            self.dfsG = dfsG

        def was_visited(self):
            return self.visit_state != 0

        def get_successors(self):
            return [ self.dfsG[x] for x in self.item.called_functions ]

        def __str__(self):
            return str("Item: %s | visit: %d" % (self.item, self.visit_state))

    def __dfs_visit(self, dc):
        if dc.was_visited():
            return dc.item.has_syscall


        dc.visit_state += 1 # Visited

        if dc.item.has_syscall:
            return True
        # Go further, for each call in the function
        for succ in dc.get_successors():
            # Recursively check is any successor makes a syscall
            if self.__dfs_visit(succ):
                # Someone made a syscall:
                dc.item.has_syscall = True # mark current function,
                return True                # and propagate to callers

        return False

    def __dfs(self, functions):
        '''Prepare and run DFS to mark all syscall calling functions'''
        self.dfsG = dict()
        for f in functions:
            self.dfsG[f] = self.DFSContainer(f, self.dfsG)
            #print("Before: %s has_syscall: %d" % (f.name, f.has_syscall))


        for dc in self.dfsG.values():
            if self.__dfs_visit(dc):
                dc.item.has_syscall = True


    def __mark_relevant_functions(self, functions):
        '''A DFS to mark all function that do syscalls,
           or call other functions that doing syscall'''
        StartOS = self.system_graph.get(Function, "StartOS")
        StartOS.has_syscall = False
        self.__dfs(list(functions))
        StartOS.has_syscall = True

    def __do_merge(self, entry_abb, exit_abb, inner_abbs = set()):
        #print('Trying to merge:', inner_abbs, exit_abb, 'into', entry_abb)
        #assert not entry_abb == exit_abb, 'Entry ABB cannot merge itself into itself'
        assert not entry_abb in inner_abbs
        assert exit_abb.function and entry_abb.function, 'ABBs must reside in any function'
        assert not entry_abb.relevant_callees and not exit_abb.relevant_callees, 'Mergeable ABBs may not call relevant functions'

        parent_function = entry_abb.function

        # adopt basic blocks
        for abb in (inner_abbs | {exit_abb}) - {entry_abb}:
            for bb in abb.basic_blocks:
                entry_abb.basic_blocks.append(bb) # adopt llvm basic blocks

        # adopt outgoing edges
        for target in exit_abb.get_outgoing_nodes(E.function_level):
            exit_abb.remove_cfg_edge(target, E.function_level)
            if not target == entry_abb: # omit self loop
                entry_abb.add_cfg_edge(target, E.function_level)

        # Remove edges between entry and inner_abbs/exit
        for abb in inner_abbs | {entry_abb}:
            for target in abb.get_outgoing_nodes(E.function_level):
                if target in inner_abbs | {exit_abb}:
                    abb.remove_cfg_edge(target, E.function_level)

        for abb in (inner_abbs | {exit_abb}):
            # Adapt exit ABB in corresponding function
            if parent_function.exit_abb == abb:
                parent_function.set_exit_abb(entry_abb)


        # Remove merged successors from any existing list
        for abb in (inner_abbs | {exit_abb}) - {entry_abb}:
            self.system_graph.remove_abb(abb.get_id())
            parent_function.remove_abb(abb)

        #print("Merged: ", successor, "into:", abb)
        #print(abb.outgoing_edges)

    def __can_be_merged(self, entry_abb, exit_abb, inner_abbs = set()):
        """ Checks if a set of ABBs can be merged """
        for abb in inner_abbs | {entry_abb, exit_abb}:
            # Check if any ABB can actually be merged, that is not invoking any system call
            if not abb.is_mergeable():
                return False

        if entry_abb != exit_abb:
            for exit_successor in exit_abb.get_outgoing_nodes(E.function_level):
                # The exit node may not have any edge to an inner ABB
                if exit_successor in inner_abbs:
                    return False

            for exit_predecessor in exit_abb.get_incoming_nodes(E.function_level):
                # The exit node may not be reachable from the outside
                if exit_predecessor not in inner_abbs | {entry_abb}:
                    return False

            for entry_successor in entry_abb.get_outgoing_nodes(E.function_level):
                # The entry node may only be followed by any inner ABB or the exit ABB
                if not (entry_successor in inner_abbs | {exit_abb}):
                    return False
        else: # entry_abb == exit_abb
            pass
            # Intentionally left blank:
            # We can only check if "some" predecessors are within the inner_abb region

        for inner_abb in inner_abbs:
            # Any inner ABB may only succeed any other inner ABB or the entry ABB
            for inner_predecessor in inner_abb.get_incoming_nodes(E.function_level):
                if not (inner_predecessor in inner_abbs | {entry_abb}):
                    return False

        return True

    def __merge_linear_abbs(self):
        anyChanges = True
        while anyChanges:
            anyChanges = False
            # copy original dict
            for abb in list(self.system_graph.abbs): # Iterate over list of abbs dict KeysView
                #if abb.has_single_successor(E.function_level):
                #    successor = abb.definite_after(E.function_level)
                for successor in abb.get_outgoing_nodes(E.function_level):
                    if successor and self.__can_be_merged(abb, successor):
                        assert successor in self.system_graph.abbs
                        self.__do_merge(abb, successor)
                        anyChanges = True

        # done. do some statistics
        self.merge_stats.after_linear_merge = len(self.system_graph.abbs)

    def __find_branches_to_merge(self, abb):
        successors = abb.get_outgoing_nodes(E.function_level)
        if not len(successors) == 2:
           return None

        left_succ = successors[0]
        right_succ = successors[1]

        #   O abb
        #  | \
        #  | O right_succ
        #  | /
        #   O left_succ
        #
        if right_succ.has_single_successor(E.function_level):
            rss = right_succ.definite_after(E.function_level)
            if rss == left_succ:
                return self.MergeCandidates(entry_abb = abb, exit_abb = left_succ, inner_abbs = set([right_succ]))

        #   O abb
        #  /|
        # O | left_succ
        # \ |
        #  O  right_succ
        #
        if left_succ.has_single_successor(E.function_level):
            lss = left_succ.definite_after(E.function_level)
            if lss == right_succ:
                return self.MergeCandidates(entry_abb = abb, exit_abb = right_succ, inner_abbs = set([left_succ]))

        #
        #   O abb
        #  / \
        # O   O right_succ
        #  \ /
        #   O rss/lss
        if left_succ.has_single_successor(E.function_level) and right_succ.has_single_successor(E.function_level):
            lss = left_succ.definite_after(E.function_level)
            rss = right_succ.definite_after(E.function_level)
            if lss == rss:
                return self.MergeCandidates(entry_abb = abb, exit_abb = lss, inner_abbs = set([right_succ, left_succ]))

        return None

    def __merge_branches(self):
        """
        Try to merge if - else branches with the following pattern:
                O      O
               / \     |\
              O  O     |O
               \/      |/
               O       O
        """
        anyChanges = True
        while anyChanges:
            anyChanges = False
            for abb in list(self.system_graph.abbs):
                mc = self.__find_branches_to_merge(abb)
                if mc and self.__can_be_merged(mc.entry_abb, mc.exit_abb, mc.inner_abbs):
                    self.__do_merge(mc.entry_abb, mc.exit_abb, mc.inner_abbs)
                    anyChanges = True


        self.merge_stats.after_branch_merge = len(self.system_graph.abbs)

    def __find_loops_to_merge(self, abb):
        # |
        # o<--->o
        # |
        successors = abb.get_outgoing_nodes(E.function_level)
        if not len(successors) == 2:
           return None

        left_succ = successors[0]
        right_succ = successors[1]

        if left_succ.has_single_successor(E.function_level):
            succ = left_succ.definite_after(E.function_level)
            if succ == abb:
                return self.MergeCandidates(entry_abb = abb, exit_abb = abb,
                                            inner_abbs = {left_succ})
        if right_succ.has_single_successor(E.function_level):
            succ = right_succ.definite_after(E.function_level)
            if succ == abb:
                return self.MergeCandidates(entry_abb = abb, exit_abb = abb,
                                            inner_abbs = {right_succ})

        return None

    def __merge_loops(self):
        anyChanges = True
        while anyChanges:
            anyChanges = False
            for abb in list(self.system_graph.abbs):
                mc = self.__find_loops_to_merge(abb)
                if mc and self.__can_be_merged(mc.entry_abb, mc.exit_abb, mc.inner_abbs):
                    self.__do_merge(mc.entry_abb, mc.exit_abb, mc.inner_abbs)
                    anyChanges = True

        self.merge_stats.after_loop_merge = len(self.system_graph.abbs)

    def find_region(self, start, end):
        region = set([start, end])
        ws = stack([start])
        while ws:
            cur = ws.pop()
            region.add(cur)
            for node in cur.get_outgoing_nodes(E.function_level):
                if not node in region:
                    ws.push(node)
        return region

    def __merge_dominance(self):
        for func in self.system_graph.functions:
            # Filter some functions
            if not func.is_system_relevant:
                continue
            if len(func.abbs) <= 3 or func.exit_abb == None:
                continue

            # Forward analysis
            dom = DominanceAnalysis(forward = True, edge_levels = E.function_level)
            dom.do(nodes=func.abbs,
                   is_entry=lambda x: x == func.entry_abb)

            # Backward analysis
            post_dom = DominanceAnalysis(forward = False,
                                         edge_levels = E.function_level)
            post_dom.do(nodes=func.abbs,
                   is_entry=lambda x: x == func.exit_abb)

            removed = set()

            for abb in func.abbs:
                if abb in removed:
                    continue
                start = dom.immdom_tree[abb]
                end   = post_dom.immdom_tree[abb]
                if start and end and start != end:
                    region = self.find_region(start, end)
                    inner = region - set([start, end])
                    # Was there already some subset removed?
                    if start in removed or end in removed:
                        continue
                    inner = inner - removed
                    if self.__can_be_merged(start, end, inner):
                        self.__do_merge(start, end, inner)
                        # Mark as removed
                        removed.add(end)
                        removed.update(inner)

        self.merge_stats.after_dominance_merge = len(self.system_graph.abbs)

    def do(self):
        self.merge_stats.initial_abb_count = len(self.system_graph.abbs)

        # First mark all Functions that do a syscall or invoke any sub function that does so
        self.__mark_relevant_functions(self.system_graph.functions)

        # Merge with dominance information.
        self.__merge_dominance()
        logging.info("Dominance Merge: %d/%d" %(self.merge_stats.initial_abb_count - self.merge_stats.after_dominance_merge,
                                                self.merge_stats.after_dominance_merge))

        self.merge_stats.initial_abb_count = len(self.system_graph.abbs)
        current_size = None
        while current_size != self.merge_stats.initial_abb_count:
            current_size = len(self.system_graph.abbs)

            # linear merging:
            self.__merge_linear_abbs()

            # try to merge if-else branches
            self.__merge_branches()

            # merge loop regions
            self.__merge_loops()

            logging.info(self.merge_stats)

            self.merge_stats.initial_abb_count = len(self.system_graph.abbs)
            first = False
