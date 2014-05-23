from generator.graph.Analysis import Analysis
from generator.graph.AtomicBasicBlock import E, S
import logging

class AddFunctionCalls(Analysis):
    """This task contructs the task_level control flow graph from the
    function_level control graph"""
    def __init__(self):
        Analysis.__init__(self)
        self.relevant_functions = None

    def requires(self):
        ret = ["EnsureComputationBlocks"]
        merge = self.system_graph.get_pass("ABBMergePass",
                                           only_enqueued = True)
        if merge:
            ret.append("ABBMergePass")
        return ret

    def get_edge_filter(self):
        return set([E.function_level, E.task_level])

    def do(self):
        ## Mark all relevant functions

        # All subtasks are relevant
        self.relevant_functions = set(self.system_graph.get_subtasks())

        # All functions that belong to tasks are relevant:
        for task in self.system_graph.tasks:
            self.relevant_functions.update(task.functions)

        for name in ("os_main", "StartOS"):
            if name in self.system_graph.functions:
                self.relevant_functions.add(self.system_graph.find_function(name))

        for abb in self.system_graph.get_abbs():
            if not abb.function.has_syscall:
                continue

            # Add all 'normal' function call edges
            handled = False
            if len(abb.relevant_callees) == 1:
                calling_block = abb
                function = list(abb.relevant_callees)[0]
                assert function.has_syscall, str(function)

                called_block  = function.entry_abb
                returned_block = calling_block.definite_after(E.function_level)
                return_block = function.exit_abb
                assert calling_block.isA(S.computation)
                assert calling_block != None, "Could not find CallingBlock ABB%d" % call.abb
                assert return_block != None, "Could not find FunctionCall return block"

                # Mark as a relevant function
                self.relevant_functions.add(function)

                # Transform the local edge to a virtual local edge, to
                # preserve the return information
                calling_block.add_cfg_edge(called_block, E.task_level)
                return_block.add_cfg_edge(returned_block, E.task_level)
                handled = True

            else:
                assert len(abb.relevant_callees) == 0
                for target in abb.get_outgoing_nodes(E.function_level):
                    abb.add_cfg_edge(target, E.task_level)


    def is_relevant_function(self, function):
        if not self.valid:
            return True
        return function in self.relevant_functions
