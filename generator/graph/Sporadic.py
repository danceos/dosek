class SporadicEvent:
    def __init__(self, system_graph, name, task):
        self.system_graph = system_graph
        self.name = name
        self.triggered_in_abb = set()
        self.task = task

    def can_trigger(self, state):
        return True

    def trigger(self, state):
        self.triggered_in_abb.add(state.current_abb)
        return state

    def all_task_subtasks_suspended(self, state):
        """Returns whether all subtasks in the belonging task are suspended in
           the given systemstate. All sutbasks must be surely suspended.
        """
        for subtask in self.task.subtasks:
            if state.is_maybe_suspended(subtask):
               continue
            return False
        return True

class Alarm(SporadicEvent):
    def __init__(self, system_graph, alarm_handler, alarm_info, subtask):
        # A alarm belongs to the subtask it activates!
        SporadicEvent.__init__(self, system_graph, alarm_info.name, subtask.task)
        # FIXME: when events are supported
        assert alarm_info.event == None
        # An alarm handler is a function with one activate task
        self.handler = alarm_handler
        self.subtask = subtask
        self.counter = alarm_info.counter
        self.initial_armed = alarm_info.armed
        self.initial_cycletime = alarm_info.cycletime
        self.initial_reltime = alarm_info.reltime

    def can_trigger(self, state):
        # ISRs can only trigger, if we're not in an isr
        if state.current_abb.function.subtask.is_isr \
           or state.current_abb.function.is_system_function:
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
        SporadicEvent.trigger(self, state)
        copy_state = state.copy()
        current_subtask = state.current_abb.function.subtask
        copy_state.set_continuation(current_subtask, state.current_abb)
        copy_state.current_abb = self.subtask.entry_abb
        copy_state.set_ready(self.subtask)
        return copy_state



class ISR(SporadicEvent):
    def __init__(self, system_graph, isr_handler):
        SporadicEvent.__init__(self, system_graph, isr_handler.function_name, isr_handler.task)
        self.handler = isr_handler

    def can_trigger(self, state):
        # ISRs can only trigger, if we're not in an isr
        if state.current_abb.function.subtask.is_isr:
            return False
        # Cannot triggger in region with blocked interrupts
        if state.current_abb.interrupt_block_all \
           or state.current_abb.interrupt_block_os:
            return False
        return True

    def trigger(self, state):
        SporadicEvent.trigger(self, state)
        copy_state = state.copy()
        assert state.is_surely_suspended(self.handler)

        # Save current IP
        current_subtask = state.current_abb.function.subtask
        copy_state.set_continuation(current_subtask, state.current_abb)

        # Dispatch to ISR
        copy_state.set_continuation(self.handler, self.handler.entry_abb)
        copy_state.set_ready(self.handler)
        copy_state.current_abb = self.handler.entry_abb
        return copy_state
