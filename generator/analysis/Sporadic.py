from collections import namedtuple
from .SystemObject import SystemObject
from .Subtask import Subtask

class Counter(SystemObject):
    """SystemObject representing an counter. The .conf is an
       OILObject(Counter) and the .impl is an DataObject.
    """
    def __init__(self, system_graph, name, configuration):
        super(Counter, self).__init__(name, configuration)
        self.system_graph = system_graph

    @property
    def alarms(self):
        return [x for x in self.system_graph.alarms
                if x.conf.counter == self]

class SporadicEvent:
    def __init__(self, system_graph, name, task, handler):
        self.system_graph = system_graph
        self.name = name
        self.triggered_in_abb = set()
        self.task = task
        self.handler = handler

    def can_trigger(self, state):
        # ISRs can only trigger, if we're not in an isr
        if state.current_abb.subtask.conf.is_isr: \
            return False
        # Cannot triggger in region with blocked interrupts
        if state.current_abb.interrupt_block_all \
           or state.current_abb.interrupt_block_os:
            return False

        # If the belonging task promises to be serialized, this event
        # cannot trigger, when any of the subtasks of hat tasks may be running.
        if self.task.does_promise("serialized"):
            if not self.all_task_subtasks_suspended(state):
                return False

        return True

    def trigger(self, state):
        self.triggered_in_abb.add(state.current_abb)

        copy_state = state.copy()
        assert state.is_surely_suspended(self.handler), (state, self.handler)

        # Save current IP
        current_subtask = state.current_abb.subtask
        copy_state.set_continuation(current_subtask, state.current_abb)

        # Dispatch to Event Handler
        entry_abb = self.handler.entry_abb
        # If we use the APP-FSM method to do the SSE, then we have
        # this field available in the handler (== ISR Subtask)
        if hasattr(self.handler, "ApplicationFSMIterator"):
            entry_abb = self.handler.ApplicationFSMIterator(self.handler, self.handler.fsm.initial_state)
        copy_state.set_continuation(self.handler, entry_abb)
        copy_state.set_ready(self.handler)
        copy_state.current_abb = entry_abb
        return copy_state


    def all_task_subtasks_suspended(self, state):
        """Returns whether all subtasks in the belonging task are suspended in
           the given systemstate. All sutbasks must be surely suspended.
        """
        for subtask in self.task.subtasks:
            if state.is_maybe_suspended(subtask):
                continue
            return False
        return True

class AlarmSubtask(SporadicEvent, Subtask):
    def __init__(self, system_graph):
        SporadicEvent.__init__(self, system_graph, "AlarmHandler", system_graph.system_task, self)
        Subtask.__init__(self, system_graph, "AlarmHandler", "OSEKOSAlarmHandler", None)
        self.conf = self.system_graph.MockSubtaskConfig()
        self.conf.is_isr = True
        self.conf.static_priority = (1<<31)
        self.conf.preemptable = False
        self.conf.autostart = False
        self.conf.isr_device = 0

        self.alarms = []

    def can_trigger(self, state):
        # ISRs can only trigger, if we're not in an isr
        if state.current_abb.subtask.conf.is_isr: \
            return False
        # Cannot triggger in region with blocked interrupts
        if state.current_abb.interrupt_block_all \
           or state.current_abb.interrupt_block_os:
            return False

        return any([a.can_trigger(state) for a in self.alarms])


class Alarm(SporadicEvent, SystemObject):
    def __init__(self, system_graph, conf):
        SporadicEvent.__init__(self, system_graph, conf.name, conf.subtask.task, None)
        SystemObject.__init__(self, conf.name, conf)

        # This syscall is carried by the alarm
        self.carried_syscall = None

    def can_trigger(self,state):
        # Soft Counters cannot be triggered from the interrupt
        if self.conf.counter.conf.softcounter:
            return False
        # If the belonging task promises to be serialized, this event
        # cannot trigger, when any of the subtasks of hat tasks may be running.
        if self.task.does_promise("serialized"):
            if not self.all_task_subtasks_suspended(state):
                return False

        return True

    def trigger(self):
        raise NotImplementedError


class ISR(SporadicEvent):
    def __init__(self, system_graph, isr_handler):
        SporadicEvent.__init__(self, system_graph, isr_handler.function_name,
                               isr_handler.task, isr_handler)
