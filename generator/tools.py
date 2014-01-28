#!/usr/bin/python

"""
    @file
    @ingroup rules
    @brief
"""

import sys
import logging

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

def flatten(seq):
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


def panic(fmt, *args):
    logging.error(fmt, *args)
    sys.exit(-1)

def merge_dict_tree(tree_a, tree_b, depth = 0):
    if tree_a == None:
        return tree_b
    if tree_b == None:
        return tree_a
    key_a = set(tree_a.keys())
    key_b = set(tree_b.keys())
    if depth == 0:
        assert key_a != key_b, "%s ~~ %s"%(key_a, key_b)
        return dict(tree_a.items() + tree_b.items())
    else:
        ret = {}
        for key in key_a | key_b:
            ret[key] = merge_dict_tree(tree_a.get(key),
                                       tree_b.get(key),
                                       depth - 1)
        return ret
