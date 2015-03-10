#!/usr/bin/env python3
"""Parse OIL (OSEK Implementation Language) files.
   see: http://portal.osek-vdx.org/files/pdf/specs/oil25.pdf
"""
from pyparsing import (Word, alphanums, alphas, hexnums,
                       nums, Optional, Keyword, QuotedString, Suppress,
                       Group, Forward, ZeroOrMore, cStyleComment, restOfLine)

""" This is an example oil description:
CPU Josek_x86 {
        OS JOSEK {
                USEPARAMETERACCESS = FALSE;
                STATUS = STANDARD;
                USERESSCHEDULER = FALSE;
                USEGETSERVICEID = FALSE;
                POSTTASKHOOK = TRUE;
                STARTUPHOOK = TRUE;
                PRETASKHOOK = TRUE;
        };

        TASK task1 {
                AUTOSTART = TRUE {
                        APPMODE = OSDEFAULTAPPMODE;
                };
                ACTIVATION = 1;
                PRIORITY = 1;
                SCHEDULE = NON;
        };

        APPMODE OSDEFAULTAPPMODE { };

        APPMODE OSDEFAULTAPPMODE { };

};
"""


class OILObject:

    def __init__(self, name=""):
        self.name = name

    def evaluate(self, oil):
        self.name = oil[0][1]
        for param in oil[1]:
            if hasattr(self, param[0]):
                setattr(self, param[0], param[1])

    def __str__(self):
        ret = self.__class__.__name__ + " : " + str(self.name)
        for k, v in vars(self).items():
            if k.isupper():  # if it it a uppercase OIL Keyword
                # lowercase members are special sets or lists
                ret += "\n\t\t" + str(k) + ": " + str(v)
        return ret


class AppMode(OILObject):

    def __init__(self, name=""):
        super(AppMode, self).__init__(name)


class Resource(OILObject):

    def __init__(self, name=""):
        super(Resource, self).__init__(name)
        self.RESOURCEPROPERTY = ""
        self.static_priority = 0
        self.tasks = dict()

    def __str__(self):
        ret = super(Resource, self).__str__()
        if self.tasks:
            ret += "\n\t\tUsed by task(s): " + str(self.tasks)
        return ret




class CheckedObject(OILObject):

    def __init__(self, name=""):
        super(CheckedObject, self).__init__(name)
        self.TYPEDEF = ""
        self.HEADER = None
        self.CHECKFUNCTION = None

    @property
    def typename(self):
        return self.TYPEDEF

    @property
    def header(self):
        return self.HEADER

    @property
    def checkfunc(self):
        return self.CHECKFUNCTION


class Event(OILObject):

    def __init__(self, name=""):
        super(Event, self).__init__(name)
        self.MASK = "AUTO"


class Counter(OILObject):

    def __init__(self, name=""):
        super(Counter, self).__init__(name)
        self.MAXALLOWEDVALUE = ""
        self.TICKSPERBASE = ""
        self.MINCYCLE = ""
        self.SOFTCOUNTER = False

    @property
    def maxallowedvalue(self):
        return self.MAXALLOWEDVALUE

    @property
    def ticksperbase(self):
        return self.TICKSPERBASE

    @property
    def mincycle(self):
        return self.MINCYCLE

    @property
    def softcounter(self):
        return self.SOFTCOUNTER


class Alarm(OILObject):

    class ActionParam:
        def __str__(self):
            ret = self.__class__.__name__
            for k, v in vars(self).items():
                if k.isupper():
                    ret += "\n\t\t\t" + str(k) + ": " + str(v)
            return ret

    class ACTIVATETASK(ActionParam):
        def __init__(self, task=""):
            self.TASK = task

    class SETEVENT(ActionParam):
        def __init__(self, task="", event=""):
            self.TASK = task
            self.EVENT = event

    class ALARMCALLBACK(ActionParam):
        def __init__(self, cb=""):
            self.ALARMCALLBACKNAME = cb

    class AutostartParams(ActionParam):
        def __init__(self):
            self.ALARMTIME = 0
            self.CYCLETIME = 0
            self.APPMODE = set()

    def __init__(self, name=""):
        super(Alarm, self).__init__(name)
        self.__counter = None
        self.COUNTER = ""
        self.ACTION = ""
        self.action_params = None
        self.AUTOSTART = False
        self.autostart_params = None

    def evaluate(self, oil):
        super(Alarm, self).evaluate(oil)
        ''' read out alarm actions '''
        for param in oil[1]:
            if param[0] == "ACTION" and len(param) > 2:
                if param[1] == "SETEVENT":
                    self.action_params = self.SETEVENT()
                elif param[1] == "ACTIVATETASK":
                    self.action_params = self.ACTIVATETASK()
                elif param[1] == "ALARMCALLBACK":
                    self.action_params = self.ALARMCALLBACK()

                for acp in param[2:]:
                    if hasattr(self.action_params, acp[0]):
                        setattr(self.action_params, acp[0], acp[1])

            ''' read out autostart parameters '''
            if param[0] == "AUTOSTART" and len(param) > 2 and param[1] is True:
                self.autostart_params = self.AutostartParams()
                for acp in param[2:]:
                    if acp[0] == "ALARMTIME":
                        self.autostart_params.ALARMTIME = int(acp[1])
                    elif acp[0] == "CYCLETIME":
                        self.autostart_params.CYCLETIME = int(acp[1])
                    elif acp[0] == "APPMODE":
                        self.autostart_params.APPMODE.add(acp[1])

    @property
    def counter(self):
        if self.__counter:
            return self.__counter
        return self.COUNTER.name

    @counter.setter
    def counter(self, value):
        self.__counter = value

    @property
    def armed(self):
        return self.AUTOSTART

    @property
    def cycletime(self):
        if self.autostart_params:
            return self.autostart_params.CYCLETIME
        return 0

    @property
    def reltime(self):
        if self.autostart_params:
            return self.autostart_params.ALARMTIME
        return 0

    @property
    def subtask(self):
        if self.action_params.TASK:
            if isinstance(self.action_params.TASK, Task):
                return self.action_params.TASK.name
            return self.action_params.TASK
        else:
            return None

    @subtask.setter
    def subtask(self, value):
        self.action_params.TASK = value


    @property
    def event(self):
        if hasattr(self.action_params, "EVENT") and self.action_params.EVENT:
            if isinstance(self.action_params.EVENT, Event):
                return self.action_params.EVENT.name
            return self.action_params.EVENT
        else:
            return None

    @event.setter
    def event(self, value):
        self.action_params.EVENT = value


    def __str__(self):
        ret = super(Alarm, self).__str__()
        ret += "\n\t\tAction Params: " + str(self.action_params)
        if self.autostart_params:
            ret += "\n\t\tAutostart Params: " + str(self.autostart_params)
        return ret


class TaskGroup(OILObject):

    def __init__(self, name=""):
        super(TaskGroup, self).__init__(name)
        self.promises = dict()

    def evaluate(self, oil):
        super(TaskGroup, self).evaluate(oil)

        ''' read out appmodes for autostart '''
        for param in oil[1]:
            if param[0] == "PROMISE":
                self.promises[param[1].lower()] = True


class Task(OILObject):

    def __init__(self, name=""):
        super(Task, self).__init__(name)
        self.AUTOSTART = False
        self.autostart_appmodes = dict()
        self.ACTIVATION = 0
        self.PRIORITY = 0
        self.SCHEDULE = "NON"
        self.TASKGROUP = None
        self.resources = dict()
        self.events = dict()

    def evaluate(self, oil):
        super(Task, self).evaluate(oil)

        ''' read out appmodes for autostart '''
        for param in oil[1]:
            if param[0] == "AUTOSTART":
                if len(param) > 2 and param[1] == "TRUE":
                    ''' if AUTOSTART = TRUE, there should be appmodes to start in '''
                    for appmode in param[2:]:
                        if appmode[0] == "APPMODE":
                            self.autostart_appmodes[appmode[1]] = appmode[1]
            if param[0] == "RESOURCE":
                self.resources[param[1]] = param[1];
            if param[0] == "EVENT":
                self.events[param[1]] = param[1];

    @property
    def preemptable(self):
        return self.SCHEDULE.upper() == "FULL"

    @property
    def max_activations(self):
        return self.ACTIVATION

    @property
    def autostart(self):
        return self.AUTOSTART

    @property
    def static_priority(self):
        return self.PRIORITY

    @static_priority.setter
    def static_priority(self, value):
        self.PRIORITY = value

    @property
    def taskgroup(self):
        if not self.TASKGROUP:
            return self.name
        else:
            return self.TASKGROUP

    @property
    def is_isr(self):
        return False

    @property
    def basic_task(self):
        return False

    def __str__(self):
        ret = super(Task, self).__str__()
        if self.AUTOSTART:
            ret += "\n\t\tAUTOSTART APPMODES: " + str(self.autostart_appmodes)
        if len(self.resources) > 0:
            ret += "\n\t\tRESOURCES: " + str(self.resources)
        return ret


class ISR(OILObject):

    def __init__(self, name=""):
        super(ISR, self).__init__(name)
        self.CATEGORY = ""
        self.PRIORITY = -1
        self.resources = dict()
        self.messages = dict()
        self.DEVICE = None
        self.TASKGROUP = None

        # Assumption: Our subtasks are non-preemptable basic-tasks
        self.preemptable = False
        self.basic_task = True
        self.max_activations = 1
        self.autostart = False
        self.static_priority = None
        self.is_isr = True

    def get_device(self):
        assert self.DEVICE, "No device number set for ISR '" + self.name + "'"
        return self.DEVICE

    @property
    def taskgroup(self):
        if not self.TASKGROUP:
            return self.name
        else:
            return self.TASKGROUP

    @property
    def isr_device(self):
        return self.get_device()


    def evaluate(self, oil):
        super(ISR, self).evaluate(oil)
        for param in oil[1]:
            if param[0] == "RESOURCE":
                self.resources[param[1]] = param[1]

    def __str__(self):
        ret = super(ISR, self).__str__()
        if self.resources:
            ret += "\n\t\tUses resource(s)" + str(self.resources)
        return ret


class OS(OILObject):

    def __init__(self, name=""):
        super(OS, self).__init__(name)
        self.name = name
        self.USEPARAMETERACCESS = False
        self.STATUS = "STANDARD"
        self.USERESSCHEDULER = False
        self.USEGETSERVICEID = False
        self.POSTTASKHOOK = False
        self.STARTUPHOOK = False
        self.PRETASKHOOK = False


class CPU:

    def __init__(self, name=""):
        self.name = name
        self.description = ""
        self.os = OS()
        self.tasks = dict()
        self.appmodes = dict()
        self.resources = dict()
        self.counters = dict()
        self.events = dict()
        self.isrs = dict()
        self.checked_objects = dict()
        self.task_groups = dict()

    def evaluate(self, oil):
        self.name = oil[1]

    def interconnect(self):
        for task in self.tasks.values():
            #  Interconnect resources
            new_taskresources = dict()
            for tres in task.resources:
                assert tres in self.resources, "Resource '" + tres + "' used by Task '" + task.name + "' not found"
                new_taskresources[tres] = self.resources[tres]
                self.resources[tres].tasks[task.name] = task
            task.resources = new_taskresources

            #  Interconnect events
            new_taskevents = dict()
            for tres in task.events:
                assert tres in self.events, "Event '" + tres + "' used by Task '" + task.name + "' not found"
                new_taskevents[tres] = self.events[tres]
            task.events = new_taskevents

            #  Interconnect appmodes
            new_appmodes = dict()
            for tappm in task.autostart_appmodes:
                assert tappm in self.appmodes, "Appmode '" + tappm + "' used by Task '" + task.name + "' not found"
                new_appmodes[tappm] = self.appmodes[tappm]
            task.autostart_appmodes = new_appmodes

        for alarm in self.alarms.values():
            # Interconnect alarm counters
            assert alarm.COUNTER in self.counters, "Counter '" + alarm.COUNTER + "' used by Alarm '" + alarm.name + "' not found"
            alarm.COUNTER = self.counters[alarm.COUNTER]

            if alarm.ACTION == "SETEVENT":
                assert isinstance(alarm.action_params, Alarm.SETEVENT), "Alarm action parameter mismatch"
                altask = alarm.action_params.TASK
                alevent = alarm.action_params.EVENT
                assert altask in self.tasks, "Alarm action task '" + altask + "' not found"
                assert alevent in self.events, "Alarm action event '" + alevent + "' not found"
                alarm.action_params.TASK = self.tasks[altask]
                alarm.action_params.EVENT = self.events[alevent]
            elif alarm.ACTION == "ACTIVATETASK":
                assert isinstance(alarm.action_params, Alarm.ACTIVATETASK), "Alarm action parameter mismatch"
                altask = alarm.action_params.TASK
                assert altask in self.tasks, "Alarm action task '" + altask + "' not found"
                alarm.action_params.TASK = self.tasks[altask]
            elif alarm.ACTION == "ALARMCALLBACK":
                assert isinstance(alarm.action_params, Alarm.ALARMCALLBACK), "Alarm action parameter mismatch"
                # intentionally left blank, there is no callback object defined in oil

            if alarm.autostart_params:
                new_appmodes = dict()
                for appm in alarm.autostart_params.APPMODE:
                    assert appm in self.appmodes, "Appmode '" + appm + "' used by Alarm '" + alarm.name + "' not found"
                    new_appmodes[appm] = self.appmodes[appm]
                alarm.autostart_params.APPMODE = new_appmodes

        for isr in self.isrs.values():
            new_isrresources = dict()
            for isrres in isr.resources:
                assert isrres in self.resources, "ISR uses undefined resource '" + isrres + "'"
                new_isrresources[isrres] = self.resources[isrres]
            isr.resources = new_isrresources


    def __str__(self):
        ret = "CPU " + self.name + "\n\t" + str(self.os)
        for x in [obj.values() for obj in
                  [self.tasks, self.appmodes, self.resources,
                   self.counters, self.alarms, self.events, self.isrs,
                   self.checked_objects]]:
            for xi in x:
                ret += "\n\t" + str(xi)

        return ret


class OILSystemDescription:

    """  This is the pyparsing OIL syntax description  """
    name = Word(alphas+"_", alphanums + "_")  # Only Alphas as starting character
    hexnumber = ("0x" + Word(hexnums)).setParseAction(lambda t : int("".join(t),16))
    decnumber = (Optional("-") + Word(nums)).setParseAction(lambda t : int("".join(t)))
    number = hexnumber ^ decnumber
    boolean = (Keyword("TRUE") | Keyword("FALSE")).setParseAction(lambda t : True if t[0] == "TRUE" else False)
    oilstring = QuotedString('"')

    description = Optional(Suppress(":") + oilstring)
    semi = Suppress(";")
    ob = Suppress("{")
    cb = Suppress("}")

    oobject = Keyword("OS") ^ Keyword("TASK") ^ Keyword("COUNTER") ^ Keyword("ALARM")  \
        ^ Keyword("RESOURCE") ^ Keyword("EVENT") ^ Keyword("ISR") ^ Keyword("MESSAGE") \
        ^ Keyword("COM") ^ Keyword("NM") ^ Keyword("APPMODE") ^ Keyword("IPDU") \
        ^ Keyword("CHECKEDOBJECT") ^ Keyword("TASKGROUP")
    object_name = Group(oobject + name)  # e.g., OS myOs, COUNTER mycounter

    attribute_name = name ^ oobject
    attribute_value = boolean ^ name ^ oilstring ^ number #  longest match wins 'TRUEtask' wins against 'TRUE'
    parameter_list = Forward()  # Forward declaration...
    parameter_decl = attribute_name + Suppress("=") + attribute_value
    parameter = Group(parameter_decl + description("parameter_description")
                      + Optional(ob + parameter_list + cb) + semi)

    parameter_list << (ZeroOrMore(parameter))

    object_definiton = object_name + description + semi ^ object_name + ob \
        + Group(Optional(parameter_list)) + cb + description + semi

    object_definiton_list = ZeroOrMore(Group(object_definiton))

    oil_def = Group("CPU" + name("cpu_name")) + ob + object_definiton_list("cpu_objects") \
        + cb + description + semi

    singleLineComment = "//" + restOfLine
    oil_def.ignore(singleLineComment)  # Ignore // comments until end of line
    oil_def.ignore(cStyleComment)  # Ignore /* */ comments


    def __init__(self, oilfile):
        self.oil = self.oil_def.parseFile(oilfile)
        print("evaluating: " + oilfile)
        self.refined = self.refine(self.oil)

    def refine(self, oil):
        ''' Read out parsed oil file '''
        cpu = CPU()
        os = OS()
        tasks = dict()
        appmodes = dict()
        resources = dict()
        counters = dict()
        alarms = dict()
        events = dict()
        isrs = dict()
        checked_objects = dict()
        groups = dict()
        #  Read out CPU
        for x in oil:
            if x[0] == "CPU":
                cpu.evaluate(x)
            elif x[0][0] == "OS":
                os.evaluate(x)
            elif x[0][0] == "TASK":
                task = Task()
                task.evaluate(x)
                tasks[task.name] = task
            elif x[0][0] == "APPMODE":
                appmode = AppMode(x[0][1])
                appmodes[appmode.name] = appmode
            elif x[0][0] == "RESOURCE":
                resource = Resource()
                resource.evaluate(x)
                resources[resource.name] = resource
            elif x[0][0] == "COUNTER":
                counter = Counter()
                counter.evaluate(x)
                counters[counter.name] = counter
            elif x[0][0] == "ALARM":
                alarm = Alarm()
                alarm.evaluate(x)
                alarms[alarm.name] = alarm
            elif x[0][0] == "EVENT":
                event = Event()
                event.evaluate(x)
                events[event.name] = event
            elif x[0][0] == "ISR":
                isr = ISR()
                isr.evaluate(x)
                isrs[isr.name] = isr
            elif x[0][0] == "CHECKEDOBJECT":
                obj = CheckedObject()
                obj.evaluate(x)
                checked_objects[obj.name] = obj
            elif x[0][0] == "TASKGROUP":
                group = TaskGroup()
                group.evaluate(x)
                groups[group.name] = group

        cpu.os = os
        cpu.tasks = tasks
        cpu.appmodes = appmodes
        cpu.resources = resources
        cpu.counters = counters
        cpu.alarms = alarms
        cpu.events = events
        cpu.isrs = isrs
        cpu.checked_objects = checked_objects
        cpu.task_groups = groups

        cpu.interconnect()
        return cpu

    def getOS(self):
        return self.refined.os

    def getTasks(self):
        return self.refined.tasks.values()

    def getCounters(self):
        return self.refined.counters.values()

    def getAlarms(self):
        return self.refined.alarms.values()

    def getResources(self):
        return self.refined.resources.values()

    def getISRs(self):
        return self.refined.isrs.values()

    def getCheckedObjects(self):
        return self.refined.checked_objects.values()

    def getTaskGroups(self):
        return self.refined.task_groups.values()

    def getEvents(self):
        return self.refined.events.values()


    def __str__(self):
        return str(self.refined)

if __name__ == "__main__":
    oil = OILSystemDescription('test/example.oil')
    print(oil)
