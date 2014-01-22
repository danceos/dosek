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

    def call_function(self, block, function, rettype, arguments, prepend = False):
        """Generates a call to a function and stores the result in an
           variable, if it isn't void"""
        ret_var = VariableDefinition.new(self.generator, rettype)
        if ret_var:
            block.add(ret_var)
            name = ret_var.name
        else:
            name = None
        if prepend:
            call    = block.prepend( FunctionCall(function, arguments, name))
        else:
            call    = block.add( FunctionCall(function, arguments, name))
        return ret_var
