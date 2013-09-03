#!/usr/bin/env python
import waflib.Logs as msg
import os.path as osp
from . import requirements as reqmod
from orch import deconf

class PackageFeatureInfo(object):
    '''
    Give convenient access to all info about a package for features.

    Also sets the contexts group and env to the ones for the package.
    '''

    def __init__(self, feature_name, ctx, **pkgcfg):
        package_name = pkgcfg['package']

        for req in reqmod.reqdesc_list:
            if not req.relative:
                continue
            val = pkgcfg.get(req.name)
            if val is None:     # happens if req doesn't apply to feature
                continue
            val = osp.join(req.relative, val)
            pkgcfg[req.name] = val
            
        self._data = deconf.format_flat_dict(pkgcfg)
        self.feature_name = feature_name
        self.package_name = package_name
        self.env = ctx.all_envs[package_name]
        self.env.env = self.env.munged_env
        self.ctx = ctx

        group = self.group
        self.ctx.set_group(group)

        #print 'PFI:', package_name, feature_name, sorted(self._data.items())

        msg.debug(
            'orch: Feature: "{feature}" for package "{package}/{version}" in group "{group}"'.
            format(feature = feature_name, **self._data))

    def __call__(self, name, dir = None):
        if dir and isinstance(dir, type('')):
            dir = self.get_node(dir)
        return self.get_node(name, dir)

    def __getattr__(self, name):
        val = self._data[name]
        if val is None:
            raise ValueError, '"%s" is None for feature: "%s", package: "%s"' % \
                (name, self.feature_name, self.package_name)
        req = reqmod.pool.get(name)
        if req and req.typecode.lower() in ['f','d']:
            return self.node(val)
        return val

    def node(self, path):
        n = self.ctx.bldnode
        if path.startswith('/'):
            n = self.ctx.root
        return n.make_node(path)


    def task(self, name, **kwds):
        task_name = self.format('{package}_%s'%name)
        kwds.setdefault('env', self.env)
        kwds.setdefault('depends_on', self.get_deps(name))
        return self.ctx(name = task_name, **kwds)
        

    def insert_dependency(self, before, after):
        '''
        Insert step name <before> before step named <after>
        '''
        tsk = self.ctx.get_tgen_by_name(self.format('{package}_{after}', after=after))
        tsk.depends_on.append(self.format('{package}_{before}', before=before))
        return


    def format(self, string, **extra):
        d = dict(self._data)
        d.update(extra)
        return string.format(**d)

    def get_var(self, name):
        if name not in self._allowed:
            raise KeyError, 'not allowed name: "%s"' % name
        val = self._data.get(name)
        if not val: return
        return self.check_return(name, self.format(val))

    def get_node(self, name, dir_node = None):
        var = self.get_var(name)
        if not var: 
            return self.check_return('var:'+name)
        if dir_node:
            return self.check_return('node:%s/%s'%(name,var), dir_node.make_node(var))
        path = self.ctx.bldnode
        if var.startswith('/'):
            path = self.ctx.root
        return self.check_return('node:%s/%s'%(name,var),  path.make_node(var))

    def check_return(self, name, ret=None):
        if ret: 
            # try:
            #     full = ret.abspath()
            # except AttributeError:
            #     full = ''
            #msg.debug('orch: Variable for {package}/{version}: {varname} = {value} ({full})'.\
            #    format(varname=name, value=ret, full=full, **self._data))
            return ret
        raise ValueError(
            'Failed to get "%s" for package "%s" (keys: %s)' % 
            (name, self._data['package'], ', '.join(sorted(self._data.keys())))
            )

    def get_deps(self, step):
        deps = self._data.get('depends')
        if not deps: return list()
        mine = []
        for dep in [x.strip() for x in deps.split(',')]:
            if ':' in dep:
                dep = dep.split(':',1)
                if dep[0] == step:
                    mine.append(dep[1])
                    continue
            else:
                mine.append(dep)
        if mine:
            msg.debug(
                self.format('orch: Package {package} step "{step}" depends: "{dep}"',
                            step=step,dep=','.join(mine))
                )
        return mine

registered_func = dict()        # feature name -> function
registered_config = dict()  # feature name -> configuration dictionary
def feature(feature_name, **feature_config):
    def wrapper(feat_func):
        def wrap(bld, package_config):
            pfi = PackageFeatureInfo(feature_name, bld, **package_config)
            return feat_func(pfi)
        registered_func[feature_name] = wrap
        registered_config[feature_name] = feature_config
        return wrap
    return wrapper
