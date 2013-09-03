#!/usr/bin/env python
from waflib import TaskGen
from .pfi import PackageFeatureInfo

from orch.wafutil import exec_command

git_requirements = {
    'git_urlfile': '{package}.git.url',
    'git_url': None,
    'git_cmd': 'git clone',
    'git_cmd_options': '',
    'source_dir': 'sources',
    'source_unpacked': '{package}-git',
    'unpacked_target': 'configure',
}


@TaskGen.feature('git')
def feature_git(self):
    '''
    Checkout a git repository.  Implements steps seturl and checkout.
    '''
    pfi = PackageFeatureInfo(self.package_name, 'git', self.bld, git_requirements)


    if not pfi('git_url'):
        self.fatal(
            "git feature enabled for package [%s] but not 'git_url'" %
            self.package_name,
            )
        return
    
    f_urlfile = pfi.get_node('git_urlfile')

    d_source = pfi.get_node('source_dir')
    d_unpacked = pfi.get_node('source_unpacked', d_source)
    f_unpack = pfi.get_node('unpacked_target', d_unpacked)

    def create_urlfile(task):
        tgt = task.outputs[0]
        tgt.write("%s %s -b %s %s %s" % (
            pfi.get_var('git_cmd'),
            pfi.get_var('git_cmd_options') or '',
            pfi.get_var('version'),
            pfi.get_var('git_url'),
            d_unpacked.abspath(),
            ))
        return 0
    
    self.bld(name = pfi.format('{package}_seturl'),
             rule = create_urlfile,
             update_outputs = True,
             target = f_urlfile,
             depends_on = pfi.get_deps('seturl'),
             env = pfi.env)

    def checkout_task(task):
        src = task.inputs[0]
        tgt = task.outputs[0]
        cmd = "%s" % (src.read(),)
        return exec_command(task, cmd)

    self.bld(name = pfi.format('{package}_checkout'),
             rule = checkout_task,
             source = f_urlfile,
             target = f_unpack,
             depends_on = pfi.get_deps('checkout'),
             cwd = d_source.abspath(),
             env = pfi.env)

    return

hg_requirements = {
    'hg_urlfile': '{package}.hg.url',
    'hg_url': None,
    'hg_cmd': 'hg clone',
    'hg_cmd_options': '',
    'source_dir': 'sources',
    'source_unpacked': '{package}-hg',
    'unpacked_target': 'configure',
}


@TaskGen.feature('hg')
def feature_hg(self):
    '''
    Checkout a mercurial repository.  Implements steps seturl and checkout.
    '''
    pfi = PackageFeatureInfo(self.package_name, 'hg', self.bld, hg_requirements)


    if not pfi('hg_url'):
        self.fatal(
            "hg feature enabled for package [%s] but not 'hg_url'" %
            self.package_name,
            )
        return
    
    f_urlfile = pfi.get_node('hg_urlfile')

    d_source = pfi.get_node('source_dir')
    d_unpacked = pfi.get_node('source_unpacked', d_source)
    f_unpack = pfi.get_node('unpacked_target', d_unpacked)

    def create_urlfile(task):
        tgt = task.outputs[0]
        tgt.write("%s %s -b %s %s %s" % (
            pfi.get_var('hg_cmd'),
            pfi.get_var('hg_cmd_options') or '',
            pfi.get_var('version'),
            pfi.get_var('hg_url'),
            d_unpacked.abspath(),
            ))
        return 0
    
    self.bld(name = pfi.format('{package}_seturl'),
             rule = create_urlfile,
             update_outputs = True,
             target = f_urlfile,
             depends_on = pfi.get_deps('seturl'),
             env = pfi.env)

    def checkout_task(task):
        src = task.inputs[0]
        tgt = task.outputs[0]
        cmd = "%s" % (src.read(),)
        return exec_command(task, cmd)

    self.bld(name = pfi.format('{package}_checkout'),
             rule = checkout_task,
             source = f_urlfile,
             target = f_unpack,
             depends_on = pfi.get_deps('checkout'),
             cwd = d_source.abspath(),
             env = pfi.env)

    return

svn_requirements = {
    'svn_urlfile': '{package}.svn.url',
    'svn_url': None,
    'svn_cmd': 'svn checkout',
    'svn_cmd_options': '',
    'source_dir': 'sources',
    'source_unpacked': '{package}-svn',
    'unpacked_target': 'configure',
}


@TaskGen.feature('svn')
def feature_svn(self):
    '''
    Checkout a subversion repository.  Implements steps seturl and checkout.
    '''
    pfi = PackageFeatureInfo(self.package_name, 'svn', self.bld, svn_requirements)


    if not pfi('svn_url'):
        self.fatal(
            "svn feature enabled for package [%s] but not 'svn_url'" %
            self.package_name,
            )
        return
    
    f_urlfile = pfi.get_node('svn_urlfile')

    d_source = pfi.get_node('source_dir')
    d_unpacked = pfi.get_node('source_unpacked', d_source)
    f_unpack = pfi.get_node('unpacked_target', d_unpacked)

    def create_urlfile(task):
        tgt = task.outputs[0]
        tgt.write("%s %s %s %s" % (
            pfi.get_var('svn_cmd'),
            pfi.get_var('svn_cmd_options') or '',
            pfi.get_var('svn_url'),
            d_unpacked.abspath(),
            ))
        return 0
    
    self.bld(name = pfi.format('{package}_seturl'),
             rule = create_urlfile,
             update_outputs = True,
             target = f_urlfile,
             depends_on = pfi.get_deps('seturl'),
             env = pfi.env)

    def checkout_task(task):
        src = task.inputs[0]
        tgt = task.outputs[0]
        cmd = "%s" % (src.read(),)
        return exec_command(task, cmd)

    self.bld(name = pfi.format('{package}_checkout'),
             rule = checkout_task,
             source = f_urlfile,
             target = f_unpack,
             depends_on = pfi.get_deps('checkout'),
             cwd = d_source.abspath(),
             env = pfi.env)

    return
