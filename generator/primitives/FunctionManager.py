#!/usr/bin/python
import unittest

from generator.types import *
from SourceElement import Block, Statement, Newline
import tools

class Function:
    def __init__(self, name, rettype, argstype):
        self.name = name
        self.rettype = rettype
        self.argstype = argstype
        self.statements = []

    def add(self, statement):
        self.statements.append(statement)

    def source_element_declarations(self):
        decl = "%s %s(%s)" %( self.rettype.generate(self.rettype),
                              self.name,
                              ",".join([x.generate(x) for x in self.argstype]))
        return Statement(decl);

    def source_element_definitions(self):
        args = ["%s %s" %(CType.generate(x[1]), x[0]) 
                for x in self.arguments()]
        guard = "%s %s(%s)" %( self.rettype.generate(self.rettype),
                               self.name,
                               ",".join(args))
        block = Block(guard)
        for stmt in self.statements:
            block.add(stmt)
        return [block, Newline()]

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
        ret.append(Newline())
        return ret

    def source_element_definitions(self):
        ret = []
        # Sort by local and global includes
        for func in self.functions.values():
            ret.append(func.source_element_definitions())
        return ret

class TestFunctionManager(unittest.TestCase):
    def test_function_manager(self):
        m = FunctionManager()
        foo = Function("foo", void, [])
        m.add(foo)

        text = tools.format_source_tree(m.source_element_declarations())
        self.assertEqual(text.strip(), """void foo();""")


        text = tools.format_source_tree(m.source_element_definitions())
        self.assertEqual(text.strip(), """void foo() {
}""")

    def test_function_manager_args(self):
        m = FunctionManager()
        foo = Function("foo", StatusType, [EventMaskRefType])
        m.add(foo)

        text = tools.format_source_tree(m.source_element_declarations())
        self.assertEqual(text.strip(), """StatusType foo(EventMaskRefType);""")


        text = tools.format_source_tree(m.source_element_definitions())
        self.assertEqual(text.strip(), """StatusType foo(EventMaskRefType arg0) {
}""")


if __name__ == '__main__':
    unittest.main()

