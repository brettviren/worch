#!/usr/bin/env python
'''
Package specific interpretation layered on deconf.
'''
import os
    
from . import deconf2 as deconf
from . import hostinfo
from . import features as featmod
from .util import string2list

def set_derived(node):
    '''
    Put some computed values into the node
    '''
    # we subvert the read-only'ness
    items = node._items

    hd = hostinfo.description()
    for k,v in hd.items():
        items.setdefault(k,v)

    tags = node.get('tags') or ''
    tags = [x.strip() for x in tags.split(',')]
    items.setdefault('tagsdashed',  '-'.join(tags))
    items.setdefault('tagsunderscore', '_'.join(tags))

    version = node.get('version')
    if version:
        items.setdefault('version_2digit', '.'.join(version.split('.')[:2]))
        items.setdefault('version_underscore', version.replace('.','_'))
        items.setdefault('version_dashed', version.replace('.','-'))
        items.setdefault('version_nodots', version.replace('.',''))

    for sysdir in 'control urlfile download patch source'.split():
        items.setdefault('%s_dir' % sysdir, sysdir + 's')
    items.setdefault('install_dir', '{PREFIX}')
    items.setdefault('build_dir', 'builds/{package}-{version}')
    items.setdefault('dest_install_dir', '{install_dir}')

def set_features(node):
    '''
    Put any defaults provided by the node's features.
    '''
    # we subvert the read-only'ness
    items = node._items

    featlist = string2list(node.get('features'))
    featcfg = featmod.defaults(featlist)
    for k, v in featcfg.items():
        items.setdefault(k,v)

def load(filename, start='start', formatter = None, **kwds):
    top = deconf.load(filename, start=start, formatter=formatter, **kwds)
    for node in  top.owner().oftype('package'):
        set_derived(node)
        set_features(node)
    return top
