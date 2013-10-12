#!/usr/bin/python

"""
    @file 
    @ingroup primitives
    @brief Santa's little helper.
"""



def format_source_tree(tree):
    if type(tree) == list:
        return "".join([format_source_tree(x) for x in tree])
    else:
        return tree.generate()

