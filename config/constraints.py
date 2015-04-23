import os
from pyparsing import (Word, alphanums, alphas,
                       infixNotation, opAssoc, Keyword)
import fnmatch
import logging


def parse_constraint(string):
    class Expression:
        def __init__(self):
            pass

    class Option(Expression):
        def __init__(self, word):
            self.name = word[0]

        def path(self):
            return self.name.split(".")

        def evaluate(self, config):
            value, ty = config._.get(self.path())
            return value

        def __repr__(self):
            return ":%s" % self.name

    class Not:
        def __init__(self, inner):
            assert len(inner) == 1
            self.__inner = inner[0][1]

        def evaluate(self, config):
            return not self.__inner.evaluate(config)

        def __repr__(self):
            return "(! %s)" % self.__inner

    class Implies:
        def __init__(self, inner):
            assert len(inner) == 1
            self.__left = inner[0][0]
            self.__right = inner[0][2]

        def evaluate(self, config):
            if not self.__left.evaluate(config):
                return True
            return self.__right.evaluate(config)

        def __repr__(self):
            return "(%s -> %s)" % (self.__left, self.__right)

    class Equal:
        def __init__(self, inner):
            self.__option = inner[0][0]
            self.__value = inner[0][2].name

        def evaluate(self, config):
            value, ty = config._.get(self.__option.path())
            return value == ty.from_string(self.__value)


        def __repr__(self):
            return "(%s == %s)" % (self.__option, self.__value)

    class And:
        def __init__(self, args):
            self.__args = args[0][::2]

        def evaluate(self, config):
            return all([x.evaluate(config) for x in self.__args])

        def __repr__(self):
            return " && ".join([repr(x) for x in self.__args])

    class Or:
        def __init__(self, args):
            self.__args = args[0][::2]

        def evaluate(self, config):
            return any([x.evaluate(config) for x in self.__args])

        def __repr__(self):
            return " || ".join([repr(x) for x in self.__args])


    grammar = infixNotation( Word(alphanums+"._-").setParseAction(Option),
                              [
                                  ("==", 2, opAssoc.LEFT, Equal),
                                  ("!", 1,  opAssoc.RIGHT, Not),
                                  ("->", 2, opAssoc.LEFT, Implies),
                                  ("&&", 2, opAssoc.LEFT, And),
                                  ("||", 2, opAssoc.LEFT, Or),
                              ])

    #print(grammar.parseString("asd"))
    #print(grammar.parseString("!foo -> !bar"))
    #print(grammar.parseString("(!foo -> !bar) && foo && lala"))
    #print(grammar.parseString("os.specialize -> (os.systemcalls == normal)"))
    x = grammar.parseString(string)
    return x[0]

def grep_constraints(fn):
    if not os.path.exists(fn):
        return
    with open(fn, "rb") as fd:
        text = fd.read().decode('utf8', 'ignore')
        start = 0
        while True:
            # The plus is here to make it ungreppable
            idx = text.find("config-constraint" + "-:", start)
            if idx == -1:
                break

            ret = []
            while True:
                nl = text.find("\n", idx)
                if nl == -1:
                    nl = len(text)
                ret.append(text[idx:nl])
                # Get next line
                nl2 = text.find("\n", nl+1)
                if nl2 != -1:
                    next_line = text[nl:nl2]
                    if ":-:" in next_line:
                        idx = nl + 1
                    else:
                        break
            text_constraint = ""
            for x in ret:
                text_constraint += " " + x.split("-:", 1)[1].strip()
            text_constraint = text_constraint.strip()
            yield fn, idx, parse_constraint(text_constraint)
            start = idx + 1

def __find_constraints(pattern, basedir, ignore_patterns):
    if type(pattern) == list:
        for fn in pattern:
            for x in __find_constraints(fn, basedir, ignore_patterns):
                yield x
    else:
        for root, dirs, files in os.walk(os.path.abspath(basedir)):
            for i, value in reversed(list(enumerate(dirs))):
                for ignore_pattern in ignore_patterns:
                    if fnmatch.fnmatch(value, ignore_pattern):
                        del dirs[i]
                        break
            for i, value in reversed(list(enumerate(files))):
                for ignore_pattern in ignore_patterns:
                    if fnmatch.fnmatch(value, ignore_pattern):
                        del files[i]
                        break
            for fn in fnmatch.filter(files, pattern):
                for constraint in grep_constraints(os.path.join(root, fn)):
                    yield constraint

def find_constraints(pattern, basedir = ".", ignore_patterns = [".git", "*build*", "gem5"]):
    return list(__find_constraints(pattern, basedir, ignore_patterns))

def check_constraints(constraints, config, silent = False):
    # Is tree consistent?:
    # This will throw a runtime error if not.
    for _ in iter(config):
        pass
    for fn, char, constraint in constraints:
        if not constraint.evaluate(config):
            if not silent:
                logging.error("file = %s", fn)
                logging.error("constraint = %s", constraint)
            raise RuntimeError("Invalid configuration; constraint: %s" % (constraint))
        else:
            if not silent:
                logging.debug("constraint holds: %s", constraint)
