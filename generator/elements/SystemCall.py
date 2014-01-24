#!/usr/bin/python

from generator.elements.SourceElement import Statement

class SystemCall:
    def __init__(self, syscall, abb, rettype, arguments):
        self.function = syscall
        self.abb      = abb
        self.rettype  = rettype
        self.arguments = arguments

