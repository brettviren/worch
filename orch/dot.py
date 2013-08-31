import os
import waflib

class Dotter:
    def __init__(self, fname):
        self.fname = fname
        self.ingraph = False
    def __enter__(self):
        self.fp = open(self.fname, 'w')
        return self
    def __exit__(self, t,v,tb):
        self.end_graph()
        self.fp.close()
        del(self.fp)
        return
    def start_graph(self, name):
        if self.ingraph:
            self.end_graph()
        self.fp.write('digraph %s {\n' % name)
        self.ingraph = True
    def end_graph(self):
        if not self.ingraph:
            return
        self.fp.write('\t}\n')
        self.ingraph = False
    def add_node(self, name, **kwds):
        if not kwds.get('label'):
            kwds['label'] = name
        kwds.setdefault('shape', 'ellipse')
        opts = ','.join(['%s="%s"'%kv for kv in kwds.items()])
        self.fp.write('\t"%s" [%s];\n' % (name, opts))
    def add_edge(self, tail, head):
        self.fp.write('\t"%s" -> "%s";\n' % (tail, head))


def write(bld, dot_fname):
    '''
    Write a dot digraph file for the given build context <bld> into file name <dot_fname>.
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

    task_names = set()
    file_names = set()
    packages = set()
    graph_name = os.path.splitext(os.path.basename(dot_fname))[0]
    with Dotter(dot_fname) as graph:
        graph.start_graph(graph_name)

        for tg in bld.get_all_task_gen():

            # this is a feature
            if hasattr(tg, 'package_name'):
                packages.add(tg.package_name)
                continue
            
            package_name = tg.name.split('_',1)[0]

            if tg not in task_names:
                task_names.add(tg.name)
                graph.add_node(tg.name)

            if hasattr(tg,'depends_on') and tg.depends_on:
                deps = tg.depends_on
                if isinstance(deps, type('')):
                    deps = [tg.depends_on]
                for dep in deps:
                    graph.add_edge(dep, tg.name)

            if hasattr(tg, 'source') and tg.source:
                #print 'SOURCE', type(tg.source),tg.source
                source = tg.source
                if not isinstance(source, list):
                    source = [source]
                for fname in source:
                    fname = fname.nice_path()
                    if fname not in file_names:
                        file_names.add(fname)
                        graph.add_node(fname, shape='box')
                    graph.add_edge(fname, tg.name)

            if hasattr(tg, 'target') and tg.target:
                #print 'TARGET', type(tg.target),tg.target
                target = tg.target
                if not isinstance(target, list):
                    target = [target]
                for fname in target:
                    fname = fname.nice_path()
                    if fname not in file_names:
                        file_names.add(fname)
                        graph.add_node(fname, shape='box')
                    graph.add_edge(tg.name, fname)
            continue

        # loop over groups
    return
