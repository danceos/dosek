#!/usr/bin/python

from generator.Atom import Atom
from generator.atoms import *
from generator.primitives import *


class VariableDefinition(Atom):
    def __init__(self, datatype, name):
        Atom.__init__(self)
        self.datatype = datatype
        self.name = name
    def expand(self, generator):
        statement = "%s %s" % ( self.datatype, self.name )
        return [Statement(statement)]
    @staticmethod
    def atom(generator, datatype):
        if datatype == "void":
            return None
        varname = generator.variable_name_for_datatype(datatype)
        return {"__token": VariableDefinition, "datatype": datatype, "name": varname}

class FunctionCall(Atom):
    def __init__(self, name, arguments, return_variable = None):
        Atom.__init__(self)
        self.function = name
        self.arguments = arguments
        self.return_variable = return_variable

    @staticmethod
    def atom(function, arguments, return_variable):
        return {"__token": FunctionCall, "name": function,
                "arguments": arguments, "return_variable": return_variable}

    def expand(self, generator):
        statement = ""
        if self.return_variable != None:
            statement += "%s = "% self.return_variable

        argument_names = [x[0] for x in self.arguments]
        statement += "%s(%s)" % (self.function,
                                 ",".join(argument_names))

        return [Statement(statement)]

class Hook(Atom):
    def __init__(self, name):
        Atom.__init__(self)
        self.name = name

    @staticmethod
    def atom(name):
        block = Block.atom("/* %s */"% name, [{"__token": Hook, "name": name}])
        return block

    def expand(self, generator):
        return [Comment("Hook: " + self.name)]

