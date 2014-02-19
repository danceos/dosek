
class SporadicEvent:
    def __init__(self, system, name):
        self.system = system
        self.name = name
        self.triggered_in_abb = set()

    def trigger(self, state):
        self.triggered_in_abb.add(state.current_abb)
        return state

class Alarm(SporadicEvent):
    def __init__(self, system, subtask, alarm_info):
        SporadicEvent.__init__(self, system, alarm_info.name)
        # FIXME: when events are supported
        assert alarm_info.event == None
        self.subtask = subtask
        self.counter = alarm_info.counter
        self.initial_armed = alarm_info.armed
        self.initial_cycletime = alarm_info.cycletime
        self.initial_reltime = alarm_info.reltime


    def trigger(self, state):
        SporadicEvent.trigger(self, state)
        copy_state = state.copy()
        if not copy_state.is_surely_ready(self.subtask):
            copy_state.add_continuation(self.subtask, self.subtask.entry_abb)
        copy_state.set_ready(self.subtask)
        return copy_state


