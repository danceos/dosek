class SporadicEvent:
    def __init__(self, system, name):
        self.system = system
        self.name = name
        self.triggered_in_abb = set()

    def can_trigger(self, state):
        return True

    def trigger(self, state):
        self.triggered_in_abb.add(state.current_abb)
        return state

class Alarm(SporadicEvent):
    def __init__(self, system, alarm_handler, alarm_info, subtask):
        SporadicEvent.__init__(self, system, alarm_info.name)
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
        if state.current_abb.function.subtask.is_isr:
            return False
        return True

    def trigger(self, state):
        SporadicEvent.trigger(self, state)
        copy_state = state.copy()
        if not copy_state.is_surely_ready(self.subtask):
            copy_state.set_continuation(self.subtask, self.subtask.entry_abb)
        copy_state.set_ready(self.subtask)
        return copy_state



class ISR(SporadicEvent):
    def __init__(self, system_graph, isr_handler):
        SporadicEvent.__init__(self, system_graph, isr_handler.function_name)
        self.handler = isr_handler

    def can_trigger(self, state):
        # ISRs can only trigger, if we're not in an isr
        if state.current_abb.function.subtask.is_isr:
            return False
        return True

    def trigger(self, state):
        SporadicEvent.trigger(self, state)
        copy_state = state.copy()
        assert state.is_surely_suspended(self.handler)

        copy_state.set_continuation(self.subtask, self.subtask.entry_abb)
        copy_state.set_ready(self.handler)
        return copy_state
