from generator.analysis import Analysis, E
from generator.tools import Enum
import logging

# config-constraint-: dependability.state-asserts -> (os.systemcalls == normal)

class AssertionType(Enum):
    TaskIsReady = 0
    TaskIsSuspended = 1
    TaskWasKickoffed = 2
    TaskWasNotKickoffed = 3

    EventsCheck = 4

class Assertion:
    def __init__(self, _type, _arguments, prio = 0):
        self.Type = _type
        self.arguments = _arguments
        self.prio = prio

    def __repr__(self):
        return "<assert.%s%s prio=%d>" %(self.Type.name, self.arguments, self.prio)

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
        self.max_assertions_per_syscall = 45

    def requires(self):
        return ["ConstructGlobalCFG"]

    def get_edge_filter(self):
        return [E.function_level, E.system_level]

    def state_asserts(self, abb, state):
        ret = []

        for subtask in self.system_graph.subtasks:
            # Only for real tasks
            if not subtask.is_real_thread():
                continue

            # Lower is better
            prio = abs(abb.dynamic_priority - subtask.static_priority)

            if state.is_surely_ready(subtask):
                ret.append(Assertion(AssertionType.TaskIsReady, [subtask],
                                     prio = prio))
            if state.is_surely_suspended(subtask):
                ret.append(Assertion(AssertionType.TaskIsSuspended, [subtask],
                                     prio = prio))

            # Since we come from the current stack, it is quite sure,
            # were we came from
            if state.current_subtask != subtask:
                if state.was_surely_not_kickoffed(subtask):
                    ret.append(Assertion(AssertionType.TaskWasNotKickoffed, [subtask],
                                         prio = prio * 1.5))
                if state.was_surely_kickoffed(subtask):
                    ret.append(Assertion(AssertionType.TaskWasKickoffed, [subtask],
                                         prio = prio * 1.5))
            # For each event this task can receive, we can derive an assertions
            events_set = []
            events_cleared = []
            for event in subtask.events:
                SET = state.is_event_set(subtask, event)
                CLEARED = state.is_event_cleared(subtask, event)
                assert SET or CLEARED

                if SET == 0 and CLEARED == 1:
                    events_cleared.append(event)
                if SET == 1 and CLEARED == 0:
                    events_set.append(event)
            if events_set or events_cleared:
                ret.append(Assertion(AssertionType.EventsCheck, [subtask, events_cleared, events_set]))
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
        for abb in self.system_graph.syscalls:
            self.assertions_before[abb] = []
            self.assertions_after[abb]  = []

            if abb.syscall_type.isRealSyscall():
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
            incoming_abbs = [x for x in incoming_abbs if x in self.assertions_before]

            # We cannot remove asserts from syscalls without incoming abbs
            if len(incoming_abbs) == 0:
                continue
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

        logging.info(" + %d/%d assertions generated for %d syscalls", 
                     count_before, count_after, len(working_abbs))

        # Limit the maximal assertions to
        # max_assertions_per_syscall. After system call asserts are
        # more important, since they capture the influence of a system
        # call to the system state.
        pruned_before = 0
        pruned_after = 0
        for abb in working_abbs:
            asserts_left = self.max_assertions_per_syscall
            x = sorted(self.assertions_after[abb], key = lambda x: x.prio)
            self.assertions_after[abb] = list(x[:asserts_left])
            asserts_left -= len(self.assertions_after[abb])
            if asserts_left < 0:
                asserts_left = 0

            x = sorted(self.assertions_before[abb], key = lambda x: x.prio)
            self.assertions_before[abb] = list(x[:asserts_left])

            pruned_before += len(self.assertions_before[abb])
            pruned_after  += len(self.assertions_after[abb])

        logging.info(" + %d/%d (%d/%d) assertions generated for %d syscalls",
                     pruned_before, pruned_after,
                     (pruned_before - count_before),
                     (pruned_after - count_after),
                     len(working_abbs))


    def system_enter_hook(self, generator, abb, hook):
        """This function is called by the code generation, when the system
           enter hook should be filled"""
        generator.syscall_rules.do_assertions(hook, self.assertions_before[abb])

    def system_leave_hook(self, generator, abb, hook):
        """This function is called by the code generation, when the system
           leave hook should be filled"""
        generator.syscall_rules.do_assertions(hook, self.assertions_after[abb])
