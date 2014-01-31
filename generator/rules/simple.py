#!/usr/bin/python

from generator.tools import stringify
from generator.elements import *
from generator.rules.base import BaseRules

class SimpleSystem(BaseRules):
    def __init__(self):
        BaseRules.__init__(self)

    def call_function(self, block, function, rettype, arguments):
        """Generates a call to a function and stores the result in an
           variable, if it isn't void"""
        ret_var = VariableDefinition.new(self.generator, rettype)
        if ret_var:
            block.add(ret_var)
            name = ret_var.name
        else:
            name = None
        call    = block.add( FunctionCall(function, arguments, name))
        return ret_var

    def return_statement(self, block, expression):
        block.add(Statement("return %s" % expression))

    def object_COM(self, interface="COM1"):
        """Returns a variable name to a serial output driver, which can be used for
        debug printing"""
        varname = self.generator.variable_name_for_singleton("Serial", interface)
        serial = DataObject("Serial", varname, "Serial(Serial::%s)" % interface)
        self.generator.source_file.data_manager.add(serial, namespace=("os", "data"))
        self.generator.source_file.includes.add(Include("serial.h"))
        return varname

    def kout(self, block, *expressions):
        """Generates a print statement to a serial console"""
        com = self.object_COM()
        block.add( Statement("%s << %s" % (com, " << ".join(expressions))))

    def system_enter_hook(self, function):
        hook = Hook("SystemEnterHook")
        function.add(hook)
        return hook

    def system_leave_hook(self, function):
        hook = Hook("SystemLeaveHook")
        function.add(hook)
        return hook

    def systemcall(self, systemcall, function):
        """Generate systemcall into function"""
        self.system_enter_hook(function)

        ret_var = self.call_function(function,
                                     "OSEKOS_" + systemcall.function,
                                     systemcall.rettype,
                                     [x[0] for x in systemcall.arguments])

        self.kout(function, stringify(systemcall.function + "was called\n"))
        self.system_leave_hook(function)

        if ret_var:
            self.return_statement(function, ret_var.name)

    def StartOS(self, block):
        pass

    def generate_dataobjects(self):
        """Generate all dataobjects for the system"""
        self.generate_dataobjects_task_stacks()
        self.generate_dataobjects_task_entries()
        self.generate_dataobjects_task_descriptors()
        self.generate_dataobjects_counters_and_alarms()

    def generate_dataobjects_task_stacks(self):
        """Generate the stacks for the tasks, including the task pointers"""
        for subtask in self.system_graph.get_subtasks():
            # Ignore the Idle thread and ISR subtasks
            if not subtask.is_real_thread():
                continue
            stacksize = subtask.get_stack_size()
            stack = DataObjectArray("uint8_t", subtask.name + "_stack", stacksize,
                                    extern_c = True)
            self.generator.source_file.data_manager.add(stack)

            stackptr = DataObject("void *", "OS_" + subtask.name + "_stackptr")
            self.generator.source_file.data_manager.add(stackptr, namespace = ("os", "scheduler"))

            self.objects[subtask]["stack"] = stack
            self.objects[subtask]["stackptr"] = stackptr
            self.objects[subtask]["stacksize"] = stacksize


    def generate_dataobjects_task_entries(self):
        for subtask in self.system_graph.get_subtasks():
            # Ignore the Idle thread
            if not subtask.is_real_thread():
                continue
            entry_function = FunctionDeclaration(subtask.function_name, "void", [],
                                                                 extern_c = True)
            self.generator.source_file.function_manager.add(entry_function)
            self.objects[subtask]["entry_function"] = entry_function

    def generate_dataobjects_task_descriptors(self):

        self.generator.source_file.includes.add(Include("os/scheduler/task.h"))
        task_id = 1
        for subtask in self.system_graph.get_subtasks():
            # Ignore the Idle thread
            if not subtask.is_real_thread():
                continue
            initializer = "(%d, %d, %s, &%s, %s, %s)" % (
                task_id,
                subtask.static_priority,
                self.objects[subtask]["entry_function"].name,
                self.objects[subtask]["stack"].name,
                self.objects[subtask]["stackptr"].name,
                self.objects[subtask]["stacksize"]
            )


            task_id += 1
            desc = DataObject("const os::scheduler::Task", "OS_" + subtask.name + "_task",
                              initializer)
            desc.allocation_prefix = "constexpr "
            self.generator.source_file.data_manager.add(desc, namespace = ("os", "tasks"))

            self.objects[subtask].update({"task_descriptor": desc, "task_id": task_id - 1})

    def generate_dataobjects_counters_and_alarms(self):
        self.objects["counter"] = {}
        self.objects["alarm"] = {}
        for counter_info in self.generator.system_description.getHardwareCounters():
            counter = DataObject("Counter", "OS_%s_counter" %( counter_info.name),
                                 "(%d, %d, %d)" % (counter_info.maxallowedvalue,
                                                   counter_info.ticksperbase,
                                                   counter_info.mincycle))
            self.generator.source_file.data_manager.add(counter, namespace = ("os",))
            self.objects["counter"][counter_info.name] = counter

        for alarm_info in self.generator.system_description.getAlarms():
            counter = self.objects["counter"][alarm_info.counter].name
            subtask = self.system_graph.get_subtask(alarm_info.task)
            task = "os::tasks::" + self.objects[subtask]["task_descriptor"].name
            alarm = DataObject("Alarm", "OS_%s_alarm" %( alarm_info.name),
                               "(%s, %s, %s, %d, %d)" % (counter, task,
                                                         str(alarm_info.armed).lower(),
                                                         alarm_info.cycletime,
                                                         alarm_info.reltime))
            self.generator.source_file.data_manager.add(alarm, namespace = ("os",))
            self.objects["alarm"][alarm_info.name] = alarm

    def generate_system_code(self):
        self.generator.source_file.includes.add(Include("os/alarm.h"))
        alarms = AlarmTemplate(self)
        self.generator.source_file.declarations.append(alarms.expand())


    def generate_hooks(self):
        hooks = ["PreIdleHook"]
        for hook in hooks:
            hook_function = Function("__OS_HOOK_" + hook, "void", [])
            self.generator.source_file.function_manager.add(hook_function)

            user_defined = "__OS_HOOK_DEFINED_" + hook
            if user_defined in self.system_graph.functions:
                self.call_function(hook_function, user_defined, "void", [])




class AlarmTemplate(CodeTemplate):
    def __init__(self, rules):
        CodeTemplate.__init__(self, rules.generator, "os/alarm.h.in")
        self.rules = rules
        self.system_graph = self.generator.system_graph
        # Reference to the objects object of our rule system
        self.objects = self.rules.objects

        # Link the foreach_subtask method from the rules
        self.foreach_subtask = self.rules.foreach_subtask

    def increase_and_check_counters(self, snippet, args):
        ret = []
        for counter in self.system_graph.system.getHardwareCounters():
            ret += self.expand_snippet("increase_counter",
                                       name = self.objects["counter"][counter.name].name)
        return ret

    def trigger_alarms(self, snippet, args):
        ret = []
        for alarm in self.system_graph.system.getAlarms():
            ret += self.expand_snippet("alarm_to_task",
                                       counter = self.objects["counter"][alarm.counter].name,
                                       alarm = self.objects["alarm"][alarm.name].name)
        return ret


