#!/usr/bin/env python
# encoding: utf-8

top = '.'
out = 'tmp'

def options(opt):
    opt.load('orch', tooldir='.')

def configure(cfg):
    cfg.load('orch', tooldir='.')
    cfg.orch_dump()

def build(bld):
    bld.load('orch', tooldir='.')

    

