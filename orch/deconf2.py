#!/usr/bin/env python

import re
import os

def to_list(lst, delims = ', '):
    'Split a string into to a list according to delimiters.'
    ret = []
    for x in re.compile('[%s]' % delims).split(lst):
        x = x.strip()
        if x is '': continue
        ret.append(x)
    return ret

def find_file(fname, paths):
    '''Return real path if file <fname> is found in list of paths, or raise IOError'''
    for check in paths:
        maybe = os.path.join(check, fname)
        if os.path.exists(maybe):
            return os.path.realpath(maybe)
    raise IOError('No such file: "%s" searched: %s' % (fname, ':'.join(paths)))
        
def get_deconf_include_paths():
    'Return list of directories defined via DECONF_INCLUDE_PATH'
    return os.environ.get('DECONF_INCLUDE_PATH','').split(':')

def get_used_include_paths(cfg):
    'Return a list of directories holding already parsed files'
    ret = map(os.path.dirname, getattr(cfg,'files',list()))
    return ret

def get_include_paths(cfg):
    'Return a list of absolute paths to check for any includes'
    ret, rel = [], ['.'] + get_used_include_paths(cfg) + get_deconf_include_paths()
    for rp in rel:
        p = os.path.realpath(rp)
        if p in ret: continue
        ret.append(p)
    return ret

def read(cfg, filename):
    'Read file into existing cfg object, file is found'
    fpath = find_file(filename, get_include_paths(cfg))
    if fpath in cfg.files:
        return
    print 'Reading %s' % fpath
    cfg.read(fpath)
    cfg.files.append(fpath)

def parse(filenames):
    'Parse the filename(s), return an uninterpreted object'
    if not filenames: raise ValueError('No filenames given')
    if isinstance(filenames, type("")):
        filenames = [filenames]

    try:                from ConfigParser import SafeConfigParser
    except ImportError: from configparser import SafeConfigParser
    cfg = SafeConfigParser()
    cfg.files = list()
    cfg.optionxform = str       # want case sensitive

    for f in filenames:
        read(cfg, f)
    return cfg


def get_includes(cfg, sec, key = 'includes'):
    'Return a list of includes from configuration section'
    if not cfg.has_option(sec, key):
        return []
    inc_val = cfg.get(sec, key)
    inc_list = to_list(inc_val)
    if not inc_list:
        raise ValueError('Configuration item "includes" badly formed: "%s"' % inc_val)
    return inc_list


def add_includes(cfg, sec = 'start', key = 'includes'):
    'Read any additional files indicated by the key <key> in the section <sec>'
    includes = get_includes(cfg, sec, key)
    if not includes: return
    paths = get_include_paths(cfg)

    for fname in includes:
        fpath = find_file(fname, paths)
        if not fpath:
            raise ValueError( 'Failed to locate file: %s (%s)' % 
                              (fname, ':'.join(to_check)) )
        read(cfg, fpath)
        cfg.files.append(fpath)
    return

def merge_defaults(cfg, start = 'start', sections = 'defaults'):
    'Call to merge the <sections> section(s) into the <start> section.'
    if isinstance(sections, type('')):
        sections = [x.strip() for x in sections.split(',')]
    #print 'CFG sections:', cfg.sections()
    for sec in sections:
        if not cfg.has_section(sec):
            # print warning?
            continue
        for k,v in cfg.items(sec):
            if cfg.has_option(start, k):
                continue
            #print 'DECONF: merging',k,v
            cfg.set(start,k,v)


def load(filename, start = 'start', **kwds):
    '''
    Return the fully parsed, interpreted, inflated and formatted suite.
    '''
    if not filename:
        raise ValueError('deconf.load not given any files to load')

    cfg = parse(filename)
    add_includes(cfg, start)
    merge_defaults(cfg, start)
    add_includes(cfg, start)    # in case [defaults] has "includes="
    return interpret(cfg, **kwds)


def get_first_typed_section(cfg, typ, name):
    target = '%s %s' % (typ, name)
    for sec in cfg.sections():
        if sec == target:
            return sec
    raise ValueError('No section: <%s> %s' % (typ,name))

from confnode import NodeGroup

def interpret(cfg, start = 'start', **kwds):
    '''
    Interpret a parsed file by following any keytypes, return raw data
    structure.

    The <start> keyword can select a different section to start the
    interpretation.  Any additional keywords are override or otherwise
    added to the initial section.
    '''
    owner = NodeGroup(keytype = dict(cfg.items('keytype')))
    top = resolve(owner, cfg, start, None, **kwds)
    return top


def secname2typename(secname):
    if ' ' in secname:
        return secname.split(' ',1)
    return None, secname

def resolve(owner, cfg, secname, parent_node, **kwds):
    'Recursively load the configuration starting at the given section'

    secitems = dict(cfg.items(secname))

    # get special keytype section governing the hierarchy schema
    keytype = owner._keytype

    items = {}
    children_sections = []
    for k,v in secitems.items():
        typ = keytype.get(k)
        if not typ:
            items[k] = v
            continue

        for name in to_list(v):
            other_sec = get_first_typed_section(cfg, typ, name)
            children_sections.append(other_sec)

    node_type, node_name = secname2typename(secname)
    if node_type:
        items[node_type] = node_name
    node = owner(node_name, node_type, parent_node, extra = kwds, **items)
    for secname in children_sections:
        resolve(owner, cfg, secname, node, **kwds)
    return node
    # fixme: I'm ignoring kwds!  these will contain stuff needed for formatting
    # explicitly call these "format keywords" to distinguish them.


