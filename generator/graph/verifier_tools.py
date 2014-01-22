def get_functions(system, names):
    """A helper for verify scripts to find quickly a set of subtask handlers"""
    ret = []
    for x in names:
        for name, func in system.functions.items():
            if x == name or \
               "OSEKOS_TASK_" + x == name or \
               "OSEKOS_ISR_" + x == name:
                ret.append(func)
    return tuple(ret)

class RunningTaskToolbox:
    def __init__(self, analysis):
        self.analysis = analysis
        self.checked_syscalls = set()

    def mark_syscall(self, syscall):
        """Mark syscall as checked"""
        self.checked_syscalls.add(syscall)

    def mark_syscalls_in_function(self, function):
        """Mark all syscalls in functions as checked"""
        for syscall in function.get_syscalls():
            self.mark_syscall(syscall)

    def promise_all_syscalls_checked(self):
        assert set(self.analysis.system.get_syscalls()) == self.checked_syscalls, "missing %s" \
            %(set(self.analysis.system.get_syscalls()) - self.checked_syscalls)

    def syscall(self, function, syscall_name, arguments):
        """Tests wheter a syscall exists and returns it"""
        syscall = self.analysis.system.find_syscall(function, syscall_name, arguments)
        assert syscall, "%s:%s(%s) not found" %(function.function_name, syscall_name, arguments)
        return syscall

    def reachability(self, function, syscall_name, arguments, possible_subtasks):
        """Check to which subtasks a certain syscall can dispatch. Syscall is
        marked as visited"""

        syscall = self.syscall(function, syscall_name, arguments)
        reachable_subtasks = self.analysis.reachable_subtasks_from_abb(syscall)
        assert(set(reachable_subtasks) == set(possible_subtasks)), "%s:%s(%s)::: %s != %s" %(
            function.function_name, syscall_name, arguments, list(possible_subtasks), list(reachable_subtasks))
        self.checked_syscalls.add(syscall)

        return syscall

    def activate(self, possible_subtasks, function):
        """Check which subtasks can activate a given function. The activating
        ABBs are returned"""
        activating_subtasks, activating_abbs = self.analysis.activating_subtasks(function)
        assert(set(activating_subtasks) == set(possible_subtasks)), "SetReady(%s):: %s != %s" %(
            function.function_name, list(activating_subtasks), list(possible_subtasks))

        return activating_abbs
