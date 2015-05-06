#!/usr/bin/python

"""
    @file
    @ingroup primitives
    @brief Builds a source line.
"""

from generator.tools import format_source_tree

class SourceElement():
    def __init__(self):
        pass

class Comment(SourceElement):
    def __init__(self, text):
        SourceElement.__init__(self)
        if len(text) > 72:
            # Split text at 72 characters
            current_line = 0
            self.text = ""
            for word in text.split(" "):
                self.text += word
                current_line += len(word) + 1
                if current_line > 72:
                    self.text += "\n"
                    current_line = 0
                else:
                    self.text += " "
            self.text = self.text.strip()
        else:
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

class CPPStatement(SourceElement):
    def __init__(self, cmd, arg):
        SourceElement.__init__(self)
        self.cmd = cmd
        self.arg = arg

    def expand(self, generator):
        return ["#", Indent(), self.cmd + " " + self.arg + "\n"]

class Block(SourceElement):
    # Class Member
    indentation_level = 0

    @staticmethod
    def indent_spaces():
        return " " * (Block.indentation_level * 4)

    def __init__(self, static_guard = "", statements = None, arguments = None):
        SourceElement.__init__(self)
        if statements is None:
            self.inner = []
        else:
            self.inner = statements
        self.static_guard = static_guard
        self.__arguments = arguments

    def arguments(self):
        return self.__arguments

    def block_guard(self):
        return self.static_guard

    def add(self, obj):
        self.inner.append(obj)
        return obj

    def prepend(self, statement):
        self.inner = [statement] + self.inner
        return statement

    def expand(self, generator):
        ret = [Block.indent_spaces() + self.block_guard() + "{\n"]
        Block.indentation_level += 1
        for i in self.inner:
            ret += format_source_tree(generator, i)
        Block.indentation_level -= 1
        ret += Block.indent_spaces() + "}\n"
        return ret

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

class Indent(SourceElement):
    def __init__(self):
        SourceElement.__init__(self)
    def expand(self, generator):
        return [Block.indent_spaces()]

class VariableDefinition(SourceElement):
    def __init__(self, datatype, name, array_length = None):
        SourceElement.__init__(self)
        self.datatype = datatype
        self.name = name
        self.array_length = array_length

    def expand(self, generator):
        if self.array_length:
            statement = "%s %s[%s]" % ( self.datatype, self.name, self.array_length )
        else:
            statement = "%s %s" % ( self.datatype, self.name )
        return [Statement(statement)]

    @staticmethod
    def new(generator, datatype, array_length = None):
        if datatype == "void":
            return None
        varname = generator.variable_name_for_datatype(datatype)
        return VariableDefinition(datatype, varname, array_length)

class FunctionCall(SourceElement):
    def __init__(self, name, arguments, return_variable = None):
        SourceElement.__init__(self)
        self.function = name
        self.arguments = arguments
        self.return_variable = return_variable

    def expand(self, generator):
        statement = ""
        if self.return_variable != None:
            statement += "%s = "% self.return_variable

        statement += "%s(%s)" % (self.function,
                                 ", ".join(self.arguments))

        return [Statement(statement)]

class Hook(Block):
    def __init__(self, name, arguments = None):
        Block.__init__(self, arguments = arguments)
        self.name = name

    def expand(self, generator):
        return [Comment("Hook: " + self.name), Block.expand(self, generator)]

    def __str__(self):
        return "<Hook: %s>" % self.name

