#!/usr/bin/python3
import os
from pprint import pprint
import copy



class NamespaceDict(dict):
    __readonly = False
    __initialized = False

    def __init__(self, d=None, readonly = True, **kwargs):
        self.__readonly = readonly
        if d:
            self.update(d)
        self.update(kwargs)
        self.__initialized = True

    def __getattr__(self, name):
        try:
            return dict.__getattribute__(self, name)
        except AttributeError:
            pass
        if name in self:
            return self[name]
        name = name.replace("_", "-")
        if name in self:
            return self[name]
        raise (AttributeError(repr(name)))

    def __contains__(self, name):
        return dict.__contains__(self, name) \
            or dict.__contains__(self, name.replace("_", "-"))

    def __getitem__(self, name):
        return dict.get(self, name) \
            or dict.__getitem__(self, name.replace("_", "-"))

    def __setattr__(self, name, value):
        if self.__readonly and self.__initialized:
            raise TypeError("object is read only")
        if name.startswith("_") or not self.__initialized:
            dict.__setattr__(self, name, value)
        else:
            dict.__setitem__(self, name, value)

    def __setitem__(self, name, value):
        if self.__readonly:
            raise TypeError("object is read only")
        dict.__setitem__(self, name, value)

class ConfigurationTree(NamespaceDict):
    def __init__(self, d = None, readonly = True, **kwargs):
        if not d:
            d = dict()
        d.update(kwargs)
        for k in list(d.keys()):
            assert type(k) == str, "Key in configuration tree must be a string"
            if type(d[k]) == dict:
                d[k] = ConfigurationTree(d[k])
        NamespaceDict.__init__(self, d, readonly = readonly)

    def __iter__(self, base = None):
        if base is None:
            base = []
        for name, model in self.items():
            path = base + [name]
            if isinstance(model, ConfigurationTree):
                for x in model.__iter__(path):
                    yield x
            else:
                yield (tuple(path), model)

    def set(self, path, value):
        if not type(path) in (list,tuple):
            path = (path, )
        if len(path) == 1:
            self[path[0]] = value
        else:
            if not path[0] in self:
                self[path[0]] = ConfigurationTree(readonly = False)
            self[path[0]].set(path[1:], value)


class ConfigurationTreeStack(object):
    def __init__(self, stack, model = None, with_model = False):
        self.__with_model = with_model
        self.__model = model
        self.__stack = stack

    def get(self, name):
        ret = [x[name] for x in self.__stack if name in x]
        is_config_tree = [isinstance(x, ConfigurationTree) for x in ret]
        if all(is_config_tree):
            assert self.__model and name in self.__model, "Subtree %s is not in model" % name
            return (ConfigurationTreeStack(ret, self.__model[name], self.__with_model), None)
        elif all([not(x) for x in is_config_tree]):
            assert len(ret) == 1 or all(ret[1] == x for x in ret[1:]), "Every value in the tree has to be consistent"
            assert isinstance(ret[-1], self.__model[name].config_type)
            return (ret[-1], self.__model[name])
        else:
            raise AttributeError("The configuration tree is not valid (leaf and subtree at some position)")

    def __iter__(self, base = None):
        if base is None:
            base = []
        for name, model in self.__model.items():
            path = base + [name]
            value = self.__getattr__(name)
            if isinstance(value, ConfigurationTreeStack):
                for x in value.__iter__(path):
                    yield x
            else:
                yield (tuple(path), value)

    def __getattr__(self, name):
        if name == "_":
            ret = ConfigurationTreeStack(self.__stack, self.__model, True)
            return ret
        ret = self.get(name)
        if self.__with_model and ret[1] != None:
            return ret
        return ret[0]

    def as_dict(self):
        ret = ConfigurationTree(readonly = False)
        for path, (v, ty) in self._:
            ret.set(path, v)
        return ret

class ConfigurationItem:
    def __init__(self, short_help = None, long_help = None):
        self.short_help = short_help
        self.long_help = long_help

class OneOf(ConfigurationItem, NamespaceDict):
    config_type = str

    default_value = ""

    def __init__(self, symbols = [], **kwargs):
        ConfigurationItem.__init__(self, **kwargs)
        self.default_value = symbols[0]
        self.symbols = symbols

        NamespaceDict.__init__(self, {x:x for x in symbols})

    def to_string(self, value):
        assert value in self.symbols
        return value

    def from_string(self, value):
        assert value in self.symbols
        return value

class String(ConfigurationItem):
    config_type = str

    default_value = ""

    to_string = lambda self, x: x
    from_string = lambda self, x: x


class Boolean(ConfigurationItem):
    def __init__(self, **kwargs):
        ConfigurationItem.__init__(self, **kwargs)

    config_type = bool

    default_value = False

    to_string = lambda self, x: str(x)

    from_string = lambda self, x: x.lower() in ("yes", "1", "true", "Y", "y", "t")

class Int():
    def __init__(self, **kwargs):
        ConfigurationItem.__init__(self, **kwargs)

    config_type = int

    default_value = 0

    to_string = str

    from_string = int


def from_file(fn):
    with open(fn) as fd:
        return ConfigurationTree(eval(fd.read(), globals()))

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
            return repr(ty.to_string(value))

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
                        ret += "#define %s_%s 1\n" % (macro, sym.upper())
                    else:
                        ret += "#define %s_%s 1\n" % (macro, sym.upper())
        return "#ifndef __CONFIG_HEADER_H\n#define __CONFIG_HEADER_H\n" \
            + ret \
            + "#endif\n"

to_c_header = _toCHeader()

to_string = repr

def empty_configuration(model):
    d = {}
    for k, v in model.items():
        if isinstance(v, ConfigurationTree):
            v = empty_configuration(v)
        else:
            v = copy.copy(v.default_value)
        d[k] = v
    return ConfigurationTree(d, readonly = False)



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
        #print (short_prefix, long_prefix, path, ty.to_string(ty.default_value))

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

model = from_file(os.path.join(os.path.dirname(__file__), "model.py"))

if __name__ == "__main__":
    c = empty_configuration(model)
    print(c)
    for (k, ty) in model:
        print (k, ty)
