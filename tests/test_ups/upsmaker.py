#!/usr/bin/env python
'''
Produce UPS table files.  

The format is logically:

Table files: (product, [groups])
Product: string giving canonical package name
Group: ([instances], [actions])
Instance: (flavor, [qualifiers], [actions])
Flavor: string giving canonical platform name or ANY
Qualifier: string giving build qualifiers or empty
Action: (action_type, [commands])
Action Type: string giving type of action (usually "SETUP")
Command: string giving a UPS command, typically a function
'''

class Element(object):
    def format(self, string, **kwds):
        d = dict(self.__dict__)
        d.update(**kwds)
        return string.format(**d)

class TableFile(Element):

    def __init__(self, product, groups = None):
        self.product = product
        self.groups = groups or list()
    def __str__(self):
        ret = ['File = Table', self.format('Product = {product}')]
        ret += [str(g) for g in self.groups]
        return '\n'.join(ret)

class Group(Element):
    def __init__(self, instances = None, common = None):
        self.instances = instances or list()
        self.common = common or list()
    def __str__(self):
        ret  = ['Group:']
        ret += [str(x) for x in self.instances]
        ret += ['Common:']
        ret += [str(x) for x in self.common]
        ret += ['End:']
        return '\n'.join(ret)

class Instance(Element):
    def __init__(self, flavor=None, qualifiers=None, actions=None):
        self.flavor = flavor or 'ANY'
        self.qualifiers = qualifiers or list()
        self.actions = actions or list()
    def __str__(self):
        ret  = [self.format('Flavor = {flavor}')]
        q = ':'.join(self.qualifiers) or '""'
        ret += ['Qualifiers = ' + q ]
        ret += [str(x) for x in self.actions]
        return '\n'.join(ret)

class Action(Element):
    allowed_actions = 'configure unconfigure copy declare undeclare get modify setup unsetup start stop tailor'.split()

    tab = ' '*4

    def __init__(self, name='SETUP', commands = None):
        if name.lower() not in self.allowed_actions:
            raise ValueError('%s not an allowed action'%name)
        if not commands:
            raise ValueError('Action "%s" has not commands'%name)
        self.name = name
        self.commands = commands
    def __str__(self):
        ret  = [self.tab + self.format('Action = {name}')]
        ret += [self.tab*2 + str(x) for x in self.commands]
        return '\n'.join(ret)

def test():
    tf = TableFile(
        'hello',
        groups = [
            Group(
                instances=[
                    Instance(actions=[
                            Action(commands=[
                                    'pathPrepend(PATH, ${UPS_PROD_DIR}/bin)',
                                    ])])],
                common=[ Action(commands=[ 'setupEnv()' ])])])
    print tf

if '__main__' == __name__:
    test()
