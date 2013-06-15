#!/usr/bin/env python

import os
from glob import glob
from orch import deconf, envmunge

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

example_dir = '/'.join(os.path.realpath(__file__).split('/')[:-2] + ['examples'])

def test_envmunge():
    print example_dir
    cfgs = glob('%s/*.cfg'%example_dir)
    print 'Using config files: %s' % str(cfgs)
    suite = deconf.load(cfgs,
                        formatter = deconf.example_formatter)
    pp.pprint(suite)

    groups, packages = envmunge.decompose_grp_pkg(suite)
    assert set(groups.keys()) == set(['gnuprograms','buildtools'])
    
    for grp_name, grp in groups.items():
        needenv = grp.get('environment')
        if needenv:
            env = dict(os.environ)
            oldPATH = env.get('PATH')
            envmunge.add_environment(needenv, env, groups, packages)
            newPATH = env.get('PATH')
            assert len(oldPATH) < len(newPATH)
            print 'Environment set from "%s":' % needenv
            print 'PATH: %s --> %s' % (oldPATH, newPATH)

if '__main__' == __name__:
    test_envmunge()

