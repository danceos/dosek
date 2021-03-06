from .elements import *
from .base import BaseCoder
from generator.analysis.Function import Function as GraphFunction
from .implementations import *
import logging

from collections import namedtuple

class GenericArch(BaseCoder):
    def __init__(self):
        super(GenericArch, self).__init__()

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
