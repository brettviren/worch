#!/usr/bin/env python
# encoding: utf-8

import sys
import waflib.Logs as msg

top = '.'
out = 'tmp'

def options(opt):
    opt.load('orch.tools', tooldir='.')

    opt.add_option('--dot', action = 'store', default = None,
                   help = 'Produce a dot file of given name with dependency graph')
    opt.add_option('--dump-suite', action = 'store_true', default = False,
                   help = 'Dump the processed suite configuration data')

def configure(cfg):
    cfg.load('orch.tools', tooldir='.')


def dot(ctx):
    import orch.dot as odot
    bld = ctx.exec_dict['bld']
    #print 'TG:\n', '\n'.join([tg.name for tg in bld.get_all_task_gen()])
    odot.write(bld, ctx.options.dot)
    msg.info('orch: Wrote %s' % ctx.options.dot)
    sys.exit(0)

def dump(ctx):
    bld = ctx.exec_dict['bld']
    suite = bld.env.orch_package_dict
    from pprint import PrettyPrinter
    pp = PrettyPrinter(indent=2)
    pp.pprint(suite)
    sys.exit(0)

def build(bld):
    bld.load('orch.tools', tooldir='.')
    if bld.options.dot:
        # needs to be a pre-fun, not a post-fun
        bld.add_pre_fun(dot)
        #bld.add_post_fun(dot)
    if bld.options.dump_suite:
        bld.add_pre_fun(dump)
