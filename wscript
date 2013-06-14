#!/usr/bin/env python
# encoding: utf-8

top = '.'
out = 'tmp'


def options(opt):
    opt.load('orch', tooldir='.')

def configure(cfg):
    cfg.load('orch', tooldir='.')
    cfg.orch_dump()
    #cfg.recurse('hello')

def build(bld):
    print 'build command: "%s": %s' % (bld.cmd, bld.root.make_node('foo/bar').abspath())
    bld.recurse('hello bc')

