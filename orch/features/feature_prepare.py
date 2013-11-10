#!/usr/bin/env python
'''
Features for prepare source code.  

These features all rely on the "unpack" step to have run.  It produces a "prepare" step.
'''


from waflib.TaskGen import feature
import waflib.Logs as msg

from orch.wafutil import exec_command
import orch.features

orch.features.register_defaults(
    'autoconf',
    source_unpacked_path = '{source_dir}/{source_unpacked}',
    prepare_cmd = '{source_unpacked_path}/configure',
    prepare_cmd_std_opts = '--prefix={install_dir}',
    prepare_cmd_options = '',
    prepare_target = 'config.status',
    prepare_target_path = '{build_dir}/{prepare_target}',
)

@feature('autoconf')
def feature_autoconf(tgen):

    cmdstr = tgen.make_node(tgen.worch.prepare_cmd).abspath()
    cmdstr += tgen.worch.format(' {prepare_cmd_std_opts} {prepare_cmd_options}')
    tgen.step('prepare',
              rule = cmdstr,
              #after = tgen.worch.package + '_unpack',
              source = tgen.control_node('unpack'),
              target = tgen.worch.prepare_target_path)
        
orch.features.register_defaults(
    'cmake',
    source_unpacked_path = '{source_dir}/{source_unpacked}',
    prepare_cmd = 'cmake',
    prepare_cmd_std_opts = '{source_dir}/{source_unpacked}/CMakeLists.txt -DCMAKE_INSTALL_PREFIX={install_dir}',
    prepare_cmd_options = '',
    prepare_target = 'config.status',
    prepare_target_path = '{build_dir}/{prepare_target}',
)

@feature('cmake')
def feature_cmake(tgen):
    def prepare(task):
        cmdstr = '{prepare_cmd} {srcdir} {prepare_cmd_std_opts} {prepare_cmd_options}'
        cmd = tgen.worch.format(cmdstr, srcdir=task.inputs[0].parent.abspath())
        return exec_command(task, cmd)

    cmkfile = tgen.make_node(tgen.worch.source_unpacked_path + '/CMakeLists.txt')
    #msg.debug('orch: cmkfile: %s' % cmkfile.abspath())
    tgen.step('prepare',
              rule = prepare,
              source = [cmkfile, 
                        tgen.control_node('unpack')],
              target = tgen.worch.prepare_target_path)
