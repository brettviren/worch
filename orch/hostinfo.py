#!/usr/bin/env python
'''
Some info about the build host
'''

import os
import re
from .util import check_output, CalledProcessError
from . import ups
from . import rootsys

def ncpus():
    'Try to find the number of CPUs on this host'
    try:
        import psutil
        return psutil.NUM_CPUS
    except ImportError:
        pass

    try:
        import multiprocessing
        return multiprocessing.cpu_count()
    except ImportError:
        pass
    except NotImplementedError:
        pass

    if os.path.exists('/proc/cpuinfo'):
        count = 0
        for line in open('/proc/cpuinfo','r').readlines():
            if re.match(r'^processor', line):
                count += 1
        return count

    return 1

def description():
    '''
    Return a dictionary of host description variables.
    '''
    ret = {}
    uname_fields = ['kernelname', 'hostname', 
                    'kernelversion', 'vendorstring', 'machine']
    uname = os.uname()
    for k,v in zip(uname_fields, uname):
        ret[k] = v
    platform = '%(kernelname)s-%(machine)s' % ret
    ret['platform'] = platform
    ret['ups_flavor'] = ups.flavor()
    ret['root_config_arch'] = rootsys.arch()

    bits = '32'
    libbits = 'lib'
    if uname[-1] in ['x86_64']: # fixme: mac os x?
        bits = '64'
        libbits = 'lib64'
    ret['bits'] = bits
    ret['libbits'] = libbits
    ret['gcc_dumpversion'] = check_output(['gcc','-dumpversion']).strip()
    ret['gcc_dumpmachine'] = check_output(['gcc','-dumpmachine']).strip()

    try:
        ma = check_output(
            ['gcc','-print-multiarch'],    # debian-specific
            stderr=open('/dev/null', 'w')
            ).strip()
    except CalledProcessError:
        ma = ""
    ret['gcc_multiarch'] = ma
    if 'darwin' in ret['kernelname'].lower():
        libc_version = ret['kernelversion'] # FIXME: something better on Mac ?
        ret['ld_soname_option'] = 'install_name'
        ret['soext'] = 'dylib'
    else:
        libc_version = check_output(['ldd','--version']).split(b'\n')[0].split()[-1]
        ret['ld_soname_option'] = 'soname'
        ret['soext'] = 'so'
    ret['libc_version'] = libc_version
    ret['NCPUS'] = str(ncpus())
        
    return ret
