#!/usr/bin/env python
'''
Test orch.rootsys
'''

import common
from orch import rootsys

# arch:chip:release
# uname -X with X in s:m:r

trial_arch_machine_release = [
    ("linux:x86_64:2.6.32-358.6.2.el6.x86_64", "linuxx8664gcc"),
    ("linux:i686:3.2.0-4-rt-686-pae","linux"),
]
def test_arch():
    for have, want in trial_arch_machine_release:
        a,m,r = have.split(":")
        fake_uname = [a, None, r, None, m]
        got = rootsys.arch(fake_uname)
        assert want == got, 'Wanted "%s" but got "%s" with "%s"' % (want,got, fake_uname)
        print ('match: %s from %s' % (got, fake_uname))


def test_my_arch():
    print ('This hosts ROOT arch:', rootsys.arch())

if '__main__' == __name__:
    test_arch()
    test_my_arch()
