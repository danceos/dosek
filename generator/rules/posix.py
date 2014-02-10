from generator.rules.base import BaseRules
from generator.elements import CodeTemplate, FunctionDefinitionBlock, \
    Include, FunctionDeclaration, Comment, Function, DataObject, \
    DataObjectArray, Block

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


    def generate_isr(self, isr):
        # Forward declaration for the user defined function
        self.generator.source_file.includes.add(Include("irq.h"))

        isr_desc = self.generator.system_description.getISR(isr.name)

        forward = FunctionDeclaration(isr.function_name, "void", ["int"], extern_c=True)
        self.generator.source_file.function_manager.add(forward)

        self.call_function(self.objects["StartOS"],
                           "arch::irq.enable", "void", [str(isr_desc.device)],
                           prepend = True)
        self.call_function(self.objects["StartOS"], 
                           "arch::irq.set_handler", "void", [str(isr_desc.device), isr.function_name],
                           prepend = True)





    def syscall_block(self, function, subtask, argument):
        """When a systemcall is done from a app (synchronous syscall), then we
           disable interrupts. In the interrupt handler they are already
           disabled.

        """

        # System function can be executed directly in an isr
        if subtask.is_isr:
            function.add(Comment("Called from ISR, no disable interrupts required!"))
            return function

        self.call_function(function, "Machine::disable_interrupts", "void", [])
        block = Block(arguments = [(argument, "void *")])
        function.add(block)
        self.call_function(function, "Machine::enable_interrupts", "void", [])

        return block
