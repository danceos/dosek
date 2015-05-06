#!/usr/bin/python

"""
    @file
    @ingroup primitives
    @brief Building include statements
"""
from .SourceElement import CPPStatement, Comment

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
        # Filter out duplicate includes
        for inc in self.included_files:
            if inc.filename == include.filename and \
               inc.system_include == include.system_include:
                return
        self.included_files.append(include)

    def source_elements(self):
        ret = []
        # Sort by local and global includes
        for include in self.included_files:
            ret.append(include.source_elements())
        return ret

