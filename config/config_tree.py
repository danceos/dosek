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
    def __init__(self, stack, model = None, with_model = False, top = True):
        self.__with_model = with_model
        self.__model = model
        self.__stack = stack
        if top is True:
            self.__top = self
        else:
            self.__top = top

    def get(self, name):
        if type(name) in (tuple, list):
            (val, ty) = self.get(name[0])
            if isinstance(val, ConfigurationTreeStack):
                return val.get(name[1:])
            assert len(name) == 1, val
            return (val, ty)
        if name.startswith("/"):
            return self.__top.get(name[1:])
        ret = []
        for x in self.__stack:
            if not name in x:
                continue
            elem = x[name]
            if hasattr(elem, "evaluate"):
                elem = elem.evaluate(self)
            ret += [elem]
        
        is_config_tree = [isinstance(x, ConfigurationTree) for x in ret]
        if all(is_config_tree):
            assert self.__model and name in self.__model, "Subtree %s is not in model" % name
            return (ConfigurationTreeStack(ret, self.__model[name], self.__with_model, self.__top), None)
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
            ret = ConfigurationTreeStack(self.__stack, self.__model, True, self.__top)
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
    def __init__(self, short_help = None, long_help = None, default_value = None):
        self.short_help = short_help
        self.long_help = long_help
        if not default_value is None:
            self.default_value = default_value

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

def empty_configuration(model):
    d = {}
    for k, v in model.items():
        if isinstance(v, ConfigurationTree):
            v = empty_configuration(v)
        else:
            v = copy.copy(v.default_value)
        d[k] = v
    return ConfigurationTree(d, readonly = False)
