#!/usr/bin/python

from generator.elements import *

class BaseRules:
    def __init__(self):
        self.generator = None
        self.system_graph = None
        self.objects = None

    def set_generator(self, generator):
        self.generator = generator
        self.system_graph = generator.system_graph
        self.objects = generator.objects

    def foreach_subtask(self, func):
        """Call func for every subtask, that is a real task and collect the
        results in a list."""
        ret = []
        for subtask in self.system_graph.get_subtasks():
            if not subtask in self.objects:
                self.objects[subtask] = {}
            # Ignore the Idle thread and ISR subtasks
            if not subtask.is_real_thread():
                continue
            ret += func(subtask)
        return ret
