#!/usr/bin/python

"""
    @file 
    @ingroup primitives
    @brief Building include statements
"""
import unittest

from SourceElement import CPPStatement, Comment
import tools

class Include:
    def __init__(self, filename, system_include=False, comment = None):
        self.filename = filename
        self.system_include = system_include
        self.comment = comment

    def source_elements(self):
        sep = '""'
        if self.system_include:
            sep = "<>"
        arg = sep[0] + self.filename + sep[1]
        ret = []
        if self.comment:
            ret.append(Comment(self.comment))
        ret.append(CPPStatement("include", arg))
        return ret

class IncludeManager:
    def __init__(self):
        self.included_files = []

    def add(self, include):
        self.included_files.append(include)

    def source_elements(self):
        ret = []
        # Sort by local and global includes
        for include in self.included_files:
            ret.append(include.source_elements())
        return ret

class TestIncludeManager(unittest.TestCase):
    def test_global_local_includes(self):
        m = IncludeManager()
        m.add(Include("stdint.h", system_include = True))
        m.add(Include("cpu.h", comment = "The main CPU header"))
        m.add(Include("cpu_2.h", comment = "The secondary CPU header\nwith more comments"))


        text = tools.format_source_tree(m.source_elements())
        self.assertEqual(text, """#include <stdint.h>

// The main CPU header
#include "cpu.h"

/* The secondary CPU header
 * with more comments
 */
#include "cpu_2.h"
""")

if __name__ == '__main__':
    unittest.main()

