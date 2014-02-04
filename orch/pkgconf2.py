#!/usr/bin/env python
'''
Package specific interpretation layered on deconf.
'''
import os
    
import waflib.Logs as msg
from . import deconf2 as deconf
from . import hostinfo
from . import features as featmod
from .util import string2list

def set_derived(node):
    '''
    Put some computed values into the node
    '''
    hd = hostinfo.description()
    for k,v in hd.items():
        node.setdefault(k,v)

    tags = node.get('tags') or ''
    tags = [x.strip() for x in tags.split(',')]
    node.setdefault('tagsdashed',  '-'.join(tags))
    node.setdefault('tagsunderscore', '_'.join(tags))

    version = node.get('version')
    if version:
        node.setdefault('version_2digit', '.'.join(version.split('.')[:2]))
        node.setdefault('version_underscore', version.replace('.','_'))
        node.setdefault('version_dashed', version.replace('.','-'))
        node.setdefault('version_nodots', version.replace('.',''))

    for sysdir in 'control urlfile download patch source'.split():
        node.setdefault('%s_dir' % sysdir, sysdir + 's')
    node.setdefault('install_dir', '{PREFIX}')
    node.setdefault('build_dir', 'builds/{package}-{version}')
    node.setdefault('dest_install_dir', '{install_dir}')

def set_features(node):
    '''
    Put any defaults provided by the node's features.
    '''
    featlist = string2list(node.get('features'))
    featcfg = featmod.defaults(featlist)
    for k, v in featcfg.items():
        node.setdefault(k,v)

def load(cfg, filename, start='start', formatter = None, **kwds):
    top = deconf.load(filename, start=start, formatter=formatter, **kwds)

    package_nodes =  top.owner().oftype('package')
    for node in package_nodes:
        set_derived(node)
        tools = node.get('tools') or ""
        for tool in string2list(tools):
            msg.debug('orch: loading tool: "%s" for package "%s"'  % (tool, node['package']))
            cfg.load(tool)
        set_features(node)
    return top
