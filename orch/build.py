#!/usr/bin/env python
'''
The worch build tool for waf.  

This calls the build context on every package in configured list of orch groups.  

All worch feature methods are expected to be imported already.

FIXME: recursion to external wscript files has been removed.
'''

import waflib.Logs as msg
from waflib.TaskGen import feats as available_features
from . import util, wafutil


def build(bld):
    msg.debug ('orch: BUILD CALLED')

    bld.load(bld.env.orch_extra_tools)

    # batteries-included
    from . import features
    features.load()

    msg.debug('orch: available features: %s' % (', '.join(sorted(available_features.keys())), ))

    msg.info('Supported waf features: "%s"' % '", "'.join(sorted(available_features.keys())))
    msg.debug('orch: Build envs: %s' % ', '.join(sorted(bld.all_envs.keys())))

    tobuild = bld.env.orch_group_packages
    print 'TOBUILD',tobuild
    for grpname, pkgnames in tobuild:
        msg.debug('orch: Adding group: "%s"' % grpname)
        bld.add_group(grpname)
        
        for pkgname in pkgnames:
            bld.worch_package(pkgname)

    bld.add_pre_fun(pre_process)
    bld.add_post_fun(post_process)
    msg.debug ('orch: BUILD CALLED [done]')

def pre_process(bld):
    msg.debug('orch: PREPROCESS')
def post_process(bld):
    msg.debug('orch: POSTPROCESS')
