#!/usr/bin/env python
# encoding: utf-8

top = '.'
out = 'tmp'

def options(opt):
    opt.load('orch', tooldir='.')
    opt.add_option('--dot', action = 'store', default = None,
                   help = 'Produce a dot file of given name with dependency graph')

def configure(cfg):
    cfg.load('orch', tooldir='.')
    cfg.orch_dump()

def dot(ctx):
    import orch.dot as odot
    import sys
    bld = ctx.exec_dict['bld']
    #print 'TG:\n', '\n'.join([tg.name for tg in bld.get_all_task_gen()])
    odot.write(bld, ctx.options.dot)
    #print 'Wrote %s' % ctx.options.dot
    sys.exit(0)

def build(bld):
    bld.load('orch', tooldir='.')
    if bld.options.dot:
        # needs to be a pre-fun, not a post-fun
        bld.add_pre_fun(dot)
        #bld.add_post_fun(dot)

