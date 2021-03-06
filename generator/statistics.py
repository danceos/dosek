import pprint

class Statistics:
    def __init__(self, root):
        self.tree = self.__new_node(root)
        self.idx = {id(root): self.tree}

    def __new_node(self, item):
        return {"_id": id(item), "_type": item.__class__.__name__,
                "_name": repr(item)}

    def __stringify(self, obj):
        if type(obj) == dict:
            ret = {}
            for k,v in obj.items():
                ret[str(k)] = self.__stringify(v)
        elif type(obj) == list:
            ret = map(self.__stringify, obj)
        elif type(obj) == tuple:
            ret = tuple(map(self.__stringify, obj))
        elif type(obj) in (int, float, str, bool):
            ret = obj
        else:
            ret = '"' + repr(obj) + '"'
        return ret


    def add_child(self, parent, category, child):
        parent_id = id(parent)
        child_id  = id(child)
        assert parent_id in self.idx
        assert not child_id in self.idx
        parent = self.idx[parent_id]
        child = self.__new_node(child)
        child["_parent"] = parent_id
        self.idx[child_id] = child
        if not category in parent:
            parent[category] = [child]
        else:
            parent[category].append(child)

    def get_node(self, node):
        if type(node) == dict:
            node_id = node["_id"]
        elif type(node) == int:
            node_id = node
        else:
            node_id = id(node)
        if not node_id in self.idx:
            return None
        return self.idx[node_id]

    def get_parent(self, node):
        node = self.get_node(node)
        if not node:
            return None
        return self.get_node(node["_parent"])

    def add_data(self, parent, category, data, scalar=False):
        parent_id = id(parent)
        parent = self.idx[parent_id]
        if scalar:
            assert category not in parent
            parent[category] = data
        else:
            if not category in parent:
                if data in ([], None):
                    parent[category] = []
                else:
                    parent[category] = [self.__stringify(data)]
            elif data != None:
                parent[category].append(self.__stringify(data))

    def dump(self):
        ret = pprint.pformat(self.tree, width=150)
        return ret

    def rebuild_index(self, root, parent = None):
        if not type(root) == dict:
            return
        if parent:
            root["_parent"] = parent["_id"]
        for k, v in root.items():
            if k == "_id":
                self.idx[v] = root
            if type(v) == list:
                for child in v:
                    self.rebuild_index(child, root)

    def save(self, filename):
        with open(filename, "w+") as fd:
            fd.write(self.dump())

    def find_all(self, _type):
        ret = {}
        for k, v in self.idx.items():
            if v["_type"] == _type:
                ret[k] = v
        return ret

    def find_one(self, _type):
        ret = self.find_all(_type)
        assert len(ret) == 1
        return ret.values()[0]

    @staticmethod
    def load(filename):
        ins = Statistics(None)
        with open(filename) as fd:
            data = fd.read()
            ins.tree = eval(data)
            ins.idx = {}
            ins.rebuild_index(ins.tree)

        return ins
