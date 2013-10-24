#!/usr/bin/env python
'''
buildenv_VAR = set:VALUE
buildenv_00 = command:source setup && setup hello
'''

import os
import subprocess
import tempfile

def split_var_munger_command(cmdstr, cmd):
    rest = cmdstr[len(cmd):]
    return rest[0], rest[1:]


def update_var(name, cmdstr, **environ):
    oldval = environ.get(name)
    if cmdstr.startswith('append'):
        delim,val = split_var_munger_command(cmdstr, 'append')
        newval = oldval + delim + val if oldval else val
    elif cmdstr.startswith('prepend'):
        delim,val = split_var_munger_command(cmdstr, 'prepend')
        newval = val + delim + oldval if oldval else val
    elif cmdstr.startswith('set'):
        delim,val = split_var_munger_command(cmdstr, 'set')
        newval = val
    else: 
        newval = cmdstr
    environ[name] = newval
    return environ
            

def cmd_munger(cmd, **environ):

    fd, fname = tempfile.mkstemp()
    cmd += ' && env > %s' % fname
    subprocess.check_output(cmd, shell=True, env=environ)
    os.close(fd)
    envvars = open(fname).read().split('\n')
    ret = dict()
    for line in envvars:
        line = line.strip()
        if not line: 
            continue
        k,v = line.split('=',1)
        ret[k.strip()] = v.strip()
    return ret

def make_munger(name, cmdstr):
    if cmdstr.startswith('shell'):
        delim, cmdline = split_var_munger_command(cmdstr, 'shell')
        return lambda **environ: cmd_munger(cmdline, **environ)
    return lambda **environ: update_var(name, cmdstr, **environ)

def produce_mungers(prefix, **kwds):
    ret = list()
    for key, cmdstr in kwds.items():
        if not key.startswith(prefix):
            continue
        name = key[len(prefix):]
        m = make_munger(name, cmdstr)
        ret.append(m)
    return ret

def apply_mungers(mungers, **environ):
    for m in mungers:
        environ = m(**environ)
    return environ
        
if '__main__' == __name__:
    environ = dict(FOO='bar', BAZ='quax')
    cfgitems = dict(buildenv_FOO = 'set:bzzz',
                    buildenv_00 = 'shell:export BAZ=BAR')
    mungers = produce_mungers('buildenv_', **cfgitems)
    new_environ = apply_mungers(mungers, **environ)
    print new_environ
