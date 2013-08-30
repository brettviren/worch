#!/usr/bin/env python
'''

This module provides the decompose() function.

'''
import os
from collections import defaultdict

def parse_val(val, orig = None):
    '''Parse and apply a value setting command: val = <action>:value to
    original value <orig>.  <action> can be "append", "prepend" or
    "set".  If no "<action>:" is given, "set:" is assumed.
    '''
    if val.startswith('append'):
        val = val[len('append'):]
        delim = val[0]
        val = val[1:]
        if not orig: return val
        orig = orig.split(delim)
        while val in orig:
            orig.remove(val)
        return delim.join(orig + [val])

    if val.startswith('prepend'):
        val = val[len('prepend'):]
        delim = val[0]
        val = val[1:]
        if not orig: return val
        orig = orig.split(delim)
        while val in orig:
            orig.remove(val)
        return delim.join([val] + orig)

    if val.startswith('set'):
        val = val[len('set')+1:]
    return val

def split_var_munger_command(cmdstr, cmd):
    rest = cmdstr[len(cmd):]
    return rest[0], rest[1:]

def make_var_munger(cmdstr):

    if cmdstr.startswith('append'):
        delim,val = split_var_munger_command(cmdstr, 'append')
        return lambda oldval: oldval + delim + val if oldval else val
    if cmdstr.startswith('prepend'):
        delim,val = split_var_munger_command(cmdstr, 'prepend')
        return lambda oldval: val + delim + oldval if oldval else val
    if cmdstr.startswith('set'):
        delim,val = split_var_munger_command(cmdstr, 'set')
        return lambda oldval: val
    return lambda oldval: cmdstr

def make_envmungers_from_package(pkg, prefix='export_'):
    ret = defaultdict(list)
    for key, value in pkg.items():
        if not key.startswith(prefix):
            #print ('Skipping key: "%s", not start with "%s"' % (key, prefix))
            continue
        var = key.split('_',1)[1]
        mun = make_var_munger(value)
        ret[var].append(mun)
    return ret

def set_environment(environ, pkg, prefix = 'export_'):
    '''Apply any environment variable settings implied by
    <prefix>_VARIABLE to the <environ> dictionary
    '''
    for k,v in pkg.items():
        if not k.startswith(prefix):
            continue
        var = k.split('_',1)[1]
        old = environ.get(var)
        val = parse_val(v, old)
        environ[var] = val
        #print 'Setting %s=%s (was:%s)' % (var, val, old)
    return

def packages_in_group(pkglist, group_name):
    '''
    Given a list of all packages, return a list of those in the named group.
    '''
    ret = []
    for pkg in pkglist:
        if pkg.get('group') == group_name:
            ret.append(pkg)
    return ret

def resolve_packages(all_packages, desclist):
    '''Resolve packages given a description list.  Each element of the
    list is like <what>:<name> where <what> is "group" or "package"
    and <name> is the group or package name.  The list can be in the
    form of a sequence of descriptors or as a single comma-separated
    string.
    '''
    if not desclist:
        return list()

    if isinstance(desclist, type("")):
        desclist = [x.strip() for x in desclist.split(',')]
    ret = []

    for req in desclist:
        what,name = req.split(':')
        if what == 'package':
            pkg = all_packages[name]
            ret.append(pkg)
            continue
        if what == 'group':
            for pkg in packages_in_group(all_packages.values(), name):
                if pkg in ret:
                    continue
                ret.append(pkg)
        else:
            raise ValueError('Unknown descriptor: "%s:%s"' % (what, name))
        continue
    return ret


def make_environ(pkg, all_packages):
    '''Add an environ to a waf <env> for given package.  The environ
    starts with os.environ, adds any settings specified by
    'export_VARIABLE' in any dependent packages or groups of packages
    indicated by an "environment" package variable and finally by any
    specified by "buildenv_VARIABLE" in the package itself.
    '''
    environ = dict(os.environ)
    for other_pkg in resolve_packages(all_packages, pkg.get('environment')):
        set_environment(environ, other_pkg)
    set_environment(environ, pkg, prefix='buildenv_')
    return environ
        
def collapse_envmungers(mungers):
    ret = defaultdict(list)
    for m in mungers:
        for k,v in m.items():
            ret[k].extend(v)
    return ret

def make_envmungers(pkg, all_packages):
    '''Make a environment munger that will apply the export_VARIABLE
    settings from all dependency packages indicated by the
    "environment" package variable (and the export_VAR from 'depends' packages)
    and any specified by buildenv_VARIABLE in the package itself.
    '''
    mungers = list()
    autoenv = []
    deps = pkg.get('depends') or []
    if isinstance(deps, type("")): deps = deps.split()
    
    for dep in deps:
        _, step = dep.split(':')
        what = step.split('_')[0]
        if what in all_packages:
            autoenv.append('package:%s' % what)
        else: # FIXME: assume this is a group, then.
            autoenv.append('group:%s' % what)

    if pkg.get('environment'):
        en = pkg.get('environment')
        autoenv.extend([x.strip() for x in en.split(',')])
        
    for other_pkg in resolve_packages(all_packages, autoenv):
        new = make_envmungers_from_package(other_pkg)
        mungers.append(new)
        pass

    new = make_envmungers_from_package(pkg, prefix='buildenv_')
    mungers.append(new)

    new = make_envmungers_from_package(pkg, prefix='export_')
    mungers.append(new)

    return collapse_envmungers(mungers)

def apply_envmungers(environ, mungers):
    environ = dict(environ)
    for var,ms in mungers.items():
        val = environ.get(var,'')
        for m in ms:
            val = m(val)
        environ[var] = val
    return environ

def decompose(cfg, suite):
    '''Decompose suite into packages and groups of packages.  

    For every group in the suite there is one added to the waf <cfg> context.  

    Every package has an env of the same name added to <cfg> which
    contains variables defined either through its "environment"
    variable or through any variables with names beginning with
    "buildenv_".

    '''
    base_env = cfg.env

    # fixme: should use ordered dict
    gl,gd = [], {}
    pl,pd = [], {}
    for group in suite['groups']:
        group_name = group['group']
        gl.append(group_name)
        gd[group_name] = group
        for package in group['packages']:
            package_name = package['package']
            pl.append(package_name)
            pd[package_name] = package

    base_env.orch_group_list = gl
    base_env.orch_group_dict = gd
    base_env.orch_package_list = pl
    base_env.orch_package_dict = pd

    for pkg_name, pkg in pd.items():
        new_env = base_env.derive()
        mungers = make_envmungers(pkg, pd)
        new_env.munged_env = apply_envmungers(os.environ, mungers)
        cfg.setenv(pkg_name, new_env)

    return

