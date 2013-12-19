#!/usr/bin/python

"""
    @file 
    @ingroup primitives
    @brief Builds a source line.
"""

from generator.Atom import Atom
from generator.tools import format_source_tree

class SourceElement(Atom):
    def __init__(self):
        Atom.__init__(self)

class Comment(SourceElement):
    def __init__(self, text):
        SourceElement.__init__(self)
        self.text = text
    def expand(self, generator):
        if "\n" in self.text:
            # A multiline comment
            prefixed = [Indent(), "/* ",]
            for line in self.text.split("\n"):
                prefixed += [line + "\n", Indent(), " * " ]
            prefixed = prefixed[:-2] + [Indent(), " */\n"]
            return prefixed
        else:
            # Single line comment
            return [Indent(), "// " + self.text + "\n"]

    @staticmethod
    def atom(fmt, *args):
        return {"__token": Comment, "text": fmt % args}


class CPPStatement(SourceElement):
    def __init__(self, cmd, arg):
        SourceElement.__init__(self)
        self.cmd = cmd
        self.arg = arg

    def expand(self, generator):
        return ["#", Indent(), self.cmd + " " + self.arg + "\n"]

class Statement(SourceElement):
    def __init__(self, statment):
        SourceElement.__init__(self)
        self.statement = statement

    def expand(self):
        return [Indent(), self.statement + ";"]


class Block(SourceElement):
    # Class Member
    indentation_level = 0

    @staticmethod
    def indent_spaces():
        return " " * (Block.indentation_level * 4)

    def __init__(self, static_guard = "", statements = None):
        SourceElement.__init__(self)
        if statements is None:
            self.inner = []
        else:
            self.inner = statements
        self.static_guard = static_guard

    def block_guard(self):
        return self.static_guard

    @staticmethod
    def atom(static_guard, statements):
        return {"__token": Block, "static_guard": static_guard,
                "__statements": statements}

    def add(self, obj):
        self.inner.append(obj)

    def expand(self, generator):
        ret = [Block.indent_spaces() + self.block_guard() + " {\n"]
        Block.indentation_level += 1
        for i in self.inner:
            ret += format_source_tree(generator, i)
        Block.indentation_level -= 1
        ret += Block.indent_spaces() + "}\n"
        return ret;

    def __str__(self):
        return "<<" + ", ".join([str(x) for x in self.inner]) + ">>"


class ForRange(Block):
    count = 0

    def __init__(self, lower = 0, upper = 0):
        Block.__init__(self)
        self.lower = lower
        self.upper = upper
        self.__var = "for_range_" + str(self.count)
        self.count += 1

    def block_guard(self):
        return "for (int %s = %s; %s < %s; %s++)"%(self.__var, self.lower,
                                                   self.__var, self.upper,
                                                   self.__var)

    def get_counter(self):
        return self.__var

class Statement(SourceElement):
    def __init__(self, statement):
        SourceElement.__init__(self)
        self.statement = statement
    def expand(self, generator):
        return [Indent(), self.statement + ";\n"]

    @staticmethod
    def atom():
        return {"__token": Statement}
    @staticmethod
    def atom_return(expression):
        return {"__token": Statement, "statement": "return %s" % expression}

class Indent(SourceElement):
    def __init__(self):
        SourceElement.__init__(self)
    def expand(self, generator):
        return [Block.indent_spaces()]
