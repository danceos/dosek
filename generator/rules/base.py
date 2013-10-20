#!/usr/bin/python

RULE_PRIO_BASE = 0
RULE_PRIO_SYSTEM = 1000
from generator.atoms import *
from generator.primitives import *

from generator.tools import new_variable_name
from generator.types import void
import pprint

class Rule:
    def __init__(self, prio = RULE_PRIO_BASE):
        self.prio = RULE_PRIO_BASE

    def matches(self, seq, idx):
        return False

    def replace(self, seq, idx):
        return seq

    def replace_with(self, seq, idx, by):
        if type(by) != list:
            by = [by]
        # Add comments before and after the replacement to indicate
        # which rule has worked here
        by = [{'token': Comment, 'text': "START [" + self.__class__.__name__ + "]\n" + pprint.pformat(seq[idx])}] \
             + by \
             +[{'token': Comment, 'text': "END [" + self.__class__.__name__ + "]"}]
        seq = seq[:idx] + by + seq[1+idx:]
        return seq


class SystemCallsToFunctionCalls(Rule):
    def __init__(self):
        Rule.__init__(self, RULE_PRIO_BASE)

    def matches(self, seq, idx):
        return seq[idx]['token'] == SystemCall

    def replace(self, seq, idx):
        var = new_variable_name()
        repl = [{'token': FunctionCall,
                 'name': seq[idx]['syscall'],
                 'rettype': seq[idx]['rettype'],
                 'arguments': seq[idx]['arguments'],
                 'return_variable': var
             }]
        if seq[idx]['rettype'] != void:
            repl += [{'token': Statement,
                      'statement': 'return %s' % var
                  }]
        return self.replace_with(seq, idx, repl)


def base_rules():
    return [
        SystemCallsToFunctionCalls()
    ]
