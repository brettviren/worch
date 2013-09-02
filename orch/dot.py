#!/usr/bin/env python
'''
Write a dot file which shows the waf dependency graph.
'''
from .graph import Graph


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

    maingraph = Graph('worch', rankdir='LR')

    tsk2graph = dict()
    pkg2features = dict()
    for igroup, group in enumerate(bld.groups):
        number = 1 + igroup
        group_name = 'Group%d' % number
        group_graph = maingraph.add_subgraph(group_name, label=group_name)
        #print 'Group',group_name,':',id(group_graph)
        for thing in group:
            if hasattr(thing, 'package_name'):
                #print 'Skipping:', thing.name, thing.package_name, thing.features
                pkg, feats = thing.name.split('_',1)
                pkg2features[pkg] = feats
                continue

            name = thing.name
            already = tsk2graph.get(name)
            if already:
                assert already == group_graph, (name, already, group_graph)
            else:
                tsk2graph[name] = group_graph
            #print name,'->',group_name

    for tg in bld.get_all_task_gen():

        # this is a feature
        if hasattr(tg, 'package_name'):
            # ignore this
            continue
            
        package_name = tg.name.split('_',1)[0]
        package_files_name = package_name + 'files'

        group_graph = tsk2graph[tg.name]
        pkg_graph = group_graph.add_subgraph(package_name, label = package_name)
        file_graph = group_graph.add_subgraph(package_files_name, label = package_name + ' files')

        pkg_graph.add_node(tg.name, shape='ellipse')

        if hasattr(tg,'depends_on') and tg.depends_on:
            deps = tg.depends_on
            if isinstance(deps, type('')):
                deps = [tg.depends_on]
            for dep in deps:
                maingraph.add_edge(dep, tg.name, style='bold')

        if hasattr(tg, 'source') and tg.source:
            fname = tg.source.nice_path()
            # Double places packages?
            file_graph.add_node(fname, shape='box')
            maingraph.add_edge(fname, tg.name)

        if hasattr(tg, 'target') and tg.target:
            fname = tg.target.nice_path()
            file_graph.add_node(fname, package_files_name, shape='box')
            maingraph.add_edge(tg.name, fname)
        continue

        # loop over groups
    return maingraph


def write(bld, fname):
    graph = make(bld)
    with open(fname, 'w') as fp:
        fp.write(str(graph))

