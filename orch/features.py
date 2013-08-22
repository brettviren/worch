#!/usr/bin/env python
# encoding: utf-8

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

from waflib import TaskGen

class PackageFeatureInfo(object):
    '''
    Give convenient access to all info about a package for features.

    Also sets the contexts group and env to the ones for the package.
    '''

    def __init__(self, package_name, feature_name, ctx, defaults):
        self.package_name = package_name
        self.feature_name = feature_name
        self.pkgdata = ctx.all_envs[''].orch_package_dict[package_name]
        self.env = ctx.all_envs[package_name]

        self.ctx = ctx

        # fixme: this is confusing
        self.defs = defaults
        f = dict(self.defs)
        f.update(dict(self.ctx.env))
        f.update(self.pkgdata)
        self._data = f

        group = self.get_var('group')
        self.ctx.set_group(group)

        print ('Feature: "{feature}" for package "{package}/{version}" in group "{group}"'.\
            format(feature = feature_name, **self.pkgdata))

    def __call__(self, name):
        return self.get_var(name)

    def format(self, string, **extra):
        d = dict(self._data)
        d.update(extra)
        return string.format(**d)

    def get_var(self, name):
        val = self.pkgdata.get(name, self.defs.get(name))
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
            #print 'Variable for {package}/{version}: {varname} = {value} ({full})'.\
            #    format(varname=name, value=ret, full=full, **self._data)
            return ret
        raise ValueError(
            'Failed to get "%s" for package "%s"' % 
            (name, self.pkgdata['package'])
            )

    def get_deps(self, step):
        deps = self.pkgdata.get('depends')
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
            print (self.format('Package {package} step "{step}" depends: "{dep}"',
                              step=step,dep=','.join(mine)))
        return mine



def get_unpacker(filename, dirname):
    if filename.endswith('.zip'): 
        return 'unzip -d %s %s' % (dirname, filename)
    
    text2flags = {'.tar.gz':'xzf', '.tgz':'xzf', '.tar.bz2':'xjf', '.tar':'xf' }
    for ext, flags in text2flags.items():
        if filename.endswith(ext):
            return 'tar -C %s -%s %s' % (dirname, flags, filename)
    return 'tar -C %s -xf %s' % (dirname, filename)

tarball_requirements = {
    'source_urlfile': '{package}-{version}.url',
    'source_url': None,
    'srcpkg_ext': 'tar.gz',
    'source_package': '{package}-{version}.{srcpkg_ext}',
    'download_dir': 'downloads',
    'download_target': '{download_dir}/{source_package}',
    'source_dir': 'sources',
    'source_unpacked': '{package}-{version}',
    'unpacked_target': 'configure',
}


@TaskGen.feature('tarball')
def feature_tarball(self):
    '''
    Handle a tarball source.  Implements steps seturl, download and unpack
    '''
    pfi = PackageFeatureInfo(self.package_name, 'tarball', self.bld, tarball_requirements)


    f_urlfile = pfi.get_node('source_urlfile')
    d_download = pfi.get_node('download_dir')
    f_tarball = pfi.get_node('source_package', d_download)

    d_source = pfi.get_node('source_dir')
    d_unpacked = pfi.get_node('source_unpacked', d_source)
    f_unpack = pfi.get_node('unpacked_target', d_unpacked)

    self.bld(name = pfi.format('{package}_seturl'),
             rule = "echo %s > ${TGT}" % pfi('source_url'), 
             update_outputs = True, target = f_urlfile,
             depends_on = pfi.get_deps('seturl'),
             env = pfi.env)

    self.bld(name = pfi.format('{package}_download'),
             rule = "curl --insecure --silent -L --output ${TGT} ${SRC[0].read()}",
             source = f_urlfile, target = f_tarball,
             depends_on = pfi.get_deps('download'),
             env = pfi.env)

    self.bld(name = pfi.format('{package}_unpack'), 
             rule = get_unpacker(f_tarball.abspath(), f_unpack.parent.parent.abspath()),
             source = f_tarball, target = f_unpack,
             depends_on = pfi.get_deps('unpack'),
             env = pfi.env)

    return

autoconf_requirements = {
    'source_dir': 'sources',
    'source_unpacked': '{package}-{version}',
    'prepare_script': 'configure',
    'prepare_script_options': '--prefix={install_dir}',
    'prepare_target': 'config.status',
    'build_dir': 'builds/{package}-{version}',
    'build_target': None,
    'install_dir': '{PREFIX}',
    'install_target': None,
}

@TaskGen.feature('autoconf')
def feature_autoconf(self):
    pfi = PackageFeatureInfo(self.package_name, 'autoconf', self.bld, autoconf_requirements)

    d_source = pfi.get_node('source_dir')
    d_unpacked = pfi.get_node('source_unpacked', d_source)
    f_prepare = pfi.get_node('prepare_script',d_unpacked)
    d_build = pfi.get_node('build_dir')
    f_prepare_result = pfi.get_node('prepare_target', d_build)
    f_build_result = pfi.get_node('build_target', d_build)

    d_prefix = pfi.get_node('install_dir')
    f_install_result = pfi.get_node('install_target', d_prefix)


    self.bld(name = pfi.format('{package}_prepare'),
             rule = "${SRC[0].abspath()} %s" % pfi.get_var('prepare_script_options'),
             source = f_prepare,
             target = f_prepare_result,
             cwd = d_build.abspath(),
             depends_on = pfi.get_deps('prepare'),
             env = pfi.env)

    self.bld(name = pfi.format('{package}_build'),
             rule = "make",
             source = f_prepare_result,
             target = f_build_result,
             cwd = d_build.abspath(),
             depends_on = pfi.get_deps('build'),
             env = pfi.env)

    self.bld(name = pfi.format('{package}_install'),
             rule = "make install",
             source = f_build_result,
             target = f_install_result,
             cwd = d_build.abspath(),
             depends_on = pfi.get_deps('install'),
             env = pfi.env)

    # testing
    # if pd['package'] != 'cmake':
    #     self.bld(name = '{package}_which'.format(**pd),
    #              rule = 'which cmake', env=pfi.env,
    #              depends_on = 'cmake_install')


    return

