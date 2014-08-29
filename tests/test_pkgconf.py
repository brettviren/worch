#!/usr/bin/env python

import common

from orch.hostinfo import description as host_description

def test_pkgconf_host_description():
    hd = host_description()
    print (hd)

if '__main__' == __name__:
    test_pkgconf_host_description()
