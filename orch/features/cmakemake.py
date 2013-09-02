#!/usr/bin/env python
from waflib import TaskGen
from .pfi import PackageFeatureInfo

from orch.util import exec_command

requirements = {
    'source_dir': 'sources',
    'source_unpacked': '{package}-{version}',
    'unpacked_target': 'CMakeLists.txt',
    'prepare_cmd': '/bin/env && cmake ../../{source_dir}/{source_unpacked} -DCMAKE_INSTALL_PREFIX={install_dir}',
    'prepare_cmd_options': '',
    'prepare_target': 'CMakeCache.txt',
    'build_dir': 'builds/{package}-{version}',
    'build_cmd': 'make',
    'build_cmd_options': None,
    'build_target': None,
    'install_dir': '{PREFIX}',
    'install_cmd': 'make install',
    'install_cmd_options': None,
    'install_target': None,
}

@TaskGen.feature('cmakemake')
def feature_cmakemake(self):
    pfi = PackageFeatureInfo(self.package_name, 'cmakemake', self.bld, requirements)

    d_source = pfi.get_node('source_dir')
    d_unpacked = pfi.get_node('source_unpacked', d_source)
    f_unpack_target = pfi.get_node('unpacked_target',d_unpacked)

    d_build = pfi.get_node('build_dir')
    f_prepare_result = pfi.get_node('prepare_target', d_build)
    f_build_result = pfi.get_node('build_target', d_build)

    d_prefix = pfi.get_node('install_dir')
    f_install_result = pfi.get_node('install_target', d_prefix)

    def prepare_task(task):
        cmd = "%s %s" % (pfi.get_var('prepare_cmd'), pfi.get_var('prepare_cmd_options') or '')
        return exec_command(task, cmd)
        
    self.bld(name = pfi.format('{package}_prepare'),
             rule = prepare_task,
             source = f_unpack_target,
             target = f_prepare_result,
             cwd = d_build.abspath(),
             depends_on = pfi.get_deps('prepare'),
             env = pfi.env)

    # fixme: this is copy-and-paste from feature_autoconf().  Need more DRY!

    def build_task(task):
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

    return

