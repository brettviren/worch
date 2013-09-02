import waflib.Logs as msg

class PackageFeatureInfo(object):
    '''
    Give convenient access to all info about a package for features.

    Also sets the contexts group and env to the ones for the package.
    '''

    def __init__(self, package_name, feature_name, ctx, defaults):
        self.package_name = package_name
        self.feature_name = feature_name
        self.env = ctx.all_envs[package_name]
        environ = self.env.munged_env
        self.env.env = environ

        self.ctx = ctx

        # build up parameters starting with defaults from the "requirements"
        f = dict(defaults)      
        f.update(dict(self.ctx.env)) # waf env 
        # and final override by the configuration file data
        f.update(ctx.all_envs[''].orch_package_dict[package_name])
        self._data = f

        group = self.get_var('group')
        self.ctx.set_group(group)

        msg.debug(
            'orch: Feature: "{feature}" for package "{package}/{version}" in group "{group}"'.
            format(feature = feature_name, **self._data))

    def __call__(self, name):
        return self.get_var(name)

    def format(self, string, **extra):
        d = dict(self._data)
        d.update(extra)
        return string.format(**d)

    def get_var(self, name):
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
