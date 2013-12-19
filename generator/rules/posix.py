#!/usr/bin/python

from base import *
from generator.atoms import *
from generator.primitives import *



class ReplaceShutdownByExit(Rule):
    def __init__(self):
        Rule.__init__(self, RULE_PRIO_SYSTEM)

    def matches(self, generator, seq, idx):
        if SystemCall.isa(seq[idx]):
            return seq[idx]['syscall'] == "OSEKOS_ShutdownOS"
    def replace(self, generator, seq, idx):
        #include "<stdlib.h>
        generator.source_file.includes.add(Include("stdlib.h", system_include=True))

        newtoken = {'__token': FunctionCall,
                    'name': 'exit',
                    'arguments': seq[idx]['arguments']}
        return self.replace_with(seq, idx, newtoken)

def posix_rules():
    return [
        ReplaceShutdownByExit()
    ]
