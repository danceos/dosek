
class SporadicEvent:
    def __init__(self, system, name):
        self.system = system
        self.name = name

    def manipulate_state(self, block, state):
        return False # Not changed

class Alarm(SporadicEvent):
    def __init__(self, system, name, subtask):
        SporadicEvent.__init__(self, system, name)
        self.subtask = subtask

    def manipulate_state(self, block, state):
        new_state = state.new()
        new_state.set_ready(self.subtask)
        return state.merge_with(new_state)
