#!/usr/bin/python3
import os
from pprint import pprint
import copy
import logging
from config.model import model, constraints
from config.config_tree import *
from config.constraints import check_constraints


def from_file(fn):
    with open(fn, "rb") as fd:
        return ConfigurationTree(eval(fd.read().decode("utf8", 'ignore'), globals()))

class _toCMakeConfig:
    def cmake_key(self, path):
        if path[-1] == "self":
            path = path[:-1]
        return ("_".join([x.replace("-", "_") for x in path])).upper()

    def cmake_value(self, value, ty):
        if isinstance(ty, Boolean):
            return {True: "ON", False: "OFF"}[value]
        if isinstance(ty, Int):
            return str(value)
        if isinstance(ty, (String, OneOf)):
            return '"%s"' %( repr(ty.to_string(value))[1:-1])

    def cmake_type(self, ty):
        return {Boolean: "BOOL",
                Int: "INTEGER",
                OneOf: "STRING"}[ty.__class__]
    def __call__(self, config):
        x = ""
        for (p, (v, ty)) in config._:
            fmt = "set(CONFIG_%s %s CACHE INTERNAL %s)\n"
            line = fmt % (self.cmake_key(p),
                          self.cmake_value(v, ty),
                          self.cmake_type(ty))
            x += line
        return x

toCMakeConfig = _toCMakeConfig()

class _toCHeader:
    def key(self, path):
        if path[-1] == "self":
            path = path[:-1]
        return "CONFIG_" + ("_".join([x.replace("-", "_")  for x in path])).upper()

    def cmake_value(self, value, ty):
        if isinstance(ty, Boolean):
            return {True: "1", False: "0"}[value]
        if isinstance(ty, Int):
            return str(value)
        if isinstance(ty, String):
            return repr(ty.to_string(value)[1:-1] + '"')

    def __call__(self, config):
        ret = ""
        for (p, (v, ty)) in config._:
            macro = self.key(p)
            if isinstance(ty, Boolean):
                if v:
                    ret += "#define %s 1\n" % macro
                else:
                    ret += "#undef %s\n" % macro
            elif isinstance(ty, Int):
                 "#define %s %d\n" % (macro, v)
            elif isinstance(ty, OneOf):
                for sym in ty.symbols:
                    if sym == v:
                        ret += "#define %s_%s 1\n" % (macro, sym.upper().replace("-", "_"))
                    else:
                        ret += "#undef %s_%s\n" % (macro, sym.upper())
        return "#ifndef __CONFIG_HEADER_H\n#define __CONFIG_HEADER_H\n" \
            + ret \
            + "#endif\n"

to_c_header = _toCHeader()

to_string = repr




def into_optparse(model, parser, configuration = None):
    class OptParseAction:
        def __init__(self, path, ty, config):
            self.path = path
            self.ty = ty
            self.config = config

        def __call__(self, option, opt_str, value, parser):
            value = self.ty.from_string(value)
            self.config.set(self.path, value)

    def find_prefix(options, length = 1, from_beginning = False):
        # Options is an iteratable with (path-tuple, value)
        d = {}
        for path, ty in options:
            prefix = copy.copy(path)
            if path[-1] == "self":
                prefix = prefix[:-1]
            if from_beginning:
                prefix = prefix[:length]
            else:
                prefix = prefix[-length:]

            if prefix in d:
                # Conflict!
                d[prefix].append(tuple([path, ty]))
            else:
                d[prefix] = [tuple([path, ty])]
        for prefix, l in d.items():
            if len(l) == 1:
                yield (prefix, l[0])
            else:
                for x in find_prefix(l, length + 1, from_beginning = from_beginning):
                    yield x

    l = []
    if configuration is None:
        configuration = ConfigurationTree(readonly = False)

    for prefix, value in find_prefix(iter(model)):
        l.append(("-".join(prefix), value))
    for short_prefix, (long_prefix, (path, ty)) in find_prefix(l, from_beginning = True):

        action = OptParseAction(path, ty, configuration)

        default = ty.to_string(ty.default_value)
        help_text = ".".join(path) + "=" + ty.to_string(ty.default_value)

        if ty.short_help:
            help_text = "%s \t\t\t\t\t\t\t\t(%s)" %(ty.short_help, help_text)
        if len(short_prefix) == 1:
            short_prefix = '-' + short_prefix
            if parser.get_option(short_prefix):
                short_prefix = ''
        else:
            short_prefix = ''

        parser.add_option(short_prefix, '--' + long_prefix,  default = default, type=str,
                          help=help_text, action = "callback", callback = action)

    return configuration


if __name__ == "__main__":
    c = empty_configuration(model)
    find_constraints("*.py")
    print(c)
    for (k, ty) in model:
        print (k, ty)
