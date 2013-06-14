#!/usr/bin/env python
# encoding: utf-8

import os
import deconf
import features



# waf entries
def options(opt):
    opt.add_option('--orch-config', action = 'store', default = 'orch.cfg',
                   help='Give an orchestration configuration file.')
    opt.add_option('--orch-suite', action = 'store',
                   help='Set the suite to orchestrate')
    opt.add_option('--orch-start', action = 'store', default = 'start',
                   help='Set the suite to orchestrate')


def configure(cfg):
    if not cfg.options.orch_config:
        raise RuntimeError, 'No Orchestration configuration file given (--orch-config)'
    if not os.path.exists(cfg.options.orch_config):
        raise ValueError, 'No such file: %s' % cfg.options.orch_config

    extra = dict(cfg.env)
    if cfg.options.orch_suite:
        extra['suite'] = cfg.options.orch_suite

    suite = deconf.load(cfg.options.orch_config, 
                        start = cfg.options.orch_start, 
                        formatter = deconf.extra_formatter,
                        **extra)

    # only care about the leaf packages
    packages = suite['suite'][0]['packages']
    cfg.env.orch = packages
    
    from pprint import PrettyPrinter
    pp = PrettyPrinter(indent=2)
    cfg.orch_dump = lambda : pp.pprint({'packages':packages})

    return
