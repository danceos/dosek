class SystemImpl:
    def __init__(self):
        self.StartOS = None

        self.scheduler = None

class SubtaskImpl:
    def __init__(self):
        # Stack
        self.stack = None
        self.stackptr = None
        self.stacksize = None

        self.entry_function = None
        self.task_id = None
        self.task_descriptor = None
        self.tcb_descriptor = None

        self.generated_functions = []

        # For Encoded Tasks
        self.task_id_sig = None
        self.task_prio_sig = None


class EncodedSchedulerImpl:
    def __init__(self):
        self.scheduler_prio_sig = None
        self.current_prio_sig = None
        self.current_task_sig = None
