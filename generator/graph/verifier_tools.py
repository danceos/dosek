from generator.graph.AtomicBasicBlock import E,S
from generator.graph.SystemStateFlow import SystemStateFlow
from generator.graph.SymbolicSystemExecution import SymbolicSystemExecution
from generator.graph.Resource import Resource


global E

def get_functions(system, names):
    """A helper for verify scripts to find quickly a set of subtask handlers"""
    ret = []
    for x in names:
        for func in system.functions:
            if x == func.function_name or \
               "OSEKOS_TASK_" + x == func.function_name or \
               "OSEKOS_ISR_" + x == func.function_name:
                ret.append(func)
    return tuple(ret)

def get_objects(system, names):
    ret = []
    for x in names:
        ret.append(system.get(Resource, x))
    return ret

class GlobalABBInfoToolbox:
    def __init__(self, system_graph, abb_info_provider):
        self.system_graph = system_graph
        self.abb_info_provider = abb_info_provider

        self.checked_syscalls = set()
        for syscall in self.system_graph.syscalls:
            if syscall.syscall_type.isRealSyscall() \
               and not syscall.isA(S.kickoff):
                continue
            if syscall.isA(S.computation):
                continue
            self.checked_syscalls.add(syscall)
        for alarm in self.system_graph.alarms:
            self.checked_syscalls.add(alarm.carried_syscall)

    def mark_syscall(self, syscall):
        """Mark syscall as checked"""
        self.checked_syscalls.add(syscall)

    def mark_syscalls_in_function(self, function):
        """Mark all syscalls in functions as checked"""
        for syscall in function.syscalls:
            self.mark_syscall(syscall)

    def promise_all_syscalls_checked(self):
        assert set(self.system_graph.syscalls) == self.checked_syscalls,\
            "missing %s"%(set(self.system_graph.syscalls) ^ self.checked_syscalls)

    def syscall(self, function, syscall_name, arguments):
        """Tests wheter a syscall exists and returns it"""
        syscall = self.system_graph.find_syscall(function, syscall_name, arguments)
        assert syscall, "%s:%s(%s) not found" %(function.function_name, syscall_name, arguments)
        return syscall

    def reachability(self, function, syscall_name, arguments, possible_subtasks):
        """Check to which subtasks a certain syscall can dispatch. Syscall is
        marked as visited"""

        syscall = self.syscall(function, syscall_name, arguments)
        return self.reachability_bare(syscall, possible_subtasks)

    def reachability_bare(self, syscall, possible_subtasks):
        reachable_subtasks = list(self.abb_info_provider.for_abb(syscall).tasks_after.keys())
        assert(set(reachable_subtasks) == set(possible_subtasks)), "%s:%s(%s)::: %s != %s" %(
            syscall.function.function_name, syscall.syscall_type.name,
            syscall.arguments, list(possible_subtasks), list(reachable_subtasks))
        self.checked_syscalls.add(syscall)

        return syscall

    def reachability_abbs(self, syscall, targets):
        reachable_abbs = self.abb_info_provider.for_abb(syscall).abbs_after
        assert(set(targets) == set(reachable_abbs)), "%s:%s(%s)::: %s != %s" %(
            syscall.function.function_name, syscall.syscall_type.name,
            syscall.arguments, list(targets), list(reachable_abbs))


    def activate(self, possible_subtasks, function):
        """Check which subtasks can activate a given function. The activating
        ABBs are returned"""
        activating_subtasks = set()
        activating_abbs = self.abb_info_provider.for_abb(function.entry_abb).abbs_before
        for abb in activating_abbs:
            activating_subtasks.add(abb.function.subtask)

        assert(set(activating_subtasks) == set(possible_subtasks)), "SetReady(%s):: %s != %s" %(
            function.function_name, list(activating_subtasks), list(possible_subtasks))

        return activating_abbs

    def self_loop_abbs(self, function, level):
        """Returns all ABBs with a self loop in the function on the edge level"""
        ret = []
        for abb in function.abbs:
            if abb in abb.get_outgoing_nodes(level):
                ret.append(abb)
        return ret

class ConstructGlobalCFGToolbox(GlobalABBInfoToolbox):
    def __init__(self, analysis):
        GlobalABBInfoToolbox.__init__(self, analysis.system_graph,
                                      analysis.global_abb_information_provider())


class RunningTaskToolbox(GlobalABBInfoToolbox):
    def __init__(self, analysis):
        GlobalABBInfoToolbox.__init__(self, analysis.system_graph, analysis)
        assert isinstance(analysis, SystemStateFlow)
        self.analysis = analysis
        self.system_graph = analysis.system_graph
        self.check_base_constraints()

    def check_base_constraints(self):
        for syscall in self.system_graph.syscalls:
            # Some syscalls cannot reschedule
            if syscall.isA([S.GetResource, S.CancelAlarm, S.SetRelAlarm]):
                self.reachability_bare(syscall, [syscall.function.subtask])
        for abb in self.system_graph.abbs:
            abb_info = self.analysis.for_abb(abb)
            if not abb_info:
                continue
            assert abb_info.state_before.current_abb == abb, "[%s]=%s is weird" % \
                (abb, abb_info.state_before)
            for state in abb_info.states_after:
                assert state.current_abb != None
                assert state.current_abb in abb.get_outgoing_nodes(E.state_flow)

            # When we have a subtask->subtask transition, the target
            # must always be an computation block
            for next_abb in abb.get_outgoing_nodes(E.state_flow):
                if abb.function.subtask != next_abb.function.subtask:
                    assert next_abb.isA([S.kickoff, S.computation]), \
                        "Target of an subtask subtask Transition must always be " \
                        + " an computation block (%s -> %s)" %(abb.path(), next_abb.path())



