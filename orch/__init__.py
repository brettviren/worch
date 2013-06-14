#!/usr/bin/env python
# encoding: utf-8

import os
import deconf
import features



# waf entries
def options(opt):
    opt.add_option('--orch-config', action = 'store', default = 'orch.cfg',
                   help='Give an orchestration configuration file.')
    opt.add_option('--orch-start', action = 'store', default = 'start',
                   help='Set the section to start the orchestration')


def configure(cfg):
    if not cfg.options.orch_config:
        raise RuntimeError, 'No Orchestration configuration file given (--orch-config)'
    if not os.path.exists(cfg.options.orch_config):
        raise ValueError, 'No such file: %s' % cfg.options.orch_config

    extra = dict(cfg.env)

    suite = deconf.load(cfg.options.orch_config, 
                        start = cfg.options.orch_start, 
                        formatter = deconf.extra_formatter,
                        **extra)

    # only care about the leaf packages
    packages = []
    for group in suite['groups']:
        for package in group['packages']:
            packages.append(package)
    cfg.env.orch = packages
    
    from pprint import PrettyPrinter
    pp = PrettyPrinter(indent=2)
    cfg.orch_dump = lambda : pp.pprint({'packages':packages})
    cfg.orch_pkgdata = lambda name, var=None: features.get_pkgdata(cfg.env.orch, name, var)
    return

def build(bld):
    bld.orch_pkgdata = lambda name, var=None: features.get_pkgdata(bld.env.orch, name, var)
