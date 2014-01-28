#!/usr/bin/python

from generator.tools import stringify, merge_dict_tree
from generator.elements import *

class BaseRules:
    def __init__(self):
        self.generator = None


    def set_generator(self, generator):
        self.generator = generator
        self.system_graph = generator.system_graph
        self.objects = {}
        for subtask in self.system_graph.get_subtasks():
            self.objects[subtask] = {}

    def call_function(self, block, function, rettype, arguments):
        """Generates a call to a function and stores the result in an
           variable, if it isn't void"""
        ret_var = block.add( VariableDefinition.new(self.generator, rettype))
        call    = block.add( FunctionCall(function, arguments, ret_var.name))
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
        stacks = self.generate_dataobjects_task_stacks()
        entries = self.generate_dataobjects_task_entries()
        tasks = self.generate_dataobjects_task_descriptors(stacks, entries)

        self.objects = merge_dict_tree(self.objects, entries, 1)
        self.objects = merge_dict_tree(self.objects, stacks, 1)
        self.objects = merge_dict_tree(self.objects, tasks, 1)
        

    def generate_dataobjects_task_stacks(self):
        """Generate the stacks for the tasks, including the task pointers"""
        objs = {}
        for subtask in self.system_graph.get_subtasks():
            # Ignore the Idle thread and ISR subtasks
            if not subtask.is_real_thread():
                continue
            stacksize = subtask.get_stack_size()
            stack = DataObjectArray("uint8_t", subtask.name + "_stack", stacksize,
                                    extern_c = True)
            self.generator.source_file.data_manager.add(stack)

            stackptr = DataObject("void *", "OS_" + subtask.name + "_stackptr",
                                  extern_c = True)
            self.generator.source_file.data_manager.add(stackptr)

            objs[subtask] = {"stack": stack, "stackptr": stackptr, 
                             "stacksize": stacksize}
        return objs

    def generate_dataobjects_task_entries(self):
        objs = {}
        for subtask in self.system_graph.get_subtasks():
            # Ignore the Idle thread
            if not subtask.is_real_thread():
                continue
            entry_function = FunctionDeclaration(subtask.function_name, "void", [],
                                                                 extern_c = True,
                                                                 attributes = ["weak_import"])
            self.generator.source_file.function_manager.add(entry_function)
            objs[subtask] = {'entry_function': entry_function}
        return objs

    def generate_dataobjects_task_descriptors(self, stacks, entries):
        objs = {}

        self.generator.source_file.includes.add(Include("os/scheduler/task.h"))
        task_id = 1
        for subtask in self.system_graph.get_subtasks():
            # Ignore the Idle thread
            if not subtask.is_real_thread():
                continue
            initializer = "(%d, %d, %s, &%s, %s, %s)" % (
                task_id,
                subtask.static_priority,
                entries[subtask]["entry_function"].name,
                stacks[subtask]["stack"].name,
                stacks[subtask]["stackptr"].name,
                stacks[subtask]["stacksize"]
            )


            task_id += 1
            desc = DataObject("const os::scheduler::Task", "OS_" + subtask.name + "_task",
                              initializer)
            desc.allocation_prefix = "constexpr "
            self.generator.source_file.data_manager.add(desc, namespace = ("os", "tasks"))

            objs[subtask] = {"task_descriptor": desc, "task_id": task_id - 1}
        return objs


    def generate_system_code(self):
        pass
