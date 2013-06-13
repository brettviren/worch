#!/usr/bin/env python
# encoding: utf-8

top = '.'
out = 'tmp'

def configure(cfg):
    cfg.recurse('bc')

def build(bld):
    bld.recurse('bc')
