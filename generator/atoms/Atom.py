#!/usr/bin/python

import generator.tools
from generator.types import void
from generator.primitives import *

class Atom:
    """Base class for all atoms"""
    def __init__(self):
        pass

    def generate_into(self, generator, function_block):
        pass


class FunctionCall(Atom):
    def __init__(self, name, rettype, arguments, return_variable = None):
        Atom.__init__(self)
        self.function = name
        self.rettype  = rettype
        self.arguments = arguments

        if return_variable == None:
            self.return_variable = tools.new_variable_name()
        else:
            self.return_variable = return_variable

    def generate_into(self, generator, function_block):
        statement = ""
        if self.rettype != void:
            TYPE = self.rettype.generate(self.rettype)
            statement = "%s %s = " %(TYPE, self.return_variable)

        argument_names = [x[0] for x in self.arguments]
        statement += "%s(%s)" % (self.function,
                                 ",".join(argument_names))

        function_block.add(Statement(statement))
