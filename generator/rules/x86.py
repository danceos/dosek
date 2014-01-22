from generator.rules.base import BaseRules
from generator.rules.simple import SimpleArch
from generator.elements import CodeTemplate, FunctionDefinitionBlock, \
    Include, FunctionDeclaration, Comment, Function, DataObject, \
    DataObjectArray

class X86Arch(SimpleArch):
    def __init__(self):
        SimpleArch.__init__(self)

    def generate_linkerscript(self):
        linker_script = LinkerScriptTemplate(self)
        with self.generator.open_file("linker.ld") as fd:
            content = linker_script.expand()
            fd.write(content)

    def generate_dataobjects(self):
        """Generate all dataobjects for the system"""
        self.generate_dataobjects_task_stacks()
        self.generate_dataobjects_task_entries() # From SimpleArch
        self.generate_dataobjects_tcbs()

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



    def generate_dataobjects_tcbs(self):
        self.generator.source_file.includes.add(Include("tcb.h"))
        for subtask in self.system_graph.get_subtasks():
            # Ignore the Idle thread
            if not subtask.is_real_thread():
                continue
            initializer = "(&%s, %s, %s, %s)" % (
                self.objects[subtask]["entry_function"].name,
                self.objects[subtask]["stack"].name,
                self.objects[subtask]["stackptr"].name,
                self.objects[subtask]["stacksize"]
            )

            desc = DataObject("const arch::TCB", "OS_" + subtask.name + "_tcb",
                              initializer)
            desc.allocation_prefix = "constexpr "
            self.generator.source_file.data_manager.add(desc, namespace = ("arch",))
            self.objects[subtask].update({"tcb_descriptor": desc})


    def generate_isr(self, isr):
        self.generator.source_file.includes.add(Include("machine.h"))
        isr_desc = self.generator.system_description.getISR(isr.name)
        handler = FunctionDefinitionBlock('ISR', [str(isr_desc.device)])
        self.generator.source_file.function_manager.add(handler)

        # Forward declaration for the user defined function
        forward = FunctionDeclaration(isr.function_name, "void", [], extern_c=True)
        self.generator.source_file.function_manager.add(forward)

        # Call the user defined function
        self.call_function(handler, isr.function_name, "void", [])

        # Call the end of interrupt function
        self.call_function(handler, "LAPIC::send_eoi", "void", [])

    def syscall_block(self, function, subtask, argument):
        """When a systemcall is needed to execute code on kernel level, a new
           function is generated, and the new-functions block is
           returned. otherwise the argument is returned. This is
           useful for x86-bare, since an ActivateTask can be called
           directly from the ISR2, but must be invoked via an syscall
           form a TASK.

        """

        # System function can be executed directly in an isr
        if subtask.is_isr:
            function.add(Comment("Called from ISR, no syscall required!"))
            return function

        # Generate a function, that will be executed in system mode,
        # but is specific for this systemcall
        syscall = Function("__OS_syscall_" + function.function_name,
                           "void", ["int"], extern_c = True)
        syscall.unused_parameter(0)
        self.generator.source_file.function_manager.add(syscall)
        # The syscall function is called from the function that will
        # be inlined into the application
        self.call_function(function, "syscall", "void", [syscall.function_name, str(argument)])

        return syscall



class LinkerScriptTemplate(CodeTemplate):
    def __init__(self, x86):
        CodeTemplate.__init__(self, x86.generator, "arch/i386/linker.ld.in")
        self.x86 = x86
        self.system_graph    = self.x86.system_graph
        # Reference to the objects object of our rule system
        self.objects = self.x86.objects
        # Link the foreach_subtask method from the rules
        self.foreach_subtask = self.x86.foreach_subtask

        assert len(self.system_graph.get_subtasks()) <= 8, "paging.h does not support more tasks atm"

    def __select_statement(self, symbol, sections, library="*"):
        """Returns a newline seperated string of linker selectiors, for the
        corresponding sections"""
        ret = ""
        for sec in sections:
            ret += '%s(".%s.%s");\n' %(library, sec, symbol)
        return ret

    def task_code_regions(self, snippet, args):
        def do(subtask):
            ret = ". = ALIGN(4096);\n"
            ret += "_stext_task%s = .;\n" % self.objects[subtask]["task_id"]
            # Find all functions that belong to the function
            for function in self.system_graph.functions.values():
                if subtask == function.subtask:
                    ret += self.__select_statement(function.function_name, ["text", "rodata"])
            for function in self.objects[subtask]["generated_functions"]:
                ret += self.__select_statement(function.function_name, ["text", "rodata"])

            ret += "_etext_task%s = .;\n" % self.objects[subtask]["task_id"]
            ret += "\n"
            return ret

        return self.foreach_subtask(do)

    def task_stacks(self, snippet, args):
        def do(subtask):
            ret = ". = ALIGN(4096);\n"
            ret += "_sstack_task%s = .;\n" % self.objects[subtask]["task_id"]
            ret += self.__select_statement(self.objects[subtask]["stack"].name, ["data"])
            ret += "_estack_task%s = .;\n" % self.objects[subtask]["task_id"]
            ret += "\n"
            return ret

        return self.foreach_subtask(do)

    def task_data(self, snippet, args):
        def do(subtask):
            ret = ". = ALIGN(4096);\n"
            ret += "_sdata_task%s = .;\n" % self.objects[subtask]["task_id"]
            ret += self.__select_statement(subtask.name + "*", ["data"])
            ret += "_edata_task%s = .;\n" % self.objects[subtask]["task_id"]
            ret += "\n"
            return ret

        return self.foreach_subtask(do)

