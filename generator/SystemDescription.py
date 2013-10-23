#!/usr/bin/python

from lxml import objectify
import os

class SystemDescription:
    """The system description represents the system.xml, that describes
    the elements within the application (tasks, alarms, etc...)"""
    def __init__(self, system_xml):
        self.system_xml = system_xml
        self.system_dom = objectify.parse(open(self.system_xml)).getroot()

        self.osek_xml   = os.path.join(os.path.dirname(system_xml), str(self.system_dom.specificdescription))
        self.osek_dom   = objectify.parse(open(self.osek_xml)).getroot()

    def getName(self):
        return str(self.system_dom.name)

    def isExtended(self):
        return str(self.osek_dom.OS.STATUS) == "EXTENDED"

    def getHooks(self):
        hooks = {}
        for name in ["error", "startup", "shutdown", "pretask", "posttask"]:
            hooks[name] = self.osek_dom.OS[name.upper() + "HOOK"] == "TRUE"
        return hooks

    class Task:
        def __init__(self, xml_elem):
            self.xml = xml_elem

        def getName(self):
            return str(self.xml.name)

        def isBasicTask(self):
            return str(self.xml.TYPE) == "BASIC"

        def isPreemptable(self):
            return str(self.xml.SCHEDULE) == "FULL"

        def getStaticPriority(self):
            return int(str(self.xml.PRIORITY))

        def getMaxActivations(self):
            return int(str(self.xml.ACTIVATION))

        def isAutostart(self):
            return str(self.xml.AUTOSTART) == "TRUE"

        def __str__(self):
            return "<SystemDescription.Task \"%s\" prio:%d basic:%s>"%(self.getName(), self.getStaticPriority(), self.isBasicTask())

    def getTasks(self):
        return dict([(str(x.name), self.Task(x)) for x in self.osek_dom.TASK])

    def getTask(self, name):
        for task in self.osek_dom.TASK:
            if task.name == name:
                return self.Task(task)



################################################################
##
## Testcases
##
################################################################
import unittest

class TestSystemDescription(unittest.TestCase):
    def setUp(self):
        self.desc = SystemDescription("test/system.xml")
    def test_osek_attributes(self):
        self.assertEqual(self.desc.getName(), "TestSystem")
        self.assertFalse(self.desc.isExtended())
        hooks = self.desc.getHooks()
        self.assertTrue(len(hooks) == 5)
        for i in hooks:
            self.assertFalse(hooks[i])

    def test_tasks(self):
        tasks = self.desc.getTasks()
        self.assertEqual(len(tasks), 3)

        self.assertTrue(tasks["Handler12"].isBasicTask())
        self.assertEqual(tasks["Handler13"].getMaxActivations(), 1)
        self.assertEqual(tasks["Handler11"].getStaticPriority(), 5)

if __name__ == "__main__":
    unittest.main()
