import logging
import sys
from .common import *
from .AtomicBasicBlock import E, S
from collections import defaultdict
from .Event import Event
import copy

class Analysis:
    def __init__(self):
        self.valid = False
        self.debug = self.__log_void
        self.system_graph = None
        self.stats = None

    def __log_void(self, *args, **kwargs):
        pass

    def __log_debug(self, *args, **kwargs):
        logging.debug(*args, **kwargs)

    def set_debug(self, enabled = True):
        if enabled:
            self.debug = self.__log_debug
        else:
            self.debug = self.__log_void

    def set_system(self, system_graph):
        self.system_graph = system_graph
        self.stats = system_graph.stats

    @classmethod
    def name(cls):
        return cls.__name__

    def requires(self):
        """Returns a list of analysis pass names"""
        return []

    def get_analysis(self, name):
        a = self.system_graph.passes[name]
        assert a.valid
        return a

    def analyze(self):
        assert not self.valid
        assert self.system_graph != None
        self.do()
        self.valid = True

    def get_edge_filter(self):
        """Get a filter of edge types"""
        return set([E.function_level])

    def do(self):
        pass

    def panic(self, msg):
        logging.error(msg)
        sys.exit(-1)

    def for_abb(self, abb):
        """Information about a abb that the current analysis provides"""
        return None

class EnsureComputationBlocks(Analysis):
    """This pass ensures that every system call is surrounded by a
    computation block. This is necessary to model alarms/interrupts and
    other sporadic events, since they can only be take place in those blocks"""

    def __init__(self):
        Analysis.__init__(self)

    def get_edge_filter(self):
        return set([E.function_level])

    def requires(self):
        # We need the system to be read in
        return ["llvmpy"]

    def add_before(self, abb):
        necessary = False
        if len (abb.get_incoming_nodes(E.function_level)) > 1:
            necessary = True
        elif len (abb.get_incoming_nodes(E.function_level)) == 1:
            if not abb.definite_before(E.function_level).isA(S.computation):
                necessary = True
        else:
            assert abb.function.entry_abb == abb
            necessary = True

        if not necessary:
            return

        new = self.system_graph.new_abb()
        new.syscall_type = S.computation
        abb.function.add_atomic_basic_block(new)

        for edge in copy.copy(abb.incoming_edges):
            edge.source.remove_cfg_edge(abb, edge.level)
            edge.source.add_cfg_edge(new, edge.level)
        if abb.function.entry_abb == abb:
            abb.function.entry_abb = new
        new.add_cfg_edge(abb, E.function_level)

    def add_after(self, abb):
        necessary = False
        if len (abb.get_outgoing_nodes(E.function_level)) > 1:
            necessary = True
        elif len (abb.get_outgoing_nodes(E.function_level)) == 1 \
             and not abb.definite_after(E.function_level).isA(S.computation):
            necessary = True
        elif len (abb.get_outgoing_nodes(E.function_level)) == 0:
            necessary = True

        if not necessary:
            return
        #print "add_after", abb
        new = self.system_graph.new_abb()
        abb.function.add_atomic_basic_block(new)
        for edge in copy.copy(abb.outgoing_edges):
            abb.remove_cfg_edge(edge.target, E.function_level)
            new.add_cfg_edge(edge.target, E.function_level)

        abb.add_cfg_edge(new, E.function_level)

    def do(self):
        for syscall in self.system_graph.syscalls:
            if syscall.subtask and syscall.subtask.conf.is_isr:
                continue
            if syscall.isA(S.Idle):
                pass
            elif not syscall.syscall_type.isRealSyscall():
                continue
            elif syscall.syscall_type.doesKickoffTask():
                self.add_after(syscall)
            elif syscall.syscall_type.doesTerminateTask():
                self.add_before(syscall)
            else:
                # For all other syscall ABBs add a computation block
                # before and after
                self.add_before(syscall)
                self.add_after(syscall)

        for subtask in self.system_graph.subtasks:
            if subtask.entry_abb.isA(S.kickoff):
                subtask.entry_abb.arguments = [subtask]
                continue

            assert not subtask.is_real_thread(), "Should not happen with new EAG version (InsertKickoffSyscalls)"
            kickoff = self.system_graph.new_abb()
            subtask.add_atomic_basic_block(kickoff)
            kickoff.make_it_a_syscall(S.kickoff, [subtask])
            kickoff.add_cfg_edge(subtask.entry_abb, E.function_level)
            subtask.set_entry_abb(kickoff)



class CurrentRunningSubtask(Analysis):
    """This pass does a local control flow propagation of the currently
    running subtask. When a function is called from two subtasks its
    subtask set contains those two subtasks. This is forbidden by the
    generator.
    """
    def __init__(self):
        Analysis.__init__(self)
        self.values = None

    def requires(self):
        return ["AddFunctionCalls"]

    def get_edge_filter(self):
        return set([E.function_level, E.task_level])

    def for_abb(self, abb):
        x = list(self.values.get(abb, []))
        if len(x) == 0:
            return None
        elif len(x) == 1:
            return x[0]
        else:
            self.panic("For %s (%s) it is not unambiguous, which task " \
                       "is running at that very moment. This is not " \
                       "supported by the system"%(abb, abb.function))

    def block_functor(self, fixpoint, abb):
        # Gather all task objects from incoming edges
        possible_running_tasks = set(self.values[abb])
        for outgoing in abb.get_outgoing_nodes(E.task_level):
            successors =  set(self.values[outgoing])
            if not possible_running_tasks.issubset(successors):
                self.values[outgoing] += possible_running_tasks
                fixpoint.enqueue_soon(outgoing)

    def do(self):
        start_basic_blocks = []
        # AtomicBasicBlock -> set([Subtask])
        self.values = defaultdict(list)
        # All Atomic basic blocks have a start value
        for task in self.system_graph.tasks:
            for subtask in task.subtasks:
                # Start DFS at all entry nodes
                self.values[subtask.entry_abb] = set([subtask])
                #start_basic_blocks.extend(subtask.entry_abb.get_outgoing_nodes(E.task_level))
                start_basic_blocks.append(subtask.entry_abb)


        fixpoint = FixpointIteration(start_basic_blocks)
        fixpoint.do(self.block_functor)

class MoveFunctionsToTask(Analysis):
    """This pass uses the results of the CurrentRunningSubtask analysis to
    move loose functions to the Task the only calling Subtask belongs
    to. This ensures that every ABB belongs exactly to a single
    Task/Subtask by calling CurrentRunningSubtask.for_abb()
    """
    def __init__(self):
        Analysis.__init__(self)

    def requires(self):
        return [CurrentRunningSubtask.name()]

    def __event_mask(self, arg):
        if isinstance(arg, str):
            return [arg]
        if isinstance(arg, Event):
            return [arg]
        if isinstance(arg, int):
            return [arg]
        ret = []
        for x in arg:
            ret += self.__event_mask(x)
        return ret

    def do(self):
        subtask_analysis = self.get_analysis("CurrentRunningSubtask")
        for abb in self.system_graph.abbs:
            subtask = subtask_analysis.for_abb(abb) or abb.subtask
            # The function belongs to a single subtask. If it is a
            # normal function and not yet moved to a task, move it there.
            if abb.function.task == None \
               and subtask != None:
                subtask.task.add_function(abb.function)
                abb.function.subtask = subtask
                logging.debug("Moving %s to %s", abb.function, subtask.task)

            if subtask:
                self.stats.add_child(subtask, "abb", abb)
            else:
                assert abb.isA(S.computation) or abb.isA(S.StartOS), (abb.function.is_system_relevant, abb.path())

        # Find the Event mappings. At this point we have enough
        # information about the calling subtask, to rewrite the *Event
        # arguments to the actual system calls.
        for abb in self.system_graph.abbs:
            if abb.isA([S.WaitEvent, S.GetEvent, S.ClearEvent, S.SetEvent]):
                if abb.isA(S.SetEvent):
                    subtask = abb.arguments[0]
                    events = self.__event_mask(abb.arguments[1])
                elif abb.isA(S.GetEvent):
                    abb.arguments = [abb.arguments[0]]
                    continue
                else:
                    events = self.__event_mask(abb.arguments[0])
                    subtask = abb.subtask

                for idx, event in enumerate(events):
                    if isinstance(event, str):
                        assert event.startswith("OSEKOS_EVENT_"),event
                        event = event[len("OSEKOS_EVENT_"):]
                        events[idx] = subtask._events[event]
                    elif isinstance(event, int):
                        found = None
                        for E in subtask.events:
                            if E.event_mask == event:
                                found = E
                                break
                        assert found != None, "Could not find Event with 0x%x mask" % event
                        events[idx] = found
                    assert events[idx] in subtask.events, "Subtask %s does not own Event %s" %(subtask, event)
                abb.arguments = [events]
