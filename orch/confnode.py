import UserDict
import re 

def mgetter(callable):
    def f(match):
        key = match.group(1)
        val = callable(key,'{'+key+'}')
        return val
    return f

subn_reobj = re.compile('{(\w)}')

class Node(UserDict.DictMixin):
    'A dict-like object representing a node in the deconf hiearchy'
    
    def __init__(self, owner, name, type=None, parent = None, extra = None, **items):
        self._name, self._type, self._parent = name, type, parent
        self._extra = extra or dict()
        self._items = items
        self._owner = owner

        # optimization
        self._formatted = dict()
        self._keys = None
        self._nothers = 0

    def __str__(self):
        return '[%s]' % self.secname()

    def dict(self):
        'Return data as a dictionary'
        ret = dict()
        for k in self.keys():
            ret[k] = self[k]
        return ret

    def secname(self):
        'Return section name for this node'
        if self._type:
            return self._type + ' ' + self._name
        return self._name

    def owner(self): return self._owner

    def format(self, string, **extra):
        '''
        Format <string> using the node data and any <extra> keyword arguments.

        This format is like a simple str.format with only variable substitution 
        and not for mating codes.
        '''
        if not isinstance(string, type("")):
            raise TypeError("Node.format requires a string, got %s" % type(string))

        while True:
            new_string = string

            if extra:
                try:
                    #res = re.subn(r'{(\w+)}', mgetter(extra.get), new_string)
                    res = re.subn(subn_reobj, mgetter(extra.get), new_string)
                except KeyError:
                    pass
                else:
                    new_string = res[0]

            try:
                #res = re.subn(r'{(\w+)}', mgetter(self.raw), new_string)
                res = re.subn(subn_reobj, mgetter(self.raw), new_string)
            except KeyError:
                pass
            else:
                new_string = res[0]

            if new_string == string:
                return new_string
            string = new_string

    def raw(self, key, default = None):
        'Return the raw value associated with the key in the hierarchy.'
        try:                    # check if it's a direct key
            return self._items[key]
        except KeyError:
            pass

        if self._parent:
            try:                # check if parent knows it
                return self._parent.raw(key, default)
            except KeyError:
                pass

        try:                    # check if any node has it
            name, okey = key.split('_',1)
        except ValueError:
            pass
        else:
            try:
                other = self._owner.node(name)
                return other.raw(okey, default)
            except KeyError:
                pass

        return default
        
    def __getitem__(self, key):
        '''Return the value associated with the key performing as much
        formatting as possible.
        '''
        try:                    # check if we have formatted it already
            return self._formatted[key]
        except KeyError:
            pass

        val = self._owner.typed(key)
        if val:
            return val

        val = self.raw(key)
        val = self.format(val, **self._extra)
        self._formatted[key] = val
        return val

    def __setitem__(self, key, val):
        raise KeyError('can not set key "%s"' % (key, ))

    def local_keys(self):
        'Get the keys that this node holds directly.'
        ret = set()
        n = self
        while n is not None:
            ret.update(n._items.keys())
            n = n._parent
        return list(ret)
    def local_items(self):
        # fixme: should be a generator
        return [(k,self[k]) for k in self.local_keys()]


    def keys(self):
        'Return all keys as seen by this node.'
        others = self._owner.nodes().items()
        nothers = len(others)
        if self._keys:
            if nothers == self._nothers:
                return self._keys
        ret = set()
        for name, node in others:
            nkeys = node.local_keys()
            if name == self._name:
                ret.update(nkeys)
            ret.update([name + '_' + k for k in nkeys])

        ret = list(ret)
        self._keys = ret
        self._nothers = nothers
        return ret

    def incomplete(self):
        'Return list of any keys that are not complete'
        ret = list()
        for k in self.local_keys():
            v = self[k]
            if '{' in v:
                ret.append(k)
        return ret

class NodeGroup(UserDict.DictMixin):
    def __init__(self, keytype = None):
        self._nodes = dict()
        self._keytype = keytype or dict()

    def __call__(self, name, type = None, parent = None, extra=None, **items):
        if self._nodes.has_key(name):
            return self._nodes[name]
        node = Node(self, name, type, parent, extra, **items)
        self._nodes[name] = node
        return node

    def nodes(self):
        return self._nodes
    def node(self, name):
        return self._nodes[name]
        
    def typed(self, key):
        # check if it's a keytype node
        try:
            ktype = self._keytype[key]
        except KeyError:
            return
        ret = []
        for name, node in self.nodes().items():
            if node._type == ktype:
                ret.append(node)
        return ret
        
            
    def incomplete(self):
        'Return all incomplete nodes'
        ret = list()
        for n in self._nodes():
            if n.incomplete():
                ret.append(n)
        return ret

            
