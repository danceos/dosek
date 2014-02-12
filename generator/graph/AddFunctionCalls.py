from generator.graph.Analysis import Analysis


class AddFunctionCalls(Analysis):
    def __init__(self, calls):
        Analysis.__init__(self)
        self.function_calls = calls
        self.relevant_functions = None

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
        # Add all 'normal' function call edges
        for call in self.function_calls:
            calling_block = self.system.find_abb(call.abb)
            function = self.system.find_function(call.function)
            if not function in relevant_functions:
                continue
            called_block  = function.entry_abb
            returned_block = calling_block.definite_after('local')
            return_block = function.exit_abb
            assert calling_block.type == "computation"
            assert calling_block != None, "Could not find CallingBlock ABB%d" % call.abb
            assert return_block != None, "Could not find FunctionCall return block"

            calling_block.remove_cfg_edge(returned_block, 'local')
            calling_block.add_cfg_edge(called_block, 'local')
            return_block.add_cfg_edge(returned_block, 'local')

    def is_relevant_function(self, function):
        if not self.valid:
            return True
        return function in self.relevant_functions
