#!/usr/bin/python

RULE_PRIO_BASE = 0
RULE_PRIO_SYSTEM = 1000
from generator.atoms import *
from generator.primitives import *
from generator.rules.operations import *
from generator.Generator import Generator
import pprint

class Rule:
    def __init__(self, prio = RULE_PRIO_BASE):
        self.prio = RULE_PRIO_BASE

    def matches(self, generator, seq, idx):
        return False

    def replace(self, generator, seq, idx):
        return seq

    def replace_with(self, seq, idx, by):
        if type(by) != list:
            by = [by]
        if Generator.is_rule_traced(self):
            # Add comments before and after the replacement to indicate
            # which rule has worked here
            by = [Comment.atom("START [" + self.__class__.__name__ + "]\n" + pprint.pformat(seq[idx]))]\
                 + by \
                 + [Comment.atom("END [" + self.__class__.__name__ + "]")]
        seq = seq[:idx] + by + seq[1+idx:]
        return seq


class SystemCallsToFunctionCalls(Rule):
    """This rule mapps all function calls to common variant of a function call.
       It generates a variable if nessecary for the return value.
    """
    def __init__(self):
        Rule.__init__(self, RULE_PRIO_BASE)

    def matches(self, generator, seq, idx):
        return SystemCall.isa(seq[idx])

    def replace(self, generator, seq, idx):
        # The Systemcall
        #systemcall = generator.analysis.find_syscall(seq[idx]['abb'])
        #thread = generator.system_description.getTask(systemcall.calling_subtask())

        repl = [
            atom_kout(generator, stringify(seq[idx]['syscall']), "endl"),
            #Comment.atom("Called by %s at prio %d", thread.getName(), thread.getStaticPriority()),
            FunctionCall.atom(seq[idx]["syscall"], seq[idx]["arguments"], seq[idx]["return_variable"])
        ]
        return self.replace_with(seq, idx, repl)


def base_rules():
    return [
        SystemCallsToFunctionCalls()
    ]
