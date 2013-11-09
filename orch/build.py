#!/usr/bin/env python
'''
The worch build tool for waf.  

This calls the build context on every package in configured list of orch groups.  

All worch feature methods are expected to be imported already.

FIXME: recursion to external wscript files has been removed.
'''

import waflib.Logs as msg
from waflib.TaskGen import feats as available_features
from . import util


def build(bld):
    msg.debug ('orch: BUILD CALLED')

    from . import features
    features.load()
    
    msg.info('Supported waf features: "%s"' % '", "'.join(sorted(available_features.keys())))
    msg.debug('orch: Build envs: %s' % ', '.join(sorted(bld.all_envs.keys())))

    for grpname in bld.env.orch_group_list:

        msg.debug('orch: Adding group: "%s"' % grpname)
        bld.add_group(grpname)

        group = bld.env.orch_group_dict[grpname]
        for package in group['packages']:
            pkgname = package['package']

            pkgcfg = bld.env.orch_package_dict[pkgname]
            featlist = util.string2list(pkgcfg.get('features'))
            msg.debug('orch: features for %s: "%s"' % (pkgname, '", "'.join(featlist)))
            #for feat in featlist:
            #    assert feat in available_features.keys(), 'Unknown feature: "%s"' % feat
            bld.worch_package(pkgcfg)

    msg.debug ('orch: BUILD CALLED [done]')

