from .arch_generic import GenericArch
from .elements import *
from generator.analysis.Subtask import Subtask


class PosixArch(GenericArch):
    def __init__(self):
        super(PosixArch, self).__init__()

    def generate_linkerscript(self):
        """Posix does not require a linker script"""
        with self.generator.open_file("linker.ld") as fd:
            fd.write("IGNORED IN POSIX")

    def generate_dataobjects(self):
        """Generate all dataobjects for the system"""
        self.generate_dataobjects_task_stacks() # From SimpleArch
        self.generate_dataobjects_task_entries() # From SimpleArch
        self.generate_dataobjects_tcbs()

    def generate_dataobjects_tcbs(self):
        self.generator.source_file.includes.add(Include("tcb.h"))
        for subtask in self.system_graph.real_subtasks:
            initializer = "(&%s, %s, %s, %s)" % (
                subtask.impl.entry_function.name,
                subtask.impl.stack.name,
                subtask.impl.stackptr.name,
                subtask.impl.stacksize,
            )

            tcb = DataObject("const arch::TCB", "OS_" + subtask.name + "_tcb",
                              initializer)
            tcb.allocation_prefix = "constexpr "
            self.generator.source_file.data_manager.add(tcb, namespace = ("arch",))
            subtask.impl.tcb_descriptor = tcb

    def generate_isr_table(self, isrs):
        self.generator.source_file.includes.add(Include("machine.h"))
        for isr in isrs:
            self.generate_isr(isr)

    def generate_isr(self, isr):
        # Forward declaration for the user defined function
        self.generator.source_file.includes.add(Include("irq.h"))

        isr_desc = self.generator.system_graph.get(Subtask, isr.name)

        handler = Function(isr_desc.function_name + "_wrapper", "void", ["int"])
        self.generator.source_file.function_manager.add(handler)

        # Call kickoff, user defined function, and iret system call
        kickoff, iret = isr.entry_abb, isr.exit_abb
        self.call_function(handler, kickoff.generated_function_name(), "void", [])
        self.call_function(handler, isr.function_name, "void", [])
        self.call_function(handler, iret.generated_function_name(), "void", [])


        forward = FunctionDeclaration(isr.function_name, "void", [], extern_c=True)
        self.generator.source_file.function_manager.add(forward)

        self.call_function(self.system_graph.impl.StartOS,
                           "arch::irq.enable", "void", [str(isr_desc.conf.isr_device)],
                           prepend = True)
        self.call_function(self.system_graph.impl.StartOS,
                           "arch::irq.set_handler", "void", [str(isr_desc.conf.isr_device),
                                                             handler.function_name],
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
        if abb.subtask.conf.is_isr:
            userspace.add(Comment("Called from ISR, no disable interrupts required!"))
        else:
            self.call_function(userspace, "Machine::disable_interrupts", "void", [])

        args = [(arg.name, arg.datatype) for arg in arguments]
        pre_hook  = Hook("SystemEnterHook",arguments =  args)
        system    = Block(arguments = args)
        post_hook = Hook("SystemLeaveHook", userspace.arguments())

        userspace.add(pre_hook)
        userspace.add(system)
        userspace.add(post_hook)

        if abb.subtask.conf.is_isr:
            userspace.add(Comment("Called from ISR, no enable interrupts required!"))
        else:
            self.call_function(userspace, "Machine::enable_interrupts", "void", [])

        return self.KernelSpace(pre_hook, system, post_hook)

    def get_syscall_argument(self, block, i):
        name, typename = block.arguments()[i]
        return VariableDefinition(typename, name)
