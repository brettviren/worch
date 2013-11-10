#!/usr/bin/env python
'''
Pythia6 doesn't have it's own build system so this feature ("pythiainst") provides it.  

It follows "tarball" and provides "prepare", "build", "install" and some intermediates.

Note: this feature is written in an overly verbose manner....
'''

from waflib.TaskGen import feature
import waflib.Logs as msg

import orch.features
orch.features.register_defaults(
    'pythiainst', 
    source_unpacked ='pythia6',
    unpacked_target = 'pythia6416.f',
    source_unpacked_path = '{source_dir}/{source_unpacked}',
    build_target = 'libPythia6.so',
    build_target_path = '{build_dir}/{build_target}',
    install_target = 'lib/libPythia6.so',
    install_target_path = '{install_dir}/{install_target}',
)
    

@feature('pythiainst')
def feature_pythiainst(tgen):
    build_dir = tgen.make_node(tgen.worch.build_dir)
    f1 = build_dir.make_node('pythia6416.f')
    f2 = build_dir.make_node('tpythia6_called_from_cc.F')
    c1 = build_dir.make_node('main.c')
    c2 = build_dir.make_node('pythia6_common_address.c')

    fo1 = build_dir.make_node('pythia6416.o')
    fo2 = build_dir.make_node('tpythia6_called_from_cc.o')
    co1 = build_dir.make_node('main.o')
    co2 = build_dir.make_node('pythia6_common_address.o')

    tgen.step('prepare',
              rule = "cp %s/* ." % tgen.make_node(tgen.worch.source_unpacked_path).abspath(),
              source = tgen.control_node('unpack'),
              target = [f1,f2,c2],
              cwd = tgen.worch.build_dir)

    tgen.step('genmain',
              rule = "echo 'void MAIN__() {}' > main.c",
              source = f1,
              target = c1,
              cwd = tgen.worch.build_dir)
    
    tgen.step('buildc1',
              rule = 'gcc -c -fPIC %s' % c1,
              source = c1,
              target = co1,
              cwd = tgen.worch.build_dir)

    tgen.step('buildc2',
              rule = 'gcc -c -fPIC %s' % c2,
              source = c2,
              target = co2,
              cwd = tgen.worch.build_dir)

    tgen.step('buildf1',
              rule = 'gfortran -c -fPIC %s' % f1,
              source = f1,
              target = fo1,
              cwd = tgen.worch.build_dir)

    tgen.step('buildf2',
              rule = 'gfortran -c -fPIC -fno-second-underscore %s' % f2,
              source = f2,
              target = fo2,
              cwd = tgen.worch.build_dir)

    tgen.step('build',
              rule = 'gfortran -shared -Wl,-soname,libPythia6.so -o %s main.o pythia*.o tpythia*.o' % tgen.worch.build_target,
              source = [co1, co2, fo1, fo2],
              target = tgen.worch.build_target_path,
              cwd = tgen.worch.build_dir)

    inst = tgen.make_node(tgen.worch.install_target_path)
    inst.parent.mkdir()
    msg.debug('orch: install_target_path = %s' % inst.abspath())

    tgen.step('install',
              rule = 'cp %s %s' % (tgen.worch.build_target, inst.abspath()),
              source = tgen.worch.build_target_path,
              target = inst,
              cwd = tgen.worch.build_dir)

