#!/usr/bin/python
"""
    @ingroup generator
    @defgroup primitives Source file primitives generation
    @{
    Generation of simple primitives
    @}
"""

"""
    @file 
    @ingroup generator
    @brief Data object cook.
"""
import unittest
from generator import tools
from generator.elements.SourceElement import Block, Statement, ForRange


class DataObject:
    """Manages a variable"""

    def __init__(self, typename, variable, static_initializer = None, dynamic_initializer = False):
        self.typename = typename;
        self.variable = variable;
        self.static_initializer = static_initializer
        self.dynamic_initializer = dynamic_initializer
        self.data_object_manager = None

    def source_element_declaration(self):
        """Builds an extern declaration of the data object"""
        return Statement("extern " + self.typename + " " + self.variable)

    def source_element_allocation(self):
        """Builds an allocation statement for the object.

            If a static_initializer is set, the object
            is initialized accordingly.

            Example: typename = 'int', variable = 'x', static_initializer = 23
            emits:

                int x = 23;

            @return A Statement comprising the C allocation code 
        """
        if self.static_initializer != None:
            return Statement(self.typename + " " + self.variable + " = " + str(self.static_initializer));
        return Statement(self.typename + " " + self.variable);

    def source_element_initializer(self):
        """Builds a dynamic initialization statement.

            :returns: A Statement invoking the init() method of the object
        """
        if self.dynamic_initializer:
            return Statement(self.data_object_manager.get_namespace() + "::" + self.variable + ".init()")
        return []

class DataObjectArray(DataObject):
    def __init__(self, typename, variable, elements, dynamic_initializer = False):
        DataObject.__init__(self, typename, variable, None, dynamic_initializer)
        self.elements = elements

    def source_element_declaration(self):
        return Statement("extern " + self.typename + " " + self.variable + "[" + self.elements + "]")

    def source_element_initializer(self):
        if self.dynamic_initializer:
            loop = ForRange(0, self.elements)
            loop.add(Statement("%s::%s[%s].init()"%(self.data_object_manager.get_namespace(),
                                                   self.variable, loop.get_counter())))
            return loop
        return []

    def source_element_allocation(self):
        if self.static_initializer != None:
            init = "{" + ", ".join(self.static_initializer) + "}"
            return Statement("%s %s[%s] = %s" %(self.typename, self.variable, self.elements,
                                                init))
        return Statement("%s %s[%s]" %(self.typename, self.variable, self.elements))

    def add_static_initializer(self, initializer):
        if self.static_initializer == None:
            self.static_initializer = []
        self.static_initializer.append("/* %d */ "%len(self.static_initializer) +initializer)

class DataObjectManager:
    def __init__(self, namespace = "data"):
        self.__namespace = namespace
        self.__objects = []

    def get_namespace(self):
        return self.__namespace

    def add(self, obj, phase = 0):
        obj.data_object_manager = self
        # Check whether data object was already defined with that
        # name/type:
        for _, old_obj in self.__objects:
            if obj.variable == old_obj.variable:
                assert obj.typename == old_obj.typename, "Variable %s already defined with different type" % obj.variable
                # Do not add another instance for this object
                return
        self.__objects.append([phase, obj])

    def source_element_declaration(self):
        ns = Block("namespace " + self.__namespace)
        for [phase, o] in self.__objects:
            ns.add(o.source_element_declaration())
        return ns

    def source_element_allocation(self):
        ns = Block("namespace " + self.__namespace)
        for [phase, o] in self.__objects:
            ns.add(o.source_element_allocation())
        return [ns, Statement("using namespace " + self.__namespace)]

    def source_element_initializer(self):
        b = Block("void init_" + self.__namespace + "()")
        for [phase, o] in sorted(self.__objects, key = lambda x: x[0]):
            inner = o.source_element_initializer()
            if type(inner) != list:
                inner = [inner]
            b.inner += inner
        return b


