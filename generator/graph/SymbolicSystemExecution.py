from generator.graph.common import *
from generator.graph.Analysis import *
from generator.graph.DynamicPriorityAnalysis import DynamicPriorityAnalysis
from generator.graph.Sporadic import SporadicEvent
from generator.graph.GlobalAbbInfo import GlobalAbbInfo
from generator.graph.SystemSemantic import *
from generator.tools import panic, stack


class SymbolicSystemExecution(Analysis, GraphObject):
    def __init__(self):
        Analysis.__init__(self)
        GraphObject.__init__(self, "SymbolicSystemState", root = True)
        self.states_next = None

        # A member for the RunningTask analysis
        self.running_task = None
        # The SystemCall semantic
        self.system_call_semantic = None

        self.working_stack = None

        self.transitions = None

    def graph_subobjects(self):
        # Wrap each state in a graph subobject 
        subobjects = dict([(x, StateGraphSubobject(self, x))
                           for x in self.states_next.keys()])

        abbs = {}
        # Construct the control flow edges
        for state, next_states in self.states_next.items():
            abb = state.current_abb
            if not abb in abbs:
                abbs[abb] = GraphObjectContainer(label = str(abb),
                                                 color = 'red',
                                                 data = abb.dump())
            abbs[abb].subobjects.append(subobjects[state])
            for next_state in next_states:
                edge = Edge(subobjects[state], subobjects[next_state])
                subobjects[state].edges.append(edge)

        return abbs.values()

    def state_transition(self, source_block, source_state, target_block, target_state):
        self.states_next.setdefault(source_state, set())
        self.states_next[source_state].add(target_state)
        if not target_state in self.states_next:
            self.working_stack.push(target_state)

    def state_functor(self, state):
        # Do the System Call
        after_states = self.system_call_semantic.do_SystemCall(
            state.current_abb, state, self.transitions)

        # Schedule on each possible block
        for next_state in after_states:
            self.system_call_semantic.schedule(state.current_abb, next_state,
                                               lambda source, target, new_state: \
                                                 self.state_transition(source, state, target, new_state))

    def do(self):
        self.running_task = self.get_analysis(CurrentRunningSubtask.name())

        # Instanciate a new system call semantic
        self.system_call_semantic = SystemCallSemantic(self.system, self.running_task)

        self.transitions = {'StartOS': self.system_call_semantic.do_StartOS,
                            'ActivateTask': self.system_call_semantic.do_ActivateTask,
                            'TerminateTask': self.system_call_semantic.do_TerminateTask,
                            'ChainTask': self.system_call_semantic.do_ChainTask,
                            'computation': self.system_call_semantic.do_computation, # Ignore IRQs
                            'SetRelAlarm': self.system_call_semantic.do_computation, # ignore
                            'CancelAlarm': self.system_call_semantic.do_computation, # ignore
                            'GetResource': self.system_call_semantic.do_computation, # Done in DynamicPriorityAnalysis
                            'ReleaseResource': self.system_call_semantic.do_computation, # Done in DynamicPriorityAnalysis
                            'Idle': self.system_call_semantic.do_Idle}

        # Instanciate the big dict (State->[State])
        self.states_next = {}

        entry_abb = self.system.functions["StartOS"].entry_abb
        before_StartOS = SystemState(self.system)
        before_StartOS.current_abb = entry_abb
        before_StartOS.frozen = True

        self.working_stack = stack()
        self.working_stack.push(before_StartOS)

        while not self.working_stack.isEmpty():
            current = self.working_stack.pop()
            self.state_functor(current)


class StateGraphSubobject(GraphObject):
    def __init__(self, analysis, state):
        GraphObject.__init__(self, "State",
                             color = 'green')
        self.analysis = analysis
        self.state = state
        self.edges = []

    def graph_edges(self):
        return self.edges

    def dump(self):
        ret = {}
        for subtask, state in self.state.states.items():
            ret[subtask.name] = self.state.format_state(state)

        return ret
