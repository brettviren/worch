#!/usr/bin/env python
# encoding: utf-8

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

from waflib import TaskGen

def get_pkgdata(orch, name):
    for pd in orch:
        if name == pd['package']:
            return pd
    return None
    
def get_deps(pd, step):
    deps = pd.get('depends')
    if not deps: return
    mine = []
    for dep in [x.strip() for x in deps.split(',')]:
        if ':' in dep:
            dep = dep.split(':',1)
            if dep[0] == step:
                mine.append(dep[1])
                continue
        else:
            mine.append(dep)
    ret = ' '.join(mine)
    #if ret:
    #    print 'Package {package} step "{step}" depends: "{dep}"'.format(step=step,dep=ret,**pd)
    return ret


# policy
def urlfilename(pd): 
    return '{package}-{version}.url'.format(**pd)


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

class Paths(object):
    def __init__(self, ctx, pkgdata, defaults):
        self.ctx = ctx
        self.pkgdata = pkgdata
        self.defs = defaults
        
    def get_var(self, name):
        f = dict(self.defs)
        f.update(self.pkgdata)
        val = self.pkgdata.get(name, self.defs.get(name))
        if not val: return
        return self.check_return(name, val.format(**f))

    def get_node(self, name, dir_node = None):
        var = self.get_var(name)
        if not var: 
            return self.check_return('var:'+name)
        if dir_node:
            return self.check_return('node:%s/%s'%(name,var), dir_node.make_node(var))
        path = self.ctx.path
        if var.startswith('/'):
            path = self.ctx.root
        return self.check_return('node:%s/%s'%(name,var),  path.find_or_declare(var))

    def check_return(self, name, ret=None):
        if ret: return ret
        raise ValueError, 'Failed to get "%s" for package "%s"' % (name, self.pkgdata['package'])


@TaskGen.feature('tarball')
def feature_tarball(self):
    '''
    Handle a tarball source.  Implements steps seturl, download and unpack
    '''
    pd = get_pkgdata(self.env.orch, self.package_name)
    paths = Paths(self.bld, pd, tarball_requirements)

    f_urlfile = paths.get_node('source_urlfile')
    d_download = paths.get_node('download_dir')
    f_tarball = paths.get_node('source_package', d_download)

    d_source = paths.get_node('source_dir')
    d_unpacked = paths.get_node('source_unpacked', d_source)
    f_unpack = paths.get_node('unpacked_target', d_unpacked)

    self.bld(name = '{package}_seturl'.format(**pd),
             rule = "echo %s > ${TGT}" % pd['source_url'], 
             update_outputs = True, target = f_urlfile,
             depends_on = get_deps(pd, 'seturl'))

    self.bld(name = '{package}_download'.format(**pd),
             rule = "wget --quiet -nv --no-check-certificate -i ${SRC} -O ${TGT}",
             source = f_urlfile, target = f_tarball,
             depends_on = get_deps(pd, 'download'))

    self.bld(name = '{package}_unpack'.format(**pd), 
             rule = "tar -xzf ${SRC[0].abspath()} -C ${TGT[0].parent.parent.abspath()}",
             source = f_tarball, target = f_unpack,
             depends_on = get_deps(pd, 'unpack'))

    return

autoconf_requirements = {
    'source_dir': 'sources',
    'source_unpacked': '{package}-{version}',
    'configure_script': 'configure',
    'configure_target': 'config.status',
    'build_dir': 'builds/{package}-{version}',
    'build_target': None,
    'install_dir': '{PREFIX}',
    'install_target': None,
}

@TaskGen.feature('autoconf')
def feature_autoconf(self):
    #print 'Hello from feature "autoconf" for package "%s"' % self.autoconf_package
    pd = get_pkgdata(self.env.orch, self.package_name)
    paths = Paths(self.bld, pd, autoconf_requirements)

    # f_urlfile = bld.path.find_or_declare(urlfilename(pd))
    # d_download = bld.path.find_or_declare(pd.get('download_dir','downloads'))
    # n_tarball = d_download.make_node(pd.get('source_package'))

    d_source = paths.get_node('source_dir')
    d_unpacked = paths.get_node('source_unpacked', d_source)
    f_configure = paths.get_node('configure_script',d_unpacked)
    d_build = paths.get_node('build_dir')
    f_config_status = paths.get_node('configure_target', d_build)
    f_build_result = paths.get_node('build_target', d_build)

    d_prefix = paths.get_node('install_dir')
    f_install_result = paths.get_node('install_target', d_prefix)

    # bld(name = '{package}_seturl'.format(**pd),
    #     rule = "echo %s > ${TGT}" % pd['source_url'], 
    #     update_outputs = True, target = n_urlfile,
    #     depends_on = get_deps(pd, 'seturl'))

    # bld(name = '{package}_download'.format(**pd),
    #     rule = "wget --quiet -nv --no-check-certificate -i ${SRC} -O ${TGT}",
    #     source = n_urlfile, target = n_tarball,
    #     depends_on = get_deps(pd, 'download'))

    # bld(name = '{package}_unpack'.format(**pd), 
    #     rule = "tar -xzf ${SRC[0].abspath()} -C ${TGT[0].parent.parent.abspath()}",
    #     source = n_tarball, target = n_configure,
    #     depends_on = get_deps(pd, 'unpack'))
    
    self.bld(name = '{package}_prepare'.format(**pd),
        rule = "${SRC[0].abspath()} --prefix=%s" % d_prefix.abspath(),
        source = f_configure,
        target = f_config_status,
        cwd = d_build.abspath(),
        depends_on = get_deps(pd, 'prepare'))

    self.bld(name = '{package}_build'.format(**pd),
        rule = "make",
        source = f_config_status,
        target = f_build_result,
        cwd = d_build.abspath(),
        depends_on = get_deps(pd, 'build'))

    self.bld(name = '{package}_install'.format(**pd),
        rule = "make install",
        source = f_build_result,
        target = f_install_result,
        cwd = d_build.abspath(),
        depends_on = get_deps(pd, 'install'))

    #print 'goodbye'
    #print self.__dict__
    return
