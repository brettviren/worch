import os
from collections import namedtuple, OrderedDict, defaultdict

def odictify(kwds = None):
    if kwds:
        return tuple(kwds.items())
    return ()
def Node(name, **options):
    return namedtuple('Node','name options')(name,odictify(options))
def Edge(tail, head, **options):
    return namedtuple('Edge','tail head options')(tail, head, odictify(options))

def opt_to_str(options):
    if not options:
        return ''
    return ','.join(['%s="%s"' % kv for kv in options])

class Graph(object):
    def __init__(self, name, **options):
        self.name = name
        self.options = options or dict()
        self.subgraphs = OrderedDict()
        self.nodes = set()
        self.edges = set()

    def graph(self, name = None):
        if name is None or name == self.name:
            return self
        g = self.subgraphs.get(name)
        if not g: 
            self.subgraphs[name] = g = Graph(name)
        return g

    def add_subgraph(self, name, **options):
        self.subgraphs[name] = g = Graph(name, **options)
        return g

    def add_node(self, name, graph_name = None, **options):
        self.graph(graph_name).nodes.add(Node(name,**options))

    def add_edge(self, tail, head, graph_name = None, **options):
        self.graph(graph_name).edges.add(Edge(tail,head,**options))

    def todot(self, depth = 0):
        ret = []
        tab = '    '

        indent = tab * depth 

        graphtype = "digraph "
        if depth:
            graphtype = "subgraph cluster"
        ret.append('%s%sg%s {' % (indent, graphtype, self.name))

        for k,v in self.options.items():
            ret.append('%s%s = "%s";' % (indent, k, v))

        for sg in self.subgraphs.values():
            ret.append(sg.todot(depth+1))

        indent = tab * (depth + 1)
        for node in self.nodes:
            ret.append('%s"%s" [%s];' % (indent, node.name, opt_to_str(node.options)))

        for edge in self.edges: # fixme: this ignore edge options
            ret.append('%s"%s" -> "%s";' % (indent, edge.tail, edge.head))

        ret.append('%s}' % indent)
        return '\n'.join(ret)

    def __str__(self):
        return self.todot()

def write(fname, graph):
    with open(fname, 'w') as fp:
        fp.write(graph)

def make(bld):
    '''
    Return a graph of the task dependencies
    '''

    # Explicit posting of the top level task generators, which are
    # features, is needed so they can run an produce their (sub) task
    # generators
    for tg in bld.get_all_task_gen():
        tg.post()

    # for tg in bld.get_all_task_gen():
    #     #print tg, tg.__dict__.keys()
    #     print '%s: %s -> %s, depends_on:%s' % \
    #         (tg.name, tg.source, tg.target,
    #          getattr(tg, 'depends_on', 'none'))

    graph = Graph('worch')

    for tg in bld.get_all_task_gen():

        # this is a feature
        if hasattr(tg, 'package_name'):
            #packages.add(tg.package_name)
            continue
            
        package_name = tg.name.split('_',1)[0]

        graph.add_node(tg.name, package_name, shape='ellipse')

        if hasattr(tg,'depends_on') and tg.depends_on:
            deps = tg.depends_on
            if isinstance(deps, type('')):
                deps = [tg.depends_on]
            for dep in deps:
                graph.add_edge(dep, tg.name)

        if hasattr(tg, 'source') and tg.source:
            fname = tg.source.nice_path()
            spkg_name = fname.split('_',1)[0]
            graph.add_node(fname, spkg_name, shape='box')
            graph.add_edge(fname, tg.name)

        if hasattr(tg, 'target') and tg.target:
            fname = tg.target.nice_path()
            tpkg_name = fname.split('_',1)[0]
            graph.add_node(fname, tpkg_name, shape='box')
            graph.add_edge(tg.name, fname)
        continue

        # loop over groups
    return
