#!/usr/bin/env python
'''
tbb is cantankerous package to build.  This feature should follow
"tarball" or another that provides the "unpacked" step.
'''
from waflib.TaskGen import feature
import orch.features

def configure(cfg):
    orch.features.register_defaults(
        'tbbinst',
        # gratuitious wart _src
        source_archive_file = '{source_unpacked}_src.tgz',
        unpacked_target = 'Makefile',
        # Non standard location to build - must match source unpacked
        build_target = 'crappy-build-system',
        install_target = 'lib/libtbb.so',
    )
    return

def build(bld):
    pass

@feature('tbbinst')
def feature_tbbinst(tgen):

    flag = tgen.make_node(tgen.worch.build_dir).make_node(tgen.worch.build_target)
    build_rule = "(cd src && make cpp0x=1 tbb_release) && touch %s"
    tgen.step('build',
              rule = build_rule % flag.abspath(),
              source = tgen.control_node('unpack'),
              target = flag)

    instdir = tgen.make_node(tgen.worch.install_dir)
    #libdir = tgen.make_node(instdir.abspath() + '/lib')
    instarg = instdir.make_node(tgen.worch.install_target)
    libpath = instarg.parent.abspath()
    #instarg = instdir.find_or_declare(tgen.worch.install_target)
    print 'INSTDIR:', instdir.abspath()
    #print 'LIBDIR:',libdir.abspath()
    print 'INSTARG:', instarg.abspath()
    #libdir = instarg.parent.abspath()
    install_rule = 'mkdir -p %s && cp build/*_release/libtbb* %s/ && cp -a include %s'
    install_rule = install_rule % (libpath, libpath, instdir.abspath())
    tgen.step('install',
              rule = install_rule,
              source = flag,
              target = instarg)

