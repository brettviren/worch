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

def build(bld):
    bld.load('orch', tooldir='.')
    if bld.options.dot:
        from orch import dot
        dot.write(bld, bld.options.dot)
        print 'Wrote %s' % bld.options.dot
