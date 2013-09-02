#!/usr/bin/env python
from waflib import TaskGen
from .pfi import PackageFeatureInfo

@TaskGen.feature('dumpenv')
def feature_dumpenv(self):
    '''
    Dump the environment
    '''
    pfi = PackageFeatureInfo(self.package_name, 'dumpenv', self.bld, dict())

    self.bld(name = pfi.format('{package}_dumpenv'),
             rule = "/bin/env | sort",
             env = pfi.env)
