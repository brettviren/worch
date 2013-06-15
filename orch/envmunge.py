#!/usr/bin/env python
'''

This module provides the decompose() function.

'''
import os

def parse_val(val, orig = None):
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
        val = val[len('set')+1]
    return val

def set_environment(dst, data):
    for k,v in data.items():
        if not k.startswith('export_'):
            continue
        var = k.split('_',1)[1]
        old = dst.get(var)
        val = parse_val(v, old)
        dst[var] = val
        #print 'Setting %s=%s (was:%s)' % (var, val, old)

def add_environment(src, dst, groups, packages):
    for want in [x.strip() for x in src.split(',')]:
        typ,nam = want.split(':')
        if typ == 'group':
            for pkg in groups[nam]['packages']:
                set_environment(dst, pkg)
        if typ == 'package':
            set_environment(dst, packages[nam])


def decompose_grp_pkg(suite):
    '''Return tuple of(groups, packages) that make up the suite.  Each
    element is a dictionary indexed by name.    '''
    
    packages = {}
    groups = {}
    for group in suite['groups']:
        groups[group['group']] = group
        for package in group['packages']:
            packages[package['package']] = package
    return groups, packages


def decompose(cfg, suite):
    '''Decompose suite into packages and groups of packages.  Each group
    name is used to define a new env for the cfg.  All envs will have
    a orch_groups and orch_packages dictionaries set which hold the
    entirety the groups and packages from the suite.
    '''
    base_env = cfg.env
    groups, packages = decompose_grp_pkg(suite)
    for grp_name, grp in groups.items():
        cfg.setenv(grp_name, base_env.derive())
        cfg.env.env = dict(os.environ)
        needenv = grp.get('environment')
        if not needenv: 
            continue
        add_environment(needenv, cfg.env.env, groups, packages)

    base_env.orch_group_list = [x['group'] for x in suite['groups']]
    base_env.orch_groups = groups
    base_env.orch_packages = packages
    return
