from generator.elements import Include, FunctionDeclaration, Comment, \
                               DataObject, Block, Hook, VariableDefinition

from generator.rules.simple import SimpleArch


class PosixArch(SimpleArch):
    def __init__(self):
        SimpleArch.__init__(self)

    def generate_linkerscript(self):
        """Posix does not require a linker script"""
        pass

    def generate_dataobjects(self):
        """Generate all dataobjects for the system"""
        self.generate_dataobjects_task_stacks() # From SimpleArch
        self.generate_dataobjects_task_entries() # From SimpleArch
        self.generate_dataobjects_tcbs()

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

    def generate_isr_table(self, isrs):
        self.generator.source_file.includes.add(Include("machine.h"))
        for isr in isrs:
            self.generate_isr(isr)

    def generate_isr(self, isr):
        # Forward declaration for the user defined function
        self.generator.source_file.includes.add(Include("irq.h"))

        isr_desc = self.generator.system_graph.get_subtask(isr.name)

        forward = FunctionDeclaration(isr.function_name, "void", ["int"], extern_c=True)
        self.generator.source_file.function_manager.add(forward)

        self.call_function(self.objects["StartOS"],
                           "arch::irq.enable", "void", [str(isr_desc.isr_device)],
                           prepend = True)
        self.call_function(self.objects["StartOS"], 
                           "arch::irq.set_handler", "void", [str(isr_desc.isr_device), isr.function_name],
                           prepend = True)

    def generate_isr_table(self, isrs):
        self.generator.source_file.includes.add(Include("machine.h"))
        for isr in isrs:
            self.generate_isr(isr)

    def generate_kernelspace(self, userspace, abb, arguments):
        """When a systemcall is done from a app (synchroanous syscall), then we
           disable interrupts. In the interrupt handler they are already
           disabled.
        """
        if abb.function.subtask.is_isr:
            userspace.add(Comment("Called from ISR, no disable interrupts required!"))
        else:
            self.call_function(userspace, "Machine::disable_interrupts", "void", [])

        pre_hook  = Hook("SystemEnterHook")
        system    = Block(arguments = [(arg.name, arg.datatype) for arg in arguments])
        post_hook = Hook("SystemLeaveHook")

        userspace.add(pre_hook)
        userspace.add(system)
        userspace.add(post_hook)

        if abb.function.subtask.is_isr:
            userspace.add(Comment("Called from ISR, no enable interrupts required!"))
        else:
            self.call_function(userspace, "Machine::enable_interrupts", "void", [])

        return self.KernelSpace(pre_hook, system, post_hook)

    def get_syscall_argument(self, block, i):
        name, typename = block.arguments()[i]
        return VariableDefinition(typename, name)
