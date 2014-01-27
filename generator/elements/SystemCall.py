#!/usr/bin/python

class SystemCall:
    def __init__(self, syscall, abb, rettype, arguments):
        self.function = syscall
        self.abb      = abb
        self.rettype  = rettype
        self.arguments = arguments

