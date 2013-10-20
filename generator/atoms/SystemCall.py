#!/usr/bin/python

from Atom import Atom
from generator.primitives import Statement

class SystemCall(Atom):
    def __init__(self, syscall, abb, rettype, arguments):
        Atom.__init__(self)
        self.function = syscall
        self.abb      = abb
        self.rettype  = rettype
        self.arguments = arguments

    def generate_into(self, generator, function_block):
        raise "Must lower System calls"
        argument_names = [x[0] for x in self.arguments]
        statement = "return %s(%s)" % (self.function, ",".join(argument_names))
        function_block.add(Statement(statement))
