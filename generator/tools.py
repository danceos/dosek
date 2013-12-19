#!/usr/bin/python

"""
    @file
    @ingroup primitives
    @brief Santa's little helper.
"""

from itertools import chain

def abstract():
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError(caller + ' must be implemented in subclass')

def format_source_tree(generator, tree):
    if type(tree) == list:
        return "".join([format_source_tree(generator, x) for x in tree])
    else:
        if hasattr(tree, "expand"):
            return format_source_tree(generator, tree.expand(generator))
        else:
            return "".join(flatten(tree))


def flatten(seq):
    ret = []
    for i in seq:
        if type(i) == list:
            ret += flatten(i)
        else:
            ret += [i]
    return ret
