#!/usr/bin/python

from base import *
from generator.atoms import *
from generator.primitives import *



class ReplaceShutdownByExit(Rule):
    def __init__(self):
        Rule.__init__(self, RULE_PRIO_SYSTEM)

    def matches(self, seq, idx):
        if seq[idx]['token'] == SystemCall:
            #FIXME
            return seq[idx]['syscall'] == "OSEKOS_TerminateTask"
    def replace(self, seq, idx):
        newtoken = {'token': Comment, 'text': "Hier war ein exit"}
        return self.replace_with(seq, idx, newtoken)

def posix_rules():
    return [
        ReplaceShutdownByExit()
    ]
