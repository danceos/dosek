from generator.elements import *
from generator.elements.DataObjectManager import ExternalDataObject
from generator.rules.base import BaseRules
from generator.graph.Function import Function as GraphFunction
from .implementations import *
import logging

from collections import namedtuple

class SimpleSystem(BaseRules):
    def __init__(self):
        BaseRules.__init__(self)


    def return_statement(self, block, expression):
        block.add(Statement("return %s" % expression))

    def systemcall(self, systemcall, function):
        """Generate systemcall into function"""
        raise NotImplementedError()

    def generate_dataobjects(self):
        """Generate all dataobjects for the system"""
        self.generate_dataobjects_task_descriptors()
        self.generate_dataobjects_counters_and_alarms()
        self.generate_dataobjects_checkedObjects()
        self.generate_dataobjects_global_keso_ids()
        # Give the passes the chance to generate dataobjects
        self.callback_in_valid_passes("generate_dataobjects")

    def generate_dataobjects_global_keso_ids(self):
        for subtask in self.system_graph.real_subtasks:
            # add: const TaskType subtaskname_id = OS_subtask.name_task.id;
            iddesc = DataObject("const TaskType", "OSEKOS_TASK_" + subtask.conf.name,
                                static_initializer = str(subtask.impl.task_id),
                                extern_c = True)
            self.generator.source_file.data_manager.add(iddesc);

        for alarm in self.system_graph.alarms:
            iddesc = DataObject("const AlarmType", "OSEKOS_ALARM_" + alarm.conf.name,
                                static_initializer = str(alarm.impl.alarm_id),
                                extern_c = True)
            self.generator.source_file.data_manager.add(iddesc);

    def generate_dataobjects_task_descriptors(self):
        self.generator.source_file.includes.add(Include("os/scheduler/task.h"))
        self.system_graph.idle_subtask.impl.task_id = 0
        task_id = 1
        for subtask in self.system_graph.subtasks:
            # Ignore the Idle thread
            if not subtask.is_real_thread():
                continue
            initializer = "(%d, %d, %s, arch::%s)" % (
                task_id,
                subtask.conf.static_priority,
                str(subtask.conf.preemptable).lower(),
                subtask.impl.tcb_descriptor.name
            )

            desc = DataObject("const os::scheduler::Task", "OS_" + subtask.name + "_task",
                              initializer)
            desc.allocation_prefix = "constexpr "

            self.generator.source_file.data_manager.add(desc, namespace = ("os", "tasks"))
            subtask.impl.task_descriptor = desc
            subtask.impl.task_id = task_id

            task_id += 1


    def generate_counter(self, ctr):
        return DataObject("UnencodedCounter",
                             "OS_%s_counter" % (ctr.name),
                             "(%d, %d, %d)" % (ctr.conf.maxallowedvalue,
                                               ctr.conf.ticksperbase,
                                               ctr.conf.mincycle))

    def generate_alarm(self, alarm, counter, task):
        return DataObject("UnencodedAlarm<&%s>" % counter.impl.name,
                           "OS_%s_alarm" %( alarm.conf.name),
                           "(%s, %s, %d, %d, %d)" % (task,
                                                     str(alarm.conf.armed).lower(),
                                                     alarm.conf.reltime,
                                                     alarm.conf.cycletime,
                                                     alarm.impl.alarm_id,
                           ))

    def generate_dataobjects_counters_and_alarms(self):
        for ctr in self.generator.system_graph.counters:
            assert ctr.conf.maxallowedvalue < 2**16, "At the moment the maxallowedvalue has to fit into a 16 Bit Value"

            impl = self.generate_counter(ctr)

            # Add and save counter Implementation
            self.generator.source_file.data_manager.add(impl, namespace = ("os",))
            ctr.impl = impl

        alarm_id = 1
        for alarm in self.generator.system_graph.alarms:
            subtask = alarm.conf.subtask
            task = "os::tasks::" + subtask.impl.task_descriptor.name

            alarm.impl = AlarmImpl()
            alarm.impl.alarm_id = alarm_id
            alarm_id += 1

            impl = self.generate_alarm(alarm, alarm.conf.counter, task)

            # Add and save alarm implementation
            self.generator.source_file.data_manager.add(impl, namespace = ("os",))
            alarm.impl.name = impl.name
            alarm.impl.alarm_desc = impl

    def generate_system_code(self):
        pass

    def generate_hooks(self):
        hooks = [("PreIdleHook",[]),("FaultDetectedHook",["DetectedFault_t","uint32_t","uint32_t"]),
                 ("StartupHook", []), ("PreTaskHook", []), ("PostTaskHook", []),
                 ("ShutdownHook", ["StatusType"])]
        for hook,args in hooks:
            hook_function = Function("__OS_HOOK_" + hook, "void", args)
            self.generator.source_file.function_manager.add(hook_function)
            # Cast arguments to void, to get rid of unused parameter warning
            for i in range(0, len(args)):
                hook_function.unused_parameter(i);

            # In the pre idle hook, we place the kickoff method of the
            # idle subtask
            if hook == "PreIdleHook":
                self.call_function(hook_function, 
                                   self.system_graph.idle_subtask.entry_abb\
                                   .generated_function_name(),
                                   "void", [])


            user_defined = "__OS_HOOK_DEFINED_" + hook
            if self.system_graph.find(GraphFunction, user_defined):
                # Generate actual call, only if user had defined the hook function
                self.call_function(hook_function, user_defined, "void", hook_function.arguments_names())
                if hook == "PostTaskHook":
                    logging.warning("Be aware that PostTaskHooks are not properly implemented")

            if hook == "FaultDetectedHook":
                hook_function.add(Statement("debug << \"FaultDetectedHook \" << arg0<< endl"))
                self.call_function(hook_function, "ShutdownMachine",
                                   "void", [])
                self.call_function(hook_function, "Machine::unreachable",
                                   "void", [])


    def generate_dataobjects_checkedObjects(self):
        if len(list(self.system_graph.checkedObjects)) < 1:
            return
        self.generator.source_file.includes.add(Include("dependability/dependability_service.h"))
        self.generator.source_file.includes.add(Include("dependability/depsvc.h"))

        co_index = 0;
        initializator = "{\n"
        multiplexer_functions = []
        for co in self.system_graph.checkedObjects:
            if co.header is not None:
                self.generator.source_file.includes.add(Include(co.header))
            if co.typename is not None:
                self.generator.source_file.data_manager.add(ExternalDataObject(co.typename, co.name))
            initializator += "    { &" + co.name + ", sizeof(" + co.name + ") },\n"
            self.generator.source_file.data_manager.add(
                DataObject("const unsigned int", "OS_" + co.name + "_CheckedObject_Index", str(co_index)),
                namespace = ("dep",)
            )
            multiplexer_functions.append(co.checkfunc)
            co_index += 1
        initializator += "}"
        self.generator.source_file.data_manager.add(
            DataObject("const unsigned int", "OS_all_CheckedObjects_size", str(co_index)),
			namespace = ("dep",)
        )
        self.generator.source_file.data_manager.add(
            DataObject("Checked_Object", "OS_all_CheckedObjects[]", initializator),
			namespace = ("dep",)
        )
        # Create Function
        multiplexer = Function("OS_checkfunction_multiplexer", "unsigned int", ["unsigned int"])
        multiplexer.add("\tswitch(arg0) {\n")
        fun_index = -1
        for func in multiplexer_functions:
            fun_index += 1
            if func is None:
                continue
            multiplexer.add("\tcase " + str(fun_index) + ":\n")
            multiplexer.add("\t\treturn " + func + "();\n")
            self.generator.source_file.function_manager.add(FunctionDeclaration(func, "unsigned int", []))
        multiplexer.add("\tdefault:\n")
        multiplexer.add("\t\treturn crc32(OS_all_CheckedObjects[arg0].location, OS_all_CheckedObjects[arg0].size);\n")
        multiplexer.add("\t}\n")
        self.generator.source_file.function_manager.add(multiplexer, "dep")


class SimpleArch(BaseRules):
    def __init__(self):
        BaseRules.__init__(self)

    def generate_dataobjects_task_stacks(self):
        """Generate the stacks for the tasks, including the task pointers"""
        # Ignore the Idle thread and ISR subtasks
        for subtask in self.system_graph.real_subtasks:
            stacksize = subtask.get_stack_size()
            stack = DataObjectArray("uint8_t", subtask.name + "_stack", stacksize,
                                    extern_c = True)
            self.generator.source_file.data_manager.add(stack)

            stackptr = DataObject("void *", "OS_" + subtask.name + "_stackptr")
            self.generator.source_file.data_manager.add(stackptr, namespace = ("arch",))


            subtask.impl.stack = stack
            subtask.impl.stackptr = stackptr
            subtask.impl.stacksize = stacksize


    def generate_dataobjects_task_entries(self):
        for subtask in self.system_graph.subtasks:
            # Ignore the Idle thread
            if not subtask.is_real_thread():
                continue
            entry_function = FunctionDeclaration(subtask.function_name, "void", [],
                                                                 extern_c = True)
            self.generator.source_file.function_manager.add(entry_function)
            subtask.impl.entry_function = entry_function

    KernelSpace = namedtuple("KernelSpace", ["pre_hook", "system", "post_hook"])
    def generate_kernelspace(self, userspace, abb, arguments):
        """returns a KernelSpace object"""
        raise NotImplementedError()

    def asm_marker(self, block, label):
        self.call_function(block, "asm_label", "void",
                           ['"%s"' % label])

    def kickoff(self, abb, block):
        self.call_function(block, "Machine::enable_interrupts",
                           "void", [])

    def enable_irq(self, block):
        self.call_function(block,
                           "Machine::enable_interrupts",
                           "void", [])

    def disable_irq(self, block):
        self.call_function(block,
                           "Machine::disable_interrupts",
                           "void", [])
