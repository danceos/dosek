#!/usr/bin/python

"""
    @file 
    @ingroup primitives
    @brief Constructs the source file.
"""


from IncludeManager import IncludeManager
from DataObjectManager import DataObjectManager

import tools

class SourceFile:
    def __init__():
        self.includes = IncludeManager()
        self.data_manager = DataObjectManager()

    def source_elements(self):
        return self.includes.source_elements() \
            + self.data_manager.source_elements_declaration() \
            + self.data_manager.source_elements_allocation() \
            + self.data_manager.source_elements_initializer() \

    def generate(self, lang):
        # Get the source elements tree
        elements = self.source_elements()
        return tools.format_source_tree(elements, lang)
