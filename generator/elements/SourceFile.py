#!/usr/bin/python

"""
    @file 
    @ingroup primitives
    @brief Constructs the source file.
"""


from generator.elements.IncludeManager import IncludeManager
from generator.elements.DataObjectManager import DataObjectManager
from generator.elements.FunctionManager import FunctionManager
from generator import tools

class SourceFile:
    def __init__(self):
        self.includes = IncludeManager()
        self.data_manager = DataObjectManager()
        self.function_manager = FunctionManager()

    def source_elements(self):
        return [self.includes.source_elements()] \
            + ["\n"] \
            + [self.function_manager.source_element_declarations()] \
            + [self.data_manager.source_element_declaration()] \
            + [self.data_manager.source_element_allocation()] \
            + [self.data_manager.source_element_initializer()] \
            + ["\n"] \
            + [self.function_manager.source_element_definitions()] \

    def expand(self, generator):
        # Get the source elements tree
        elements = self.source_elements()
        return tools.format_source_tree(generator, elements)
