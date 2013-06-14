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


@TaskGen.feature('autoconf')
def feature_autoconf(self):
    #print 'Hello from feature "autoconf" for package "%s"' % self.autoconf_package
    pd = get_pkgdata(self.env.orch, self.autoconf_package)
    #pp.pprint(pd)

    bld = self.bld

    # define nodes that the tasks will rely on.  
    # FIXME: move this out somehow to allow user to query for list of what is needed.

    n_urlfile = bld.path.find_or_declare(urlfilename(pd))

    d_download = bld.path.find_or_declare(pd.get('download_dir','downloads'))
    n_tarball = d_download.make_node(pd.get('source_package'))

    d_source = bld.path.find_or_declare(pd.get('source_dir','sources'))
    d_unpacked = d_source.make_node(pd.get('source_unpacked'))
    n_configure = d_unpacked.make_node(pd.get('unpacked_target','configure'))

    d_build = bld.path.find_or_declare(pd.get('build_dir',
                                              'builds/{package}-{version}'.format(**pd)))
    n_config_status = d_build.make_node(pd.get('configure_target','config.status'))

    n_build_result = d_build.make_node(pd.get('build_target'))

    d_prefix = bld.root.make_node(pd.get('install_dir', bld.env.PREFIX))
    n_install_result = d_prefix.make_node(pd.get('install_target'))

    bld(name = '{package}_seturl'.format(**pd),
        rule = "echo %s > ${TGT}" % pd['source_url'], 
        update_outputs = True, target = n_urlfile,
        depends_on = get_deps(pd, 'seturl'))

    bld(name = '{package}_download'.format(**pd),
        rule = "wget --quiet -nv --no-check-certificate -i ${SRC} -O ${TGT}",
        source = n_urlfile, target = n_tarball,
        depends_on = get_deps(pd, 'download'))

    bld(name = '{package}_unpack'.format(**pd), 
        rule = "tar -xzf ${SRC[0].abspath()} -C ${TGT[0].parent.parent.abspath()}",
        source = n_tarball, target = n_configure,
        depends_on = get_deps(pd, 'unpack'))
    
    bld(name = '{package}_prepare'.format(**pd),
        rule = "${SRC[0].abspath()} --prefix=%s" % d_prefix.abspath(),
        source = n_configure,
        target = n_config_status,
        cwd = d_build.abspath(),
        depends_on = get_deps(pd, 'prepare'))

    bld(name = '{package}_build'.format(**pd),
        rule = "make",
        source = n_config_status,
        target = n_build_result,
        cwd = d_build.abspath(),
        depends_on = get_deps(pd, 'build'))

    bld(name = '{package}_install'.format(**pd),
        rule = "make install",
        source = n_build_result,
        target = n_install_result,
        cwd = d_build.abspath(),
        depends_on = get_deps(pd, 'install'))

    #print 'goodbye'
    #print self.__dict__
