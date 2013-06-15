#!/usr/bin/env python
# encoding: utf-8

import os
from glob import glob
import deconf
import features
import envmunge

# waf entries
def options(opt):
    opt.add_option('--orch-config', action = 'store', default = 'orch.cfg',
                   help='Give an orchestration configuration file.')
    opt.add_option('--orch-start', action = 'store', default = 'start',
                   help='Set the section to start the orchestration')


def bind_functions(ctx):
    from pprint import PrettyPrinter
    pp = PrettyPrinter(indent=2)
    ctx.orch_dump = lambda : pp.pprint({'packages': ctx.env.orch_packages.keys(),
                                        'groups': ctx.env.orch_groups.keys()})
    ctx.orch_pkgdata = lambda name, var=None: \
                       features.get_pkgdata(ctx.env.orch_packages, name, var)

def configure(cfg):
    if not cfg.options.orch_config:
        raise RuntimeError, 'No Orchestration configuration file given (--orch-config)'
    orch_config = glob(cfg.options.orch_config)

    extra = dict(cfg.env)

    suite = deconf.load(orch_config, start = cfg.options.orch_start, 
                        formatter = deconf.extra_formatter, **extra)

    envmunge.decompose(cfg, suite)

    print 'Configure envs:', cfg.all_envs

    bind_functions(cfg)
    return

def build(bld):
    from waflib.Build import POST_BOTH
    bld.post_mode = POST_BOTH 

    bind_functions(bld)

    for grpname in bld.env.orch_group_list:
        print 'Adding group: "%s"' 
        bld.add_group(grpname)

    print 'Build envs:',bld.all_envs

    to_recurse = []
    for pkgname, pkgdata in bld.env.orch_packages.items():
        if os.path.exists('%s/wscript' % pkgname):
            to_recurse.append(pkgname)
            continue
        feat = pkgdata.get('features')
        bld(features = feat, package_name = pkgname)
    if to_recurse:
        bld.recurse(to_recurse)

