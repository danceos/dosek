from generator.rules.simple import SimpleArch
from generator.elements import CodeTemplate, FunctionDefinitionBlock, \
    Include, FunctionDeclaration, Comment, Function, DataObject, \
    DataObjectArray, Hook, Block, VariableDefinition, Statement
from generator.graph.Subtask import Subtask

class ARMArch(SimpleArch):
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
        super(ARMArch, self).generate_dataobjects_task_stacks()

        stackptr_arr = DataObjectArray("void * const", "OS_stackptrs", "")
        stackptr_arr.add_static_initializer("&startup_sp")
        for subtask in self.system_graph.real_subtasks:
            stackptr_arr.add_static_initializer("&" + subtask.impl.stackptr.name)
        self.generator.source_file.data_manager.add(stackptr_arr, namespace = ("arch",))



    def generate_dataobjects_tcbs(self):
        self.generator.source_file.includes.add(Include("tcb.h"))

        tcb_arr = DataObjectArray("const TCB * const", "OS_tcbs", "")
        tcb_arr.add_static_initializer("0")

        for subtask in self.system_graph.subtasks:
            # Ignore the Idle thread
            if not subtask.is_real_thread():
                continue
            initializer = "(&%s, %s, %s, %s)" % (
                subtask.impl.entry_function.name,
                subtask.impl.stack.name,
                subtask.impl.stackptr.name,
                subtask.impl.stacksize
            )

            desc = DataObject("const arch::TCB", "OS_" + subtask.name + "_tcb",
                              initializer)
            desc.allocation_prefix = "constexpr "
            self.generator.source_file.data_manager.add(desc, namespace = ("arch",))
            subtask.impl.tcb_descriptor = desc
            tcb_arr.add_static_initializer("&" + desc.name)

        self.generator.source_file.data_manager.add(tcb_arr, namespace = ("arch",))

    def generate_isr_table(self, isrs):
        self.generator.source_file.includes.add(Include("machine.h"))
        self.generator.source_file.includes.add(Include("gic.h"))

        installed_irq_handlers = {0,      # Dispatch
                                  1,      # Reschedule
                                  29,     # Alarm
                              }
        for isr in isrs:
            irq_number = self.generate_isr(isr)
            installed_irq_handlers.add(irq_number)

        # Generate the ISR table
        irq_handler_arr = DataObjectArray("arch::irq_handler_t const", "irq_handlers", "",
                                          extern_c = True)
        self.generator.source_file.data_manager.add(irq_handler_arr)
        assert max(installed_irq_handlers)+1 < 96
        for irq in range(0, 96): # 96 should be enough for everyone
            if irq in installed_irq_handlers:
                irq_handler_arr.add_static_initializer("irq_handler_%d" % irq)
            else:
                irq_handler_arr.add_static_initializer("irq_handler_unhandled")


    def generate_isr(self, isr):
        self.generator.source_file.includes.add(Include("machine.h"))
        self.generator.source_file.includes.add(Include("gic.h"))
        isr_desc = self.generator.system_graph.find(Subtask, isr.name)
        irq_number = isr_desc.conf.isr_device
        handler = FunctionDefinitionBlock('ISR', [str(irq_number)])
        self.generator.source_file.function_manager.add(handler)

        # Forward declaration for the user defined function
        forward = FunctionDeclaration(isr.function_name, "void", [], extern_c=True)
        self.generator.source_file.function_manager.add(forward)

        # Forward declaration for our handler
        forward = FunctionDeclaration("irq_handler_%d" %(irq_number),
                                      "void*", ["void*", "uint32_t"], extern_c=True)
        self.generator.source_file.function_manager.add(forward)

        # Call the user defined function
        self.call_function(handler, isr.function_name, "void", [])

        prio = "IRQ_PRIO_LOCAL_TIMER"

        # Call give the IRQ a priority at startuo, and enable it
        self.call_function(self.system_graph.impl.StartOS,
                           "arch::GIC::enable_irq",
                           "void", [str(irq_number)],
                           prepend = True)
        self.call_function(self.system_graph.impl.StartOS,
                           "arch::GIC::set_irq_priority",
                           "void", [str(irq_number), prio],
                           prepend = True)

        return irq_number

    def generate_kernelspace(self, userspace, abb, arguments):
        """When a systemcall is done from a app (synchronous syscall), then we
           disable interrupts. In the interrupt handler they are already
           disabled.
        """
        pre_hook  = Hook("SystemEnterHook")
        post_hook = Hook("SystemLeaveHook", userspace.arguments())

        userspace.attributes.append("inlinehint")

        if abb.subtask.conf.is_isr:
            userspace.add(Comment("Called from ISR, no disable interrupts required!"))

            system    = Block(arguments = [(arg.name, arg.datatype) for arg in arguments])

            userspace.add(pre_hook)
            userspace.add(system)
            userspace.add(post_hook)

            return self.KernelSpace(pre_hook, system, post_hook)

        # Generate a function, that will be executed in system mode,
        # but is specific for this systemcall
        syscall = Function("__OS_syscall_" + userspace.function_name,
                           "void", [arg.datatype for arg in arguments], extern_c = True)

        self.generator.source_file.function_manager.add(syscall)
        # Mention the generated function in the stats
        self.stats.add_data(abb, "generated-function", syscall.name)
        # The syscall function is called from the function that will
        # be inlined into the application
        self.asm_marker(userspace, "syscall_start_%s" % userspace.name)

        syscall.add(pre_hook)
        self.call_function(userspace, "syscall", "void", [syscall.function_name] + [str(arg.name) for arg in arguments])
        userspace.add(post_hook)

        self.call_function(userspace, "Machine::enable_interrupts", "void", [])
        self.call_function(userspace, "Machine::switch_mode",
                           "void", ["Machine::USER"])

        self.asm_marker(userspace, "syscall_end_%s" % userspace.name)

        return self.KernelSpace(pre_hook, syscall, post_hook)

    def get_syscall_argument(self, block, i):
        # directly pass on the arguments, should be in register in ARM anyway.
        argument = block.arguments()[i]
        var = VariableDefinition(argument[1], argument[0])
        return var

    def kickoff(self, block, abb):
        self.call_function(block, "Machine::enable_interrupts",
                           "void", [])
        self.call_function(block, "Machine::switch_mode",
                           "void", ["Machine::USER"])

    def enable_irq(self, block):
        self.call_function(block,
                           "arch::GIC::set_task_prio",
                           "void", ["IRQ_PRIO_LOWEST"])

    def disable_irq(self, block):
        self.call_function(block,
                           "arch::GIC::set_task_prio",
                           "void", ["0"])


class LinkerScriptTemplate(CodeTemplate):
    def __init__(self, ARM):
        CodeTemplate.__init__(self, ARM.generator, "arch/arm/linker.ld.in")
        self.ARM = ARM
        self.system_graph    = self.ARM.system_graph
        # Reference to the objects object of our rule system
        self.objects = self.ARM.objects
        # Link the foreach_subtask method from the rules
        self.foreach_subtask = self.ARM.foreach_subtask

    def __select_statement(self, symbol, sections, library="*"):
        """Returns a newline seperated string of linker selectiors, for the
        corresponding sections"""
        ret = ""
        for sec in sections:
            ret += 'KEEP(%s(".%s.%s"));\n' %(library, sec, symbol)
        return ret

    def task_code_regions(self, snippet, args):
        def do(subtask):
            ret = ". = ALIGN(4096);\n"
            ret += "_stext_task%s = .;\n" % subtask.impl.task_id
            # Find all functions that belong to the function
            for function in self.system_graph.functions:
                if subtask == function.subtask:
                    ret += self.__select_statement(function.function_name, ["text", "rodata"])
            for function in subtask.impl.generated_functions:
                ret += self.__select_statement(function.function_name, ["text", "rodata"])

            ret += "_etext_task%s = .;\n" % subtask.impl.task_id
            ret += "\n"
            return ret

        return self.foreach_subtask(do)

    def task_stacks(self, snippet, args):
        def do(subtask):
            ret = ". = ALIGN(4096);\n"
            ret += "_sstack_task%s = .;\n" % subtask.impl.task_id
            ret += self.__select_statement(subtask.impl.stack.name, ["data"])
            ret += "_estack_task%s = .;\n" % subtask.impl.task_id
            ret += "\n"
            return ret

        return self.foreach_subtask(do)

    def task_data(self, snippet, args):
        def do(subtask):
            ret = ". = ALIGN(4096);\n"
            ret += "_sdata_task%s = .;\n" % subtask.impl.task_id
            ret += self.__select_statement(subtask.name + "*", ["data"])
            ret += "_edata_task%s = .;\n" % subtask.impl.task_id
            ret += "\n"
            return ret

        return self.foreach_subtask(do)

