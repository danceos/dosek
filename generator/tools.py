#!/usr/bin/python

"""
    @file
    @ingroup primitives
    @brief Santa's little helper.
"""

def abstract():
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError(caller + ' must be implemented in subclass')

variable_counter = 0
def new_variable_name():
    global variable_counter
    retval = "var_" + str(variable_counter)
    variable_counter += 1
    return retval

def format_source_tree(tree):
    if type(tree) == list:
        return "".join([format_source_tree(x) for x in tree])
    else:
        return tree.generate()

