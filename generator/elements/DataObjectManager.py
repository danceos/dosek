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

    def __init__(self, typename, name,
                 static_initializer = None,
                 dynamic_initializer = False,
                 extern_c = False):
        self.typename = typename;
        self.name = name;
        self.static_initializer = static_initializer
        self.dynamic_initializer = dynamic_initializer
        self.data_object_manager = None
        self.phase = 0
        self.extern_c = extern_c
        self.declaration_prefix = ""
        self.allocation_prefix = ""

    def source_element_declaration(self):
        """Builds an extern declaration of the data object"""
        prefix = "extern "
        if self.extern_c:
            prefix += '"C" '
        return Statement(self.declaration_prefix + prefix + self.typename + " " + self.name)

    def source_element_allocation(self):
        """Builds an allocation statement for the object.

            If a static_initializer is set, the object
            is initialized accordingly.

            Example: typename = 'int', name = 'x', static_initializer = 23
            emits:

                int x = 23;

            @return A Statement comprising the C allocation code
        """
        if self.static_initializer != None and self.static_initializer[0] != "(":
            return Statement(self.allocation_prefix
                             + self.typename + " "
                             + self.name + " = "
                             + str(self.static_initializer));
        if self.static_initializer != None and self.static_initializer[0] == "(":
            return Statement(
                self.allocation_prefix
                + self.typename + " "
                + self.name
                + str(self.static_initializer))
        return Statement(self.typename + " " + self.name);

    def source_element_initializer(self):
        """Builds a dynamic initialization statement.

            :returns: A Statement invoking the init() method of the object
        """
        if self.dynamic_initializer:
            return Statement(self.data_object_manager.get_namespace() + "::" + self.name + ".init()")
        return []

class DataObjectArray(DataObject):
    def __init__(self, typename, name, elements, dynamic_initializer = False, extern_c = False):
        DataObject.__init__(self, typename, name, None, dynamic_initializer,
                            extern_c)
        self.elements = elements

    def source_element_declaration(self):
        prefix = "extern "
        if self.extern_c:
            prefix += '"C" '
        return Statement(self.declaration_prefix + prefix + self.typename 
                         + " " + self.name + "[" + self.elements + "]")

    def source_element_initializer(self):
        if self.dynamic_initializer:
            loop = ForRange(0, self.elements)
            loop.add(Statement("%s::%s[%s].init()"%(self.data_object_manager.get_namespace(),
                                                   self.name, loop.get_counter())))
            return loop
        return []

    def source_element_allocation(self):
        if self.static_initializer != None:
            init = "{" + ", ".join(self.static_initializer) + "}"
            return Statement("%s%s %s[%s] = %s" %(self.allocation_prefix,
                                                  self.typename, self.name, self.elements,
                                                  init))
        return Statement("%s%s %s[%s]" %(self.allocation_prefix, self.typename, self.name, self.elements))

    def add_static_initializer(self, initializer):
        if self.static_initializer == None:
            self.static_initializer = []
        self.static_initializer.append("/* %d */ "%len(self.static_initializer) +initializer)

class DataObjectManager:
    def __init__(self):
        # Namespace -> [DataObjects]
        self.__objects = {}

    def objects(self):
        """Iterate over all namespaces and collect all data objects"""
        ret = []
        for obj_list in self.__objects.values():
            ret.extend(obj_list)
        return ret

    def add(self, obj, phase = 0, namespace=None):
        obj.data_object_manager = self
        # Check whether data object was already defined with that
        # name/type:
        for old_obj in self.objects():
            if obj.name == old_obj.name:
                assert obj.typename == old_obj.typename, "Variable %s already defined with different type" % obj.name
                # Do not add another instance for this object
                return
        obj.phase = phase

        if not namespace in self.__objects:
            self.__objects[namespace] = []
        self.__objects[namespace].append(obj)

    def __iterate_in_namespaces(self, func):
        ret = []
        for namespace in self.__objects:
            if namespace is None:
                for x in func(self.__objects[None]):
                    ret.append( x )
            else:
                namespaces = list(namespace)
                assert len(namespaces) > 0
                ns = Block("namespace " + namespaces[0])
                last = ns
                for x in namespaces[1:]:
                    n = Block("namespace " + x)
                    last.add(n)
                    last = n

                for x in func(self.__objects[namespace]):
                    last.add( x )

                ret += [ns, "\n"]

        return ret

    def source_element_declaration(self):
        def iterate(objects):
            ret = []
            for o in objects:
                ret.append(o.source_element_declaration())
            return ret
        return self.__iterate_in_namespaces(iterate) + ["\n"]

    def source_element_allocation(self):
        def iterate(objects):
            ret = []
            for o in objects:
                ret.append(o.source_element_allocation())
            return ret
        ret =  self.__iterate_in_namespaces(iterate)
        for namespace in self.__objects.keys():
            if namespace:
                ret += [Statement("using namespace " + "::".join(list(namespace)))]

        return ret + ["\n"]

    def source_element_initializer(self):
        # assert False, "Not implemented yet"
        return []


