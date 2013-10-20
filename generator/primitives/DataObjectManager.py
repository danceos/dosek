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
import tools
from SourceElement import Block, Statement, ForRange


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
        return ns

    def source_element_initializer(self):
        b = Block("void init_" + self.__namespace + "()")
        for [phase, o] in sorted(self.__objects, key = lambda x: x[0]):
            b.inner.append(o.source_element_initializer())
        return b


################################################################
##
## Testcase
##
################################################################

class TestDataObjectManager(unittest.TestCase):
    def test_plain_objects_declaration(self):
        m = DataObjectManager()

        m.add(DataObject("FooBar", "foobar"))
        m.add(DataObject("int", "count", 42))


        text = tools.format_source_tree(m.source_element_declaration())
        self.assertEqual(text, """namespace data {
    extern FooBar foobar;
    extern int count;
}
""")

    def test_plain_objects_allocation(self):
        m = DataObjectManager()

        m.add(DataObject("FooBar", "foobar"))
        m.add(DataObject("int", "count", 42))


        text = tools.format_source_tree(m.source_element_allocation())
        self.assertEqual(text, """namespace data {
    FooBar foobar;
    int count = 42;
}
""")

    def test_plain_objects_init(self):
        m = DataObjectManager()
        m.add(DataObject("Scheduler", "scheduler", dynamic_initializer = True))

        text = tools.format_source_tree(m.source_element_allocation())
        self.assertEqual(text, """namespace data {
    Scheduler scheduler;
}
""")

        text = tools.format_source_tree(m.source_element_initializer())
        self.assertEqual(text, """void init_data() {
    data::scheduler.init();
}
""")


    def test_array_objects(self):
        m = DataObjectManager()
        ForRange.count = 0
        m.add(DataObjectArray("Task", "tasks", "MAX_TASKS", dynamic_initializer = True))

        text = tools.format_source_tree(m.source_element_allocation())
        self.assertEqual(text, """namespace data {
    Task tasks[MAX_TASKS];
}
""")

        text = tools.format_source_tree(m.source_element_initializer())
        self.assertEqual(text, """void init_data() {
    for (int for_range_0 = 0; for_range_0 < MAX_TASKS; for_range_0++) {
        data::tasks[for_range_0].init();
    }
}
""")

    def test_init_phases(self):
        m = DataObjectManager()
        ForRange.count = 0
        m.add(DataObject("A", "a", dynamic_initializer = True), 0)
        m.add(DataObject("C", "c", dynamic_initializer = True), 3)
        m.add(DataObject("B", "b", dynamic_initializer = True), 2)

        text = tools.format_source_tree(m.source_element_initializer())
        self.assertEqual(text, """void init_data() {
    data::a.init();
    data::b.init();
    data::c.init();
}
""")

    def test_array_objects(self):
        m = DataObjectManager()
        ForRange.count = 0
        tasks = DataObjectArray("Task", "tasks", "MAX_TASKS")
        m.add(tasks)
        tasks.add_static_initializer("{0, 1, 2}")
        tasks.add_static_initializer("{0, 3, 1}")


        text = tools.format_source_tree(m.source_element_allocation())
        self.assertEqual(text, """namespace data {
    Task tasks[MAX_TASKS] = {/* 0 */ {0, 1, 2}, /* 1 */ {0, 3, 1}};
}
""")


if __name__ == '__main__':
    unittest.main()
