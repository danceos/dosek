#!/usr/bin/python

from .SourceElement import Block, Statement
from collections import namedtuple

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
            name = "arg%d" % (parameter)
        else:
            name = parameter

        self.statements.append (Statement("(void) %s" % name))

    def add(self, statement):
        self.statements.append(statement)
        return statement

    def prepend(self, statement):
        self.statements = [statement] + self.statements
        return statement


    def source_element_declarations(self):
        attributes = " ".join(self.attributes)
        decl = "%s %s %s(%s)" %(self.rettype,
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

    def arguments_names(self):
        return [arg[0] for arg in self.arguments()]

    def arguments_types(self):
        return [arg[1] for arg in self.arguments()]


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


class FunctionDefinitionBlock(Function):
    """ Can be used to declare bare definition blocks, like

        ISR(42) {
        }
    """

    def __init__(self, name, definition_args):
        Function.__init__(self, name, rettype = None, argstype = None, extern_c = None, attributes = None)
        self.definition_args = definition_args
        self.function_name = "%s(%s) " %(self.name, ", ".join(self.definition_args))
        self.name = self.function_name

    def source_element_declarations(self):
        return []

    def source_element_definitions(self):
        block = Block(self.function_name)
        for stmt in self.statements:
            block.add(stmt)
        return [block, "\n"]

class  FunctionManager:
    Namespace = namedtuple("Namespace", ["name", "functions"])

    def __init__(self):
        self.functions = []
        self.namespaces = []

    def add(self, function, namespace = None):
        current_scope = None
        if namespace is None:
            current_scope = self.functions
        else:
            for ns in self.namespaces:
                if ns.name is namespace:
                    current_scope = ns.functions
                    break
            if current_scope is None:
                self.namespaces.append(self.Namespace(namespace, []))
                current_scope = self.namespaces[-1].functions
        for x in current_scope:
            assert x.name != function.name, "Duplicate function name %s" % function.name
        current_scope.append(function)

    def source_element_declarations(self):
        ret = []
        # Sort by local and global includes
        for func in self.functions:
            ret.append(func.source_element_declarations())
        ret.append("\n")
        for ns in self.namespaces:
            ret.append("namespace " + ns.name + " {\n");
            for func in ns.functions:
                ret.append(func.source_element_declarations())
            ret.append("\n}\n")

        return ret

    def source_element_definitions(self):
        ret = []
        # Sort by local and global includes
        for func in self.functions:
            ret.append(func.source_element_definitions())
        for ns in self.namespaces:
            ret.append("namespace " + ns.name + " {\n");
            for func in ns.functions:
                ret.append(func.source_element_definitions())
            ret.append("\n}\n")
        return ret

