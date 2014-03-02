from generator.graph.Analysis import Analysis
from generator.graph.AtomicBasicBlock import E
from generator.tools import Enum
import logging

class AssertionType(Enum):
    TaskIsReady = 0
    TaskIsSuspended = 1
    TaskWasKickoffed = 2
    TaskWasNotKickoffed = 3


class Assertion:
    def __init__(self, _type, _arguments):
        self.Type = _type
        self.arguments = _arguments

    def __repr__(self):
        return "<assert.%s%s>" %(self.Type.name, self.arguments)

    def __hash__(self):
        return hash(self.Type)

    def __eq__(self, other):
        if not isinstance(other, Assertion):
            return False
        if self.Type != other.Type:
            return False
        if self.arguments != other.arguments:
            return False
        return True

    def isA(self, _type):
        return _type == self.Type

    def get_arguments(self):
        return self.arguments



class GenerateAssertionsPass(Analysis):
    """This pass generates assertions that must hold before a system call
       and after a systemcall."""

    pass_alias = "gen-asserts"

    def __init__(self):
        Analysis.__init__(self)
        self.abb_info          = None
        self.assertions_before = None
        self.assertions_after  = None

    def requires(self):
        return ["ConstructGlobalCFG"]

    def get_edge_filter(self):
        return [E.function_level, E.system_level]

    def state_asserts(self, abb, state):
        ret = []
        for subtask in self.system_graph.get_subtasks():
            # Only for real tasks
            if not subtask.is_real_thread():
                continue
            if state.is_surely_ready(subtask):
                ret.append(Assertion(AssertionType.TaskIsReady, [subtask]))
            if state.is_surely_suspended(subtask):
                ret.append(Assertion(AssertionType.TaskIsSuspended, [subtask]))

            # Since we come from the current stack, it is quite sure,
            # were we came from
            if state.current_subtask != subtask:
                if state.was_surely_not_kickoffed(subtask):
                    ret.append(Assertion(AssertionType.TaskWasNotKickoffed, [subtask]))
                if state.was_surely_kickoffed(subtask):
                    ret.append(Assertion(AssertionType.TaskWasKickoffed, [subtask]))
        return ret

    def state_assertions_before(self, abb):
        """Generate assertions for the system state before the syscall"""
        abb_info = self.abb_info.for_abb(abb)
        if not abb_info:
            # We have no information about this abb
            return

        asserts = self.state_asserts(abb, abb_info.state_before)
        self.assertions_before[abb] += asserts

    def state_assertions_after(self, abb):
        """Generate assertions for the system state after the syscall"""
        # Get the information for the computation block following the syscall
        computation_block = abb.definite_after(E.function_level)
        abb_info = self.abb_info.for_abb(computation_block)
        if not abb_info:
            # We have no information about this abb
            return

        asserts = self.state_asserts(abb, abb_info.state_before)
        self.assertions_after[abb] += asserts


    def do(self):
        # Get abb_info provider
        construct_cfg = self.system_graph.get_pass("ConstructGlobalCFG")
        self.abb_info = construct_cfg.global_abb_information_provider()

        # before-assertions must hold in the EnterSystemHook
        self.assertions_before = {}
        # after-assertions must hold in the LeaveSystemHook
        self.assertions_after  = {}

        # Empty lists to hold the assertions
        working_abbs = []
        for abb in self.system_graph.get_syscalls():
            self.assertions_before[abb] = []
            self.assertions_after[abb]  = []

            if abb.syscall_type.isRealSyscall() and \
               not abb.function.is_system_function:
                working_abbs.append(abb)

        # Generate Assertions from inferred system_state
        for abb in working_abbs:
            self.state_assertions_before(abb)
            if not abb.syscall_type.doesTerminateTask():
                self.state_assertions_after(abb)

        # The assertions after the syscall may be redundant. When a
        # systemcall returns, this might be caused by the syscall at
        # this point or when another syscall dispatches to that
        # place. So we remove all checks that are common to all
        # syscalls that return to the computation block following the
        # current syscall
        count_before, count_after = 0, 0
        for abb in working_abbs:
            if abb.syscall_type.doesTerminateTask():
                continue
            # The compuation block after the syscall. AKA the
            # continuation point
            computation_block = abb.definite_after(E.function_level)
            # All ABBs that continue to that point
            incoming_abbs = computation_block.get_incoming_nodes(E.system_level)
            # We may also be entered by interrupts, ignore them
            incoming_abbs = filter(lambda x: x in self.assertions_before,
                                   incoming_abbs)
            assert len(incoming_abbs) > 0, "Weird ABB: %s" % abb
            checked_assertions = set(self.assertions_before[incoming_abbs[0]])
            for incoming_abb in incoming_abbs[1:]:
                checked_before = set(self.assertions_before[incoming_abb])
                checked_assertions = checked_assertions & checked_before

            # Remove them from the after asserts
            should_be_checked = set(self.assertions_after[abb])
            self.assertions_after[abb] = (should_be_checked - checked_assertions)

        for abb in working_abbs:
            count_before += len(self.assertions_before[abb])
            count_after  += len(self.assertions_after[abb])

        logging.info("  + %d/%d assertions generated", count_before, count_after)


    def system_enter_hook(self, generator, abb, hook):
        """This function is called by the code generation, when the system
           enter hook should be filled"""
        for each in self.assertions_before[abb]:
            generator.syscall_rules.do_assertion(hook, each)

    def system_leave_hook(self, generator, abb, hook):
        """This function is called by the code generation, when the system
           leave hook should be filled"""
        for each in self.assertions_after[abb]:
            generator.syscall_rules.do_assertion(hook, each)


