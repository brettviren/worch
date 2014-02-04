#!/usr/bin/env python
'''

This module primarily provides the decompose() function.

'''

from . import mungers
from .util import string2list
import waflib.Logs as msg

def packages_in_group(pkglist, group_name):
    '''
    Given a list of all packages, return a list of those in the named group.
    '''
    ret = []
    for pkg in pkglist:
        if pkg.get('group') == group_name:
            ret.append(pkg)
    return ret

def resolve_packages(nodedict, desclist):
    '''Resolve packages given a description list.  Each element of the
    list is like <what>:<name> where <what> is "group" or "package"
    and <name> is the group or package name.  The list can be in the
    form of a sequence of descriptors or as a single comma-separated
    string.
    '''

    if not desclist:
        return list()

    if isinstance(desclist, type("")):
        desclist = string2list(desclist)
    ret = []

    for req in desclist:
        what,name = req.split(':')
        if what == 'package':
            pkg = nodedict[name]
            ret.append(pkg)
            continue
        if what == 'group':
            for pkg in packages_in_group(nodedict.values(), name):
                if pkg in ret:
                    continue
                ret.append(pkg)
        else:
            raise ValueError('Unknown descriptor: "%s:%s"' % (what, name))
        continue
    return ret

        
def make_envmungers(node):
    '''Make a environment munger that will apply the export_VARIABLE
    settings from all dependency packages indicated by the
    "environment" package variable (and the export_VAR from 'depends'
    packages) and any specified by buildenv_VARIABLE in the package
    itself.  Note, that the export_* variables from a given package
    are explicitly NOT applied to the package itself.
    '''
    autoenv = []
    deps = node.get('depends') or []
    if isinstance(deps, type("")): 
        deps = string2list(deps)
    
    # cmp() on nodes may be slower than using names
    all_packages = node.owner().oftype('package')
    all_groups = node.owner().oftype('group')

    for dep in deps:
        print 'DEP "%s"' % dep
        _, step = dep.split(':')
        what = step.split('_')[0]
        if what in all_packages:
            #print 'autoenv: package: "%s"' % what
            autoenv.append('package:%s' % what)
        if what in all_groups:
            #print 'autoenv: group: "%s"' % what
            autoenv.append('group:%s' % what)

    en = node.get('environment')
    if en:
        autoenv.extend(string2list(en))
        
    ret = list()
    for other in resolve_packages(node.owner().nodes(), autoenv):
        ret += mungers.construct('export_', **other)

    ret += mungers.construct('buildenv_', **node)

    # Do NOT append export_ mungers for the current pkg.

    return ret

def decompose(cfg, suite):
    '''Decompose suite into packages and groups of packages.  

    For every group in the suite there is one added to the waf <cfg> context.  

    Every package has an env of the same name added to <cfg> which
    contains variables defined either through its "environment"
    variable or through any variables with names beginning with
    "buildenv_".

    The waf env is given a "munged_env" element which holds the result
    of any environment munging applied to the current process
    environment (os.environ).
    '''
    base_env = cfg.env

    for node in suite.owner().oftype('package'):

        mlist = make_envmungers(node)
        environ = cfg.env.env or dict()
        menv = mungers.apply(mlist, **environ)

        new_env = base_env.derive()
        new_env.munged_env = menv
        cfg.setenv(node._name, new_env)
        
        msg.debug("orchenv: Set waf env for %s" % node._name)
    return

