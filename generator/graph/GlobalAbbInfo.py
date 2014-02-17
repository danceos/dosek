class GlobalAbbInfo:
    """Abstract base class for providing information about an ABB in the
    global control flow graph"""
    def __init__(self):
        pass

    @property
    def state_before(self):
        """Returns the system state before the ABB is executed"""
        raise NotImplemented()

    @property
    def states_after(self):
        """Returns a list of possible next system states"""
        raise NotImplemented()

    @property
    def abbs_after(self):
        """Returns list of possible continuations"""
        next_abbs  = set([state.current_abb for state in self.states_after])
        return next_abbs

    @property
    def tasks_after(self):
        """Returns dict (Subtask->ABB) of possible continuations"""
        next_abbs  = self.abbs_after

        # All following tasks (Subtask->ABB)
        next_subtasks = {}
        for next_abb in next_abbs:
            subtask = next_abb.function.subtask
            next_subtasks.setdefault(subtask, [])
            next_subtasks[subtask].append(next_abb)

        return next_subtasks


