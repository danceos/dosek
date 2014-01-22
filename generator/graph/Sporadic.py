
class SporadicEvent:
    def __init__(self, system, name):
        self.system = system
        self.name = name
        self.triggered_in_abb = set()

    def trigger(self, block, state):
        self.triggered_in_abb.add(block)
        return state

class Alarm(SporadicEvent):
    def __init__(self, system, name, subtask):
        SporadicEvent.__init__(self, system, name)
        self.subtask = subtask

    def trigger(self, block, state):
        SporadicEvent.trigger(self, block, state)
        new_state = state.new()
        new_state.set_ready(self.subtask)
        new_state.merge_with(state)
        return new_state


