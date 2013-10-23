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
