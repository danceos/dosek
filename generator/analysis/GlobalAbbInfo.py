class GlobalAbbInfo:
    """Abstract base class for providing information about an ABB in the
    global control flow graph"""
    def __init__(self):
        pass

    @property
    def state_before(self):
        """Returns the system state before the ABB is executed"""
        raise NotImplementedError()

    @property
    def states_after(self):
        """Returns a list of possible next system states"""
        raise NotImplementedError()

    @property
    def abbs_before(self):
        """Returns list of possible source ABBS"""
        raise NotImplementedError()

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


    @property
    def tasks_before(self):
        """Returns dict (Subtask->ABB) of possible tasks before"""
        prev_abbs  = self.abbs_before

        # All following tasks (Subtask->ABB)
        prev_subtasks = {}
        for prev_abb in prev_abbs:
            subtask = prev_abb.function.subtask
            prev_subtasks.setdefault(subtask, [])
            prev_subtasks[subtask].append(prev_abb)

        return prev_subtasks


