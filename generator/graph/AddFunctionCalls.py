from generator.graph.Analysis import Analysis
from generator.graph.AtomicBasicBlock import E


class AddFunctionCalls(Analysis):
    """This task contructs the task_level contronl flor graph from the
    function_level control graph"""
    def __init__(self, calls):
        Analysis.__init__(self)
        self.function_calls = calls
        self.relevant_functions = None

    def requires(self):
        return ["EnsureComputationBlocks"]

    def get_edge_filter(self):
        return set([E.function_level, E.task_level])

    def do(self):
        ## Mark all relevant functions

        # All subtasks are relevant
        relevant_functions = set(self.system.get_subtasks())

        # All functions that belong to tasks are relevant:
        for task in self.system.tasks:
            relevant_functions.update(task.functions)

        # All functions that contain at least one systemcall are relevant
        for function in self.system.functions.values():
            if len(function.get_syscalls()) > 0:
                relevant_functions.add(function)

        for name in ("os_main", "StartOS"):
            if name in self.system.functions:
                relevant_functions.add(self.system.find_function(name))


        changed = True
        while changed:
            changed = False
            for call in self.function_calls:
                calling_block = self.system.find_abb(call.abb)
                calling_function = calling_block.function
                called_function = self.system.find_function(call.function)

                assert called_function, "All called functions have to exist"
                assert calling_function, "All calling functions have to exist"

                if called_function in relevant_functions \
                   and not calling_function in relevant_functions:
                    relevant_functions.add(called_function)
                    print calling_function, "->", called_function
                    changed = True

        self.relevant_functions = relevant_functions
        for abb in self.system.get_abbs():
            # Add all 'normal' function call edges
            handled = False
            for call in self.function_calls:
                calling_block = self.system.find_abb(call.abb)
                # Not the current function ABB
                if calling_block != abb:
                    continue
                function = self.system.find_function(call.function)
                if not function in relevant_functions:
                    continue
                called_block  = function.entry_abb
                returned_block = calling_block.definite_after(E.function_level)
                return_block = function.exit_abb
                assert calling_block.type == "computation"
                assert calling_block != None, "Could not find CallingBlock ABB%d" % call.abb
                assert return_block != None, "Could not find FunctionCall return block"

                # Transform the local edge to a virtal local edge, to
                # preserve the return information
                calling_block.add_cfg_edge(called_block, E.task_level)
                return_block.add_cfg_edge(returned_block, E.task_level)
                handled = True
                break
            if not handled:
                for target in abb.get_outgoing_nodes(E.function_level):
                    abb.add_cfg_edge(target, E.task_level)

    def is_relevant_function(self, function):
        if not self.valid:
            return True
        return function in self.relevant_functions
