#!/usr/bin/env python

def ncpus():
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

def host_description():
    '''
    Return a dictionary of host description variables.
    '''
    import os
    from orch import ups
    from subprocess import check_output, CalledProcessError
    from orch import rootsys

    ret = {}
    uname_fields = ['kernelname', 'hostname', 
                    'kernelversion', 'vendorstring', 'machine']
    uname = os.uname()
    for k,v in zip(uname_fields, uname):
        ret[k] = v
    platform = '{kernelname}-{machine}'.format(**ret)
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
    else:
        libc_version = check_output(['ldd','--version']).split(b'\n')[0].split()[-1]
    ret['libc_version'] = libc_version
    ret['NCPUS'] = str(ncpus())
        
    return ret
def test_pkgconf_host_description():
    hd = host_description()
    print hd

if '__main__' == __name__:
    test_pkgconf_host_description()
