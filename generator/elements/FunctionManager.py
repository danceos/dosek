#!/usr/bin/python
import unittest

from SourceElement import Block, Statement
from generator import  tools

class Function:
    def __init__(self, name, rettype, argstype, extern_c = False):
        self.name = name
        self.rettype = rettype
        self.argstype = argstype
        self.statements = []
        self.extern_c = extern_c

    def add(self, statement):
        self.statements.append(statement)
        return statement

    def source_element_declarations(self):
        decl = "%s %s(%s)" %( self.rettype,
                              self.name,
                              ",".join(self.argstype))
        if self.extern_c:
            decl = 'extern "C" %s' % decl
        return Statement(decl);

    def source_element_definitions(self):
        args = ["%s %s" %(x[1], x[0])
                for x in self.arguments()]
        guard = "%s %s(%s)" %( self.rettype,
                               self.name,
                               ",".join(args))
        if self.extern_c:
            guard = 'extern "C" %s' % guard

        block = Block(guard)
        for stmt in self.statements:
            block.add(stmt)
        return [block, "\n"]

    def arguments(self):
        ret = []
        for i in range(0, len(self.argstype)):
            ret.append(("arg%d" %(i), self.argstype[i]))
        return ret

class  FunctionManager:
    def __init__(self):
        self.functions = {}

    def add(self, function):
        self.functions[function.name] = function

    def source_element_declarations(self):
        ret = []
        # Sort by local and global includes
        for func in self.functions.values():
            ret.append(func.source_element_declarations())
        ret.append("\n")
        return ret

    def source_element_definitions(self):
        ret = []
        # Sort by local and global includes
        for func in self.functions.values():
            ret.append(func.source_element_definitions())
        return ret

