#!/usr/bin/env python

import os
from glob import glob
import sys
sys.path.insert(0, '/'.join(os.path.realpath(__file__).split('/')[:-2] + ['orch']))
import deconf, envmunge

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

example_dir = '/'.join(os.path.realpath(__file__).split('/')[:-2] + ['examples'])


class FakeEnv:
    def __init__(self, **kwds):
        self.__dict__.update(**kwds)
    def __setattr__(self, name, value):
        self.__dict__[name] = value
    def derive(self):
        return FakeEnv(**self.__dict__)
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)

class FakeCfg:
    def __init__(self):
        self.env = FakeEnv()
    def setenv(self, name, value):
        self.__dict__[name] = value
    def __str__(self):
        return (self.__dict__)

def test_envmunge():
    print example_dir
    cfgs = glob('%s/*.cfg'%example_dir)
    print 'Using config files: %s' % str(cfgs)
    suite = deconf.load(cfgs,
                        formatter = deconf.example_formatter)
    pp.pprint(suite)

    cfg = FakeCfg()
    envmunge.decompose(cfg, suite)
    pp.pprint(cfg.env.__dict__)

def test_envmunger():
    print example_dir
    cfgs = glob('%s/test_envmunge.cfg'%example_dir)
    print 'Using config files: %s' % str(cfgs)
    suite = deconf.load(cfgs,
                        formatter = deconf.example_formatter)
    pp.pprint(suite)

    cfg = FakeCfg()
    envmunge.decompose(cfg, suite)
    newenv = cfg.env.envmunger(os.environ)
    for var,newv in sorted(newenv.items()):
        oldv = os.environ.get(var,'')
        if newv == oldv:
            continue
        print '%s: "%s" --> "%s"' % (var, oldv, newv)
    

def test_export():
    'Test the export_ mechanism'
    suite = deconf.load(os.path.join(example_dir, 'test_envmunge.cfg'),
                        formatter = deconf.example_formatter)
    cfg = FakeCfg()
    envmunge.decompose(cfg, suite)
    for pkg,env in cfg.__dict__.items():
        if pkg == 'env': continue
        me = env.__dict__['munged_env']
        for var in ['PATH','ENVMUNGE','GROUP','PACKAGE']:
            print 'PKGENV:', pkg, var, me.get(var,"(not set)")



if '__main__' == __name__:
#    test_envmunger()
    test_export()
