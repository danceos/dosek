#!/usr/bin/python

"""
    @file 
    @ingroup primitives
    @brief Builds a source line.
"""


class SourceElement:
    def __init__(self):
        self.__indent = 0
    def indent_spaces(self):
        return " " * (self.__indent * 4)
    def set_indent(self, indent):
        self.__indent = indent
    def get_indent(self):
        return self.__indent



class Comment(SourceElement):
    def __init__(self, text):
        SourceElement.__init__(self)
        self.text = text
    def generate(self):
        if "\n" in self.text:
            # A multiline comment
            prefixed = self.text.replace("\n", "\n" + self.indent_spaces()+ " * ")
            return "\n" + self.indent_spaces() + "/* " + prefixed + "\n" \
                + self.indent_spaces() + " */\n"
        else:
            # Single line comment
            return "\n" + self.indent_spaces() + "// " + self.text + "\n"


class CPPStatement(SourceElement):
    def __init__(self, cmd, arg):
        SourceElement.__init__(self)
        self.cmd = cmd
        self.arg = arg

    def generate(self):
        return "#" + self.indent_spaces() + self.cmd + " " + self.arg + "\n"

class Statement(SourceElement):
    def __init__(self, statment):
        SourceElement.__init__(self)
        self.statement = statement

    def generate(self):
        return self.indent_spaces() + self.statement + ";"


class Block(SourceElement):
    def __init__(self, static_guard = ""):
        SourceElement.__init__(self)
        self.inner = []
        self.static_guard = static_guard

    def block_guard(self):
        return self.static_guard

    def add(self, obj):
        self.inner.append(obj)

    def generate(self):
        ret = self.indent_spaces() + self.block_guard() + " {\n"
        for i in self.inner:
            i.set_indent(self.get_indent() + 1)
            ret += i.generate();
        ret += self.indent_spaces() + "}\n"
        return ret;


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
    def generate(self):
        return self.indent_spaces() + self.statement + ";\n";


class Newline(SourceElement):
    def __init__(self):
        SourceElement.__init__(self)
    def generate(self):
        return "\n"
