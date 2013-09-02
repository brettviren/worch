#!/usr/bin/env python
from waflib import TaskGen
from .pfi import PackageFeatureInfo

from orch.util import exec_command

requirements = {
    'source_dir': 'sources',
    'source_unpacked': '{package}-{version}',
    # fixme: the prepare_script should typically match something that
    # provides the source directory, eg, unpacked_target from
    # tarball_requirements.  Best to make these the same keywords to
    # make it clear.  Currently, if the package isn't truly autoconf
    # one needs to change this "configure" value in two places.
    'prepare_script': 'configure',
    'prepare_script_options': '--prefix={install_dir}',
    'prepare_target': 'config.status',
    'build_dir': 'builds/{package}-{version}',
    'build_cmd': 'make',
    'build_cmd_options': None,
    'build_target': None,
    'install_dir': '{PREFIX}',
    'install_cmd': 'make install',
    'install_cmd_options': None,
    'install_target': None,
}

@TaskGen.feature('autoconf')
def feature_autoconf(self):
    pfi = PackageFeatureInfo(self.package_name, 'autoconf', self.bld, requirements)

    d_source = pfi.get_node('source_dir')
    d_unpacked = pfi.get_node('source_unpacked', d_source)
    f_prepare = pfi.get_node('prepare_script',d_unpacked)
    d_build = pfi.get_node('build_dir')
    f_prepare_result = pfi.get_node('prepare_target', d_build)
    f_build_result = pfi.get_node('build_target', d_build)

    d_prefix = pfi.get_node('install_dir')
    f_install_result = pfi.get_node('install_target', d_prefix)

    def prepare_task(task):
        src = task.inputs[0]
        tgt = task.outputs[0]
        
        cmd = "%s %s" % (src.abspath(), pfi.get_var('prepare_script_options'))
        return exec_command(task, cmd)
        
        
    self.bld(name = pfi.format('{package}_prepare'),
             rule = prepare_task,
             source = f_prepare,
             target = f_prepare_result,
             cwd = d_build.abspath(),
             depends_on = pfi.get_deps('prepare'),
             env = pfi.env)

    def build_task(task):
        src = task.inputs[0]
        tgt = task.outputs[0]
        cmd = "%s %s" % (
                 pfi.get_var('build_cmd'),
                 pfi.get_var('build_cmd_options') or '',
            )
        return exec_command(task, cmd)
        
    self.bld(name = pfi.format('{package}_build'),
             rule = build_task,
             source = f_prepare_result,
             target = f_build_result,
             cwd = d_build.abspath(),
             depends_on = pfi.get_deps('build'),
             env = pfi.env)

    def install_task(task):
        src = task.inputs[0]
        tgt = task.outputs[0]
        cmd = "%s %s" % (
                 pfi.get_var('install_cmd'),
                 pfi.get_var('install_cmd_options') or '',
            )
        return exec_command(task, cmd)
        
    self.bld(name = pfi.format('{package}_install'),
             rule = install_task,
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


