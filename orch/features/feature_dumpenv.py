#!/usr/bin/env python

from .pfi import feature

@feature('dumpenv')
def feature_dumpenv(info):
    '''
    Dump the environment
    '''
    info.ctx(name = info.format('{package}_dumpenv'),
             rule = "env | sort",
             env = info.env)
