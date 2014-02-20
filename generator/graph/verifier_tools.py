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

def get_objects(system, names):
    ret = []
    for x in names:
        if x in system.resources:
            ret.append(system.resources[x])
    return ret

class RunningTaskToolbox:
    def __init__(self, analysis):
        self.analysis = analysis
        self.checked_syscalls = set()
        for syscall in self.analysis.system.get_syscalls():
            if syscall.type == "ShutdownOS":
                self.checked_syscalls.add(syscall)

        # All Systemcalls in alarms are automatically checked
        for alarm in analysis.system.alarms:
            self.checked_syscalls.add(alarm.handler.entry_abb)

        self.check_base_constraints()

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
        return self.reachability_bare(syscall, possible_subtasks)

    def reachability_bare(self, syscall, possible_subtasks):
        reachable_subtasks = self.analysis.reachable_subtasks_from_abb(syscall)
        assert(set(reachable_subtasks) == set(possible_subtasks)), "%s:%s(%s)::: %s != %s" %(
            syscall.function.function_name, syscall.type,
            syscall.arguments, list(possible_subtasks), list(reachable_subtasks))
        self.checked_syscalls.add(syscall)

        return syscall

    def reachability_abbs(self, syscall, targets):
        reachable_abbs = syscall.get_outgoing_nodes('global')
        assert(set(targets) == set(reachable_abbs)), "%s:%s(%s)::: %s != %s" %(
            syscall.function.function_name, syscall.type,
            syscall.arguments, list(targets), list(reachable_abbs))


    def activate(self, possible_subtasks, function):
        """Check which subtasks can activate a given function. The activating
        ABBs are returned"""
        activating_subtasks, activating_abbs = self.analysis.activating_subtasks(function)
        assert(set(activating_subtasks) == set(possible_subtasks)), "SetReady(%s):: %s != %s" %(
            function.function_name, list(activating_subtasks), list(possible_subtasks))

        return activating_abbs

    def check_base_constraints(self):
        for syscall in self.analysis.system.get_syscalls():
            # Some syscalls cannot reschedule
            if syscall.type in ("GetResource", "CancelAlarm", "SetRelAlarm"):
                self.reachability_bare(syscall, [syscall.function.subtask])
        for abb in self.analysis.system.get_abbs():
            abb_info = self.analysis.for_abb(abb)
            if not abb_info:
                continue
            assert abb_info.state_before.current_abb == abb, "%s is weird"
            for state in abb_info.states_after:
                assert state.current_abb != None
                assert state.current_abb in abb.get_outgoing_nodes('global')

            # When we have a subtask->subtask transition, the target
            # must always be an computation block
            for next_abb in abb.get_outgoing_nodes('global'):
                if abb.function.subtask != next_abb.function.subtask:
                    assert next_abb.type == "computation", \
                        "Target of an subtask subtask Transition must always be " \
                        + " an computation block (%s -> %s)" %(abb.path(), next_abb.path())

