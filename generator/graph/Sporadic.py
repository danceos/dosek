
class SporadicEvent:
    def __init__(self, system, name):
        self.system = system
        self.name = name
        self.triggered_in_abb = set()

    def trigger(self, block, state):
        self.triggered_in_abb.add(block)
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


    def trigger(self, block, state):
        SporadicEvent.trigger(self, block, state)
        new_state = state.new()
        new_state.set_ready(self.subtask)
        new_state.merge_with(state)
        return new_state


