class SystemImpl:
    def __init__(self):
        self.StartOS = None

        self.scheduler = None
        self.basic_task_stackptr = None

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

class AlarmImpl:
    def __init__(self):
        self.alarm_id   = None
        self.name = None
        self.alarm_desc = None

class EventImpl:
    def __init__(self):
        self.event_mask   = None
        self.name = None

class SyscallImplementation:
    def __init__(self):
        self.userspace   = None
        self.kernelspace = None
        self.pre_hook    = None
        self.post_hook   = None

        self.rettype = None
        self.argtyes = None
