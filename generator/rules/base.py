#!/usr/bin/python

from generator.elements import *

class BaseRules:
    def __init__(self):
        self.generator     = None
        self.system_graph  = None
        self.objects       = None
        self.arch_rules    = None
        self.os_rules      = None
        self.syscall_rules = None
        self.stats         = None

    def set_generator(self, generator):
        self.generator = generator
        self.system_graph = generator.system_graph
        self.arch_rules = generator.arch_rules
        self.os_rules   = generator.os_rules
        self.syscall_rules = generator.syscall_rules
        self.stats         = self.system_graph.stats

    def callback_in_valid_passes(self, callback_name, *arguments):
        """Call functions in all passes that are valid"""
        for each in self.system_graph.valid_passes():
            if each.valid and hasattr(each, callback_name):
                getattr(each, callback_name)(self.generator, *arguments)

    def foreach_subtask(self, func):
        """Call func for every subtask, that is a real task and collect the
        results in a list."""
        ret = []
        # Ignore the Idle thread and ISR subtasks
        for subtask in self.system_graph.real_subtasks:
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
            block.prepend( FunctionCall(function, arguments, name))
        else:
            block.add( FunctionCall(function, arguments, name))
        return ret_var
