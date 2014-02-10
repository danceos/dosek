#!/usr/bin/python

from lxml import objectify
import os
from collections import namedtuple


class SystemDescription:
    """The system description represents the system.xml, that describes
    the elements within the application (tasks, alarms, etc...). 

    WARNING: This is only a hacky frontent for the system.xml. Use the Systemgraph for real information."""
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
        def __init__(self, event_element, root_subtask_name, subtasks):
            self.event = event_element
            self.root_subtask = root_subtask_name
            self.subtasks = subtasks

    def getEvent(self, name):
        for event in self.system_dom.periodicevent:
            if event.identifier == name:
                return (name, "periodic", event.period, event.phase, event.jitter)

        for event in self.system_dom.nonperiodicevent:
            if event.identifier == name:
                return (name, "nonperiodic", event.interarrivaltime)

    def getTasks(self):
        tasks = []
        for task in self.system_dom.task:
            event = self.getEvent(task.event)
            assert event != None
            subtasks = {}
            root_subtask = None
            for subtask in task.subtask:
                deadline = (subtask.deadline.type,
                            subtask.deadline.relative,
                            subtask.deadline.deadline)
                subtasks[subtask.handler] = deadline
                if "root" in subtask.keys():
                    root_subtask = subtask.handler
            tasks.append(self.Task(event, root_subtask, subtasks))
        return tasks

    def isISR(self, name):
        if hasattr(self.osek_dom, "ISR"):
            for isr in self.osek_dom.ISR:
                if isr.name == name:
                    return True
        return False

    SubTask = namedtuple("Subtask", ["name", "is_basic", "static_priority", "max_activations",
                                     "autostart", "preemptable"])
    def getSubTasks(self):
        subtasks = []
        for xml in self.osek_dom.TASK:
            subtasks.append(self.SubTask(
                name = str(xml.name),
                is_basic = str(xml.TYPE) == "BASIC",
                preemptable = str(xml.SCHEDULE) == "FULL",
                static_priority = int(str(xml.PRIORITY)),
                max_activations = int(str(xml.ACTIVATION)),
                autostart = str(xml.AUTOSTART) == "TRUE"))
        return subtasks

    def getSubTask(self, name):
        for task in self.getSubTasks():
            if task.name == name:
                return task

    Alarm = namedtuple("Alarm", ["name", "counter", "task", "event",
                                 "armed", "cycletime", "reltime"])

    def getAlarms(self):
        alarms = []
        if not hasattr(self.osek_dom, "ALARM"):
            return []
        for alarm in self.osek_dom.ALARM:
            name = alarm.name
            tasks = []
            events = []
            if hasattr(alarm, "ACTIVATETASK"):
                for task in alarm.ACTIVATETASK:
                    tasks.append(task.TASK)
            if hasattr(alarm, "SETEVENT"):
                for setevent in alarm.SETEVENT:
                    tasks.append(setevent.TASK)
                    events.append(setevent.EVENT)

            armed = False
            cycletime = 0
            reltime = 0
            if hasattr(alarm, "ARMED"):
                armed = (str(alarm.ARMED) == "TRUE")
            if hasattr(alarm, "CYCLETIME"):
                cycletime = int(str(alarm.CYCLETIME))
            if hasattr(alarm, "RELTIME"):
                reltime = int(str(alarm.RELTIME))

            # OSEK Spec 9.2 Only one task or one event is
            # activated
            assert len(tasks) == 1 or (len(tasks == 1 and len(events)) == 1)
            if len(events) == 0:
                events = [None]
            alarms.append(self.Alarm(name = str(name),
                                     counter = str(alarm.COUNTER),
                                     task = tasks[0],
                                     event = events[0],
                                     armed = armed,
                                     cycletime = cycletime,
                                     reltime = reltime))
        return alarms

    Counter = namedtuple("Counter", ["name", "maxallowedvalue", "ticksperbase", "mincycle"])

    def getHardwareCounters(self):
        counters = []
        if not hasattr(self.osek_dom, "HARDWARECOUNTER"):
            return []
        for counter in self.osek_dom.HARDWARECOUNTER:
            counters.append(self.Counter(name = counter.name,
                                         maxallowedvalue = counter.MAXALLOWEDVALUE,
                                         ticksperbase = counter.TICKSPERBASE,
                                         mincycle = counter.MINCYCLE))
        return counters


    ISR = namedtuple("ISR", ["name", "category", "priority", "device"])

    def getISR(self, name):
        if not hasattr(self.osek_dom, "ISR"):
            return
        for isr in self.osek_dom.ISR:
            if isr.name == name:
                return self.ISR(name = isr.name,
                                category = int(isr.CATEGORY),
                                priority = int(isr.PRIORITY),
                                device = int(isr.DEVICE),
                            )

    Resource = namedtuple("Resource", ["name", "tasks"])

    def getResources(self):
        resources = []
        if not hasattr(self.osek_dom, "RESOURCE"):
            return resources
        for res in self.osek_dom.RESOURCE:
            tasks = set([])
            for task in self.osek_dom.TASK:
                if res.name == "RES_SCHEDULER":
                    tasks.add(task.name)
                if not hasattr(task, "RESOURCE"):
                    continue
                for x in task.RESOURCE:
                    if str(x) == res.name:
                        tasks.add(task)
            resources.append(self.Resource(name = res.name,
                                           tasks = list(tasks)))
        return resources


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
        tasks = dict([(x.name, x) for x in self.desc.getSubTasks()])
        self.assertEqual(len(tasks), 3)

        self.assertTrue(tasks["Handler12"].is_basic)
        self.assertEqual(tasks["Handler13"].max_activations, 1)
        self.assertEqual(tasks["Handler11"].static_priority, 5)

if __name__ == "__main__":
    unittest.main()
