#!/usr/bin/python

import subprocess

class ObjectFile:
    UNDEFINED   = 'U'
    COMMON      = 'C'
    WEAK_REF    = 'W'
    LOCAL_TEXT  = 't'
    GLOBAL_TEXT = 'T'
    LOCAL_DATA  = 'd'
    GLOBAL_DATA = 'D'
    UNKOWN      = '?'

    """class to parse object files in order to get the symbol table"""
    def __init__(self, nm, obj):
        # The nm binary
        self.nm = nm
        self.obj = obj
        self.__symbol_table = None

    def get_symbol_table(self):
        if self.__symbol_table is None:
            self.update_symbol_table()
        return self.__symbol_table

    def update_symbol_table(self):
        out = subprocess.check_output([self.nm, "-P", self.obj])
        self.__symbol_table = dict()
        for line in out.split("\n"):
            line = line.split(" ")
            if len(line) < 2:
                continue
            self.__symbol_table[line[0]] = line[1]

    def get_undefined_symbols(self):
        table = self.get_symbol_table()
        return [x for x in table
                if table[x] == self.UNDEFINED]

