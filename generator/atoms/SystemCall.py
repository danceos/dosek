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

    @staticmethod
    def atom(syscall, abb, return_variable, arguments):
        return  {'__token': SystemCall,
                 'syscall': syscall,
                 'abb': abb,
                 'return_variable': return_variable,
                 'arguments': arguments}
        
