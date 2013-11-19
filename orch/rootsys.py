#!/usr/bin/env python
'''
Reproduce some root.cern.ch stuff
'''
import os
import re

arch_desc = [
    ("aix*", "aix5"),
    ("osf1.*:alpha:.*", "alphacxx6"),
    ("freebsd.*:.*:[789].*", "freebsd7"),
    ("freebsd.*:.*:6.*", "freebsd5"),
    ("freebsd.*:.*:5.*", "freebsd5"),
    ("freebsd.*:.*:4.*", "freebsd4"),
    ("freebsd.*:.*:.*", "freebsd"),
    ("hp-ux:ia64:.*", "hpuxia64acc"),
    ("hp-ux:.*:.*", "hpuxacc"),
    ("hurd.*:.*:.*", "hurddeb"),
    ("linux:ia64:.*", "linuxia64gcc"),
    ("linux:x86_64:.*", "linuxx8664gcc"),
    ("linux:alpha:.*", "linuxalphagcc"),
    ("linux:arm.*:.*", "linuxarm"),
    ("linux:hppa.*:.*", "linux"),
    ("linux:mips:.*", "linuxmips"),
    ("linux:sparc.*:.*", "linux"),
    ("linux:parisc.*:.*", "linuxhppa"),
    ("linux:ppc64.*:.*", "linuxppc64gcc"),
    ("linux:ppc.*:.*", "linuxppcgcc"),
    ("linux:i.*86:.*", "linux"),
    ("linux:s39.*:.*", "linux"),
    ("openbsd.*:.*:.*", "openbsd"),
    ("lynx:.*:.*", "lynxos"),
    ("darwin:power.*:.*", "macosx"),
    ("darwin:.*86.*:.*", "macosx"),
    ("irix.*:sgi.*:.*", "sgicc"),
    ("sunos:sun.*:6.*", "solarisCC5"),
    ("sunos:sun.*:5.*", "solarisCC5"),
    ("sunos:sun.*:4.*", "solaris"),
    ("sunos:i86pc:5.*", "solarisCC5"),
    ("cygwin_.*:.*86:.*", "win32"),
    ("cygwin_.*:pentium:.*", "win32"),
    ("cygwin_.*:ia64", "win32"),
    ("mingw32_.*:.*86:.*", "win32"),
    ]

def arch(uname = None):
    '''
    Should match the output of "root-config --arch"
    '''
    if not uname:
        uname = os.uname()
    arch = uname[0].lower()
    rele = uname[2].lower()
    chip = uname[4].lower()
    acr = '%s:%s:%s' % (arch,chip,rele)
    for check,answer in arch_desc:
        if re.search(check, acr):
            return answer
        #print 'Failed: "%s" <--> "%s".  Not yours: "%s"' % (check, acr, answer)
    return None


