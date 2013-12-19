#!/usr/bin/python
# In this file all helper functions are inserted, that are used in
# various rules, like doing some debug print, or calling of a
# function.

from copy import copy
from generator.atoms import *
from generator.primitives import *

def update_requirements(atom, requirements):
    for req in requirements:
        if req in  set(["__references_headers", "__references_objects"]):
            if req in atom:
                for x in requirements[req]:
                    if not x in atom[req]:
                        atom[req].append(x)
            else:
                atom[req] = copy(requirements[req])
        else:
            assert "Unkown requirement %s" % req

def stringify(string):
    if type(string) == str:
        return '"%s"' % string
    return stringify(repr(string).replace('"', '\"'))


def object_COM(generator, interface="COM1"):
    """Returns a variable to a serial output driver, which can be used for
    debug printing"""
    varname = generator.variable_name_for_singleton("Serial", interface)
    serial = DataObject("Serial", varname, "Serial(Serial::%s)" % interface)
    return (serial, {"__references_headers": ["serial.h"] })



def atom_kout(generator, *expressions):
    """Generates a print statement to a serial console"""
    stmt = Statement.atom()
    obj, requirements = object_COM(generator)
    # Register object in the statement
    update_requirements(stmt, requirements)
    update_requirements(stmt, {"__references_objects": [obj]})

    stmt["statement"] = "%s << %s;" % (obj.variable, " << ".join(expressions))
    return stmt


