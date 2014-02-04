#!/usr/bin/env python
# encoding: utf-8

top = '.'
out = 'tmp'

import time

def options(opt):
    t1 = time.time()
    opt.load('orchlib', tooldir='.')
    print 'Load orchlib options in %.03f seconds' % (time.time()-t1)

def configure(cfg):
    t1 = time.time()
    cfg.load('orchlib', tooldir='.')
    print 'Load orchlib configure in %.03f seconds' % (time.time()-t1)

def build(bld):
    t1 = time.time()
    bld.load('orchlib', tooldir='.')
    print 'Load orchlib build in %.03f seconds' % (time.time()-t1)
