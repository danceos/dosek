#!/usr/bin/python

from generator.elements.SourceElement import Block, Statement

class Function:
    def __init__(self, name, rettype, argstype, extern_c = False, attributes = None):
        self.name = name
        self.function_name = name
        self.rettype = rettype
        self.argstype = argstype
        self.statements = []
        self.extern_c = extern_c
        self.attributes = attributes
        if self.attributes == None:
            self.attributes = []

    def unused_parameter(self, parameter):
        if type(parameter) == int:
            self.statements.append (Statement("(void) arg%d" % parameter))
        else:
            self.statements.append (Statement("(void) %s" % parameter))

    def add(self, statement):
        self.statements.append(statement)
        return statement

    def source_element_declarations(self):
        attributes = ""
        if len(self.attributes) > 0:
            attributes = " __attribute__((" + ",".join(self.attributes) + "))"
        decl = "%s%s %s(%s)" %( self.rettype,
                                attributes,
                                self.name,
                                ",".join(self.argstype))
        if self.extern_c:
            decl = 'extern "C" %s' % decl
        return Statement(decl)

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

class FunctionDeclaration(Function):
    def __init__(self, name, rettype, argstype, extern_c = False, attributes = None):
        Function.__init__(self, name, rettype, argstype, extern_c, attributes)

    def add(self, statement):
        assert False, "You cannot add statements to a function DECLARATION"

    def source_element_definitions(self):
        return []

class  FunctionManager:
    def __init__(self):
        self.functions = []

    def add(self, function):
        for x in self.functions:
            assert x.name != function.name, "Duplicate function name"
        self.functions.append(function)

    def source_element_declarations(self):
        ret = []
        # Sort by local and global includes
        for func in self.functions:
            ret.append(func.source_element_declarations())
        ret.append("\n")
        return ret

    def source_element_definitions(self):
        ret = []
        # Sort by local and global includes
        for func in self.functions:
            ret.append(func.source_element_definitions())
        return ret

