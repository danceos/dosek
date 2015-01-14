from collections import namedtuple
from .SystemObject import SystemObject

class Counter(SystemObject):
    """SystemObject representing an counter. The .conf is an
       OILObject(Counter) and the .impl is an DataObject.
    """
    def __init__(self, name, configuration):
        super(Counter, self).__init__(name, configuration)

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
        assert state.is_surely_suspended(self.handler)

        # Save current IP
        current_subtask = state.current_abb.function.subtask
        copy_state.set_continuation(current_subtask, state.current_abb)

        # Dispatch to Event Handler
        copy_state.set_continuation(self.handler, self.handler.entry_abb)
        copy_state.set_ready(self.handler)
        copy_state.current_abb = self.handler.entry_abb
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

class Alarm(SporadicEvent, SystemObject):
    def __init__(self, system_graph, alarm_handler, conf, counter, subtask):
        # A alarm belongs to the subtask it activates!
        SporadicEvent.__init__(self, system_graph, conf.name, subtask.task, alarm_handler)
        SystemObject.__init__(self, conf.name, conf)

        # FIXME: when events are supported
        assert self.conf.event == None
        # This syscall is carried by the alarm
        self.carried_syscall = None
        self.subtask = subtask
        self.counter = counter

    def can_trigger(self,state):
        # Soft Counters cannot be triggered from the interrupt
        if self.counter.conf.softcounter:
            return False
        return SporadicEvent.can_trigger(self, state)

class ISR(SporadicEvent):
    def __init__(self, system_graph, isr_handler):
        SporadicEvent.__init__(self, system_graph, isr_handler.function_name,
                               isr_handler.task, isr_handler)
