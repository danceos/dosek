import sys
import logging
from inspect import getmembers, isfunction, isclass, ismethod
from collections import defaultdict

from generator.tools.enum import *
from generator.tools.typecheck import typecheck, iterable

def abstract():
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError(caller + ' must be implemented in subclass')

def format_source_tree(generator, tree):
    if type(tree) == str:
        return tree
    elif type(tree) == list:
        return "".join([format_source_tree(generator, x) for x in tree])
    else:
        if hasattr(tree, "expand"):
            return format_source_tree(generator, tree.expand(generator))
        else:
            return "".join(flatten(tree))

def flatten(seq : iterable):
    ret = []
    for i in seq:
        if type(i) == list:
            ret += flatten(i)
        else:
            ret += [i]
    return ret

def stringify(string):
    if type(string) == str:
        return '"%s"' % repr(string)[1:-1]
    return stringify(repr(string).replace('"', '\"'))


def panic(fmt : str, *args):
    logging.error(fmt, *args)
    sys.exit(-1)

def unwrap_seq(seq):
    assert len(seq) == 1
    return list(seq)[0]

def wrap_in_list(seq):
    if type(seq) == list:
        return seq
    return [seq]

class stack(list):
    def push(self, item):
        self.append(item)
    def isEmpty(self):
        return not self

def select_distinct(seq, field):
    ret = set()
    for item in seq:
        key = getattr(item, field)
        ret.add(key)
    return ret

def group_by(seq : iterable, field):
    ret = {}
    for item in seq:
        key = getattr(item, field)
        ret.setdefault(key, [])
        ret[key].append(item)
    return ret


def wrap_typecheck_functions(prefix = "generator",
                             ignore = "generator.tools.typecheck"):
    functions = set()
    fixup     = defaultdict(list)
    # Collect all possible functions
    for name, module in sys.modules.items():
        if name.startswith(prefix) or name == "__main__":
            for name, element in getmembers(module):
                # Plain functions
                if isfunction(element):
                    functions.add(element)
                    fixup[element].append((module, name))
                # Class methods
                if isclass(element):
                    for name_, method in getmembers(element):
                        if isfunction(method):
                            functions.add(method)
                            fixup[method].append((element, name_))


    for function in functions:
        if len(function.__annotations__) == 0:
            continue
        if function.__module__ == ignore:
            continue

        wrapped = typecheck(function)
        for obj, attrname in fixup[function]:
            setattr(obj, attrname, wrapped)
