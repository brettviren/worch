#!/usr/bin/env python
'''
tbb is cantankerous package to build.  This feature should follow "tarball".
'''
from .pfi import feature

requirements = dict(
    build_dir = 'builds/{source_unpacked}',
    build_target = 'crappy-build-system',
    install_target = 'lib/libtbb.so',
)

@feature('tbbinst', **requirements)
def feature_tbbisnt(info):

    flag = info.build_target.abspath()
    info.task('build',
             rule = "(cd src && make cpp0x=1 tbb_release) && touch %s" % flag,
             source = info.unpacked_target,
             target = info.build_target,)


    install_lib_dir = info.install_target.parent.abspath()
    rule = 'mkdir -p %s && cp build/*_release/libtbb* %s/' % (install_lib_dir,install_lib_dir)
    info.task('install',
             rule = rule,
             source = info.build_target,
             target = info.install_target)

