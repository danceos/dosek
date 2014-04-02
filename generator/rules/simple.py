from generator.elements import *
from generator.rules.base import BaseRules
from collections import namedtuple

class SimpleSystem(BaseRules):
    def __init__(self):
        BaseRules.__init__(self)


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

    def systemcall(self, systemcall, function):
        """Generate systemcall into function"""
        raise NotImplementedError()

    def generate_dataobjects(self):
        """Generate all dataobjects for the system"""
        self.generate_dataobjects_task_descriptors()
        self.generate_dataobjects_counters_and_alarms()

        # Give the passes the chance to generate dataobjects
        self.callback_in_valid_passes("generate_dataobjects")

    def generate_dataobjects_task_descriptors(self):
        self.generator.source_file.includes.add(Include("os/scheduler/task.h"))
        task_id = 1
        for subtask in self.system_graph.get_subtasks():
            # Ignore the Idle thread
            if not subtask.is_real_thread():
                continue
            initializer = "(%d, %d, %s, arch::%s)" % (
                task_id,
                subtask.static_priority,
                str(subtask.preemptable).lower(),
                self.objects[subtask]["tcb_descriptor"].name
            )


            task_id += 1
            desc = DataObject("const os::scheduler::Task", "OS_" + subtask.name + "_task",
                              initializer)
            desc.allocation_prefix = "constexpr "
            self.generator.source_file.data_manager.add(desc, namespace = ("os", "tasks"))

            self.objects[subtask].update({"task_descriptor": desc, "task_id": task_id - 1})

    def generate_counter(self, counter_info):
        return DataObject("UnencodedCounter",
                             "OS_%s_counter" % (counter_info.name),
                             "(%d, %d, %d)" % (counter_info.maxallowedvalue,
                                               counter_info.ticksperbase,
                                               counter_info.mincycle))

    def generate_alarm(self, alarm_info, counter, task):
        return DataObject("UnencodedAlarm",
                           "OS_%s_alarm" %( alarm_info.name),
                           "(%s, %s, %s, %d, %d)" % (counter, task,
                                                     str(alarm_info.initial_armed).lower(),
                                                     alarm_info.initial_reltime,
                                                     alarm_info.initial_cycletime))

    def generate_dataobjects_counters_and_alarms(self):
        self.objects["counter"] = {}
        self.objects["alarm"] = {}
        for counter_info in self.generator.system_graph.counters:
            assert counter_info.maxallowedvalue < 2**16, "At the moment the maxallowedvalue has to fit into a 16 Bit Value"

            counter = self.generate_counter(counter_info)
            self.generator.source_file.data_manager.add(counter, namespace = ("os",))
            self.objects["counter"][counter_info.name] = counter

        for alarm_info in self.generator.system_graph.alarms:
            counter = self.objects["counter"][alarm_info.counter].name
            subtask = alarm_info.subtask
            task = "os::tasks::" + self.objects[subtask]["task_descriptor"].name
            alarm = self.generate_alarm(alarm_info, counter, task)
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

            # In the pre idle hook, we place the kickoff method of the
            # idle subtask
            if hook == "PreIdleHook":
                self.call_function(hook_function, 
                                   self.system_graph.idle_subtask.entry_abb\
                                   .generated_function_name(),
                                   "void", [])


            user_defined = "__OS_HOOK_DEFINED_" + hook
            if user_defined in self.system_graph.functions:
                self.call_function(hook_function, user_defined, "void", [])


class SimpleArch(BaseRules):
    def __init__(self):
        BaseRules.__init__(self)

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
            self.generator.source_file.data_manager.add(stackptr, namespace = ("arch",))

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

    KernelSpace = namedtuple("KernelSpace", ["pre_hook", "system", "post_hook"])
    def generate_kernelspace(self, userspace, abb, arguments):
        """returns a KernelSpace object"""
        raise NotImplementedError()

    def asm_marker(self, block, label):
        self.call_function(block, "asm_label", "void",
                           ['"%s"' % label])

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
        for counter in self.system_graph.counters:
            ret += self.expand_snippet("increase_counter",
                                       name = self.objects["counter"][counter.name].name)
        return ret

    def trigger_alarms(self, snippet, args):
        ret = []
        for alarm in self.system_graph.alarms:
            callback_name = "OSEKOS_ALARMCB_%s" % (alarm.name)
            has_callback  = (callback_name in self.system_graph.functions)
            args = {"counter": self.objects["counter"][alarm.counter].name,
                    "alarm":   self.objects["alarm"][alarm.name].name}
            ret += self.expand_snippet("if_alarm", **args) + "\n"
            # This alarm has an callback
            if has_callback:
                # Add a Declaration
                decl = FunctionDeclaration(callback_name, "void", [], extern_c = True)
                self.generator.source_file.function_manager.add(decl)
                ret += self.expand_snippet("alarm_alarmcallback", callback = callback_name) + "\n"
            ret += "    " + alarm.carried_syscall.generated_function_name() + "(0);\n"
            ret += self.expand_snippet("endif_alarm", **args) + "\n"


        return ret


