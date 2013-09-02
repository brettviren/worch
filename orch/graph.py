#!/usr/bin/env python
'''
Simple implementation of a data structure providing a directed
acyclic graph with subgraphs.
'''
from collections import namedtuple, OrderedDict

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
        self.options = options
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
        already = self.subgraphs.get(name)
        if already:
            already.options = options
            return already
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
        ret.append('%s%s%s {' % (indent, graphtype, self.name))

        for k,v in self.options.items():
            ret.append('%s%s = "%s";' % (indent, k, v))

        for sg in self.subgraphs.values():
            ret.append(sg.todot(depth+1))

        indent = tab * (depth + 1)
        for node in self.nodes:
            ret.append('%s"%s" [%s];' % (indent, node.name, opt_to_str(node.options)))

        for edge in self.edges: # fixme: this ignore edge options
            ret.append('%s"%s" -> "%s" [%s];' % (indent, edge.tail, edge.head, 
                                                 opt_to_str(edge.options)))

        ret.append('%s}' % indent)
        return '\n'.join(ret)

    def __str__(self):
        return self.todot()
