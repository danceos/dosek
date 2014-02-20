from generator.graph.Analysis import Analysis, EnsureComputationBlocks,\
                                     FixpointIteraton, MoveFunctionsToTask

from generator.graph.PrioritySpreadingPass import PrioritySpreadingPass
from generator.graph.AtomicBasicBlock import E
from collections import namedtuple
from copy import copy

class DynamicPriorityAnalysis(Analysis):
    """This pass does a local control flow propagation of the dynamic
    priority. The dynamic priority can be changed by the aquisition of
    resources. So for each ABB we compute a set of possible taken
    resources by the task.
    """
    def __init__(self):
        Analysis.__init__(self)
        self.values = None
        self.__res = None

    def requires(self):
        return [EnsureComputationBlocks.name(), MoveFunctionsToTask.name(),
                PrioritySpreadingPass.name()]

    StateVector = namedtuple("StateVector", ["free", "taken"])

    def block_functor(self, fixpoint, abb):
        res = self.__res

        # We do an forward analysis, so we start with the "I DON'T
        # KNOW ANYTHING" state
        taken, free = False, False
        # Merge Incoming
        for incoming in abb.get_incoming_nodes(E.task_level):
            # Possible taken resources from incoming edges
            in_state = self.values[res][incoming]
            taken = taken or in_state.taken
            free  = free  or in_state.free

        if abb.type == "GetResource" and abb.arguments[0] == res:
            # Has an influence on the current resource
            state = self.StateVector(free = False, taken = True)
        elif abb.type == "ReleaseResource" and abb.arguments[0] == res:
            # Has an influence on the current resource
            state = self.StateVector(free = True, taken = False)
        else:
            state = self.StateVector(free = free, taken = taken)

        if state != self.values[res][abb]:
            self.values[res][abb] = state
            fixpoint.enqueue_soon(items = abb.get_outgoing_nodes(E.task_level))
        

    def do(self):
        start_basic_blocks = []
        # AtomicBasicBlock -> set([Resource])
        self.values = {}
        # All Atomic basic blocks have a start value
        for resource in self.system.resources.values():
            self.values[resource] = {}
            for abb in self.system.get_abbs():
                # The default is that we do not know anything
                self.values[resource][abb] \
                    = self.StateVector(free = False, taken = False)
            for subtask in self.system.get_subtasks():
                # At the entry point of a subtask every resource is free
                self.values[resource][subtask.entry_abb] \
                    = self.StateVector(free = True, taken = False)

                # The children of the entry abb are our starting point.
                successors = subtask.entry_abb.get_outgoing_nodes(E.task_level)
                start_basic_blocks.extend(successors)

            # After the System boots we also know that everything is fine
            self.values[resource][self.system.functions["StartOS"].entry_abb] \
                = self.StateVector(free = True, taken = False)

        for resource in self.system.resources.values():
            self.__res = resource
            fixpoint = FixpointIteraton(start_basic_blocks)
            fixpoint.do(self.block_functor)

        # Here we assert that for every resource we know exactly
        # wheter it is taken, or not. This prohibits situations like:
        # if (X)
        #    GetResource(A)
        # ...
        # if (X)
        #    ReleaseResource(A)
        for abb in self.system.get_abbs():
            if abb.function.subtask == None:
                # Not reachable from a subtask
                continue
            dynamic_priority = abb.function.subtask.static_priority
            for resource in self.system.resources.values():
                state = self.values[resource][abb]
                assert not(state.free and state.taken), \
                    """The allocation state of resource have to be unambigious at every
                    point. Do not make GetResource conditional (Resource %s in function %s)""" %\
                        (resource, abb.function)
                if state.taken:
                    dynamic_priority = max(dynamic_priority, resource.static_priority)

            # Each abb has a dynamic priority
            abb.dynamic_priority = dynamic_priority

        # Each systemcall has the priority of the preceeding block, if
        # there is no preceeding block (which is only true for
        # StartOS), the priority is the idle priority.
        for syscall in self.system.get_syscalls():
            precessors = syscall.get_incoming_nodes(E.task_level)
            if len(precessors) == 0:
                assert syscall.function.is_system_function
                syscall.dynamic_priority = self.system.get_subtask("Idle").static_priority
            elif len(precessors) == 1:
                syscall.dynamic_priority = precessors[0].dynamic_priority
            else:
                assert False, "Weird Systemcall %s %s, Check EnsureComputationBlocks for bugs!" %(syscall, syscall.type)
