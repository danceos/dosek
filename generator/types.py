#!/usr/bin/python

class CType:
    @staticmethod
    def generate(type):
        return type.__name__

class void(CType):
    def __str__(self):
        return "<void>"

class StatusType(CType):
    def __init__(self, state = None):
        self.state = state

    def __str__(self):
        return "<StatusType: " + self.code + ">"

E_UNSPECIFIED  = StatusType(None)
E_OK           = StatusType(0)
E_OS_ACCESS    = StatusType(1)
E_OS_CALLLEVEL = StatusType(2)
E_OS_ID        = StatusType(3)
E_OS_LIMIT     = StatusType(4)
E_OS_NOFUNC    = StatusType(5)
E_OS_RESOURCE  = StatusType(6)
E_OS_STATE     = StatusType(7)
E_OS_VALUE     = StatusType(8)

class TaskType(CType):
    def __init__(self, task):
        self.task = task

    def __str__(self):
        return "<TaskType: " + self.task + ">"

class TaskRefType(CType):
    def __str__(self):
        return "<TaskRefType>"



class TaskStateType(CType):
    def __init__(self, state):
        self.state = state

    def __str__(self):
        return "<TaskStateType: " + self.state + ">"

UNKONW_TASK_STATE = TaskStateType(None)
RUNNING = TaskStateType(0)
WAITING = TaskStateType(1)
READY   = TaskStateType(2)
SUSPENDED = TaskStateType(3)
INVALID_TASK = TaskStateType(4)

class TaskStateRefType(CType):
    def __str__(self):
        return "<TaskStateRefType>"

class ResourceType(CType):
    def __init__(self, prio):
        self.prio = prio

    def __str__(self):
        return "<ResourceType: " + self.prio + ">"

RES_SCHEDULER = ResourceType(100)

class EventMaskType(CType):
    def __str__(self):
        return "<EventMaskType>"

class EventMaskRefType(CType):
    def __str__(self):
        return "<EventMaskRefType>"
