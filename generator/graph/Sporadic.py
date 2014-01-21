
class SporadicEvent:
    def __init__(self, system, name):
        self.system = system
        self.name = name

    def trigger(self, block, state):
        return state

class Alarm(SporadicEvent):
    def __init__(self, system, name, subtask):
        SporadicEvent.__init__(self, system, name)
        self.subtask = subtask

    def trigger(self, block, state):
        new_state = state.new()
        new_state.set_ready(self.subtask)
        new_state.merge_with(state)
        return new_state


