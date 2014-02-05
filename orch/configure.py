#!/usr/bin/env python
'''
Configure waf for worch.

It is expected that any external tools that add worch features have already been loaded.
'''
import os
from glob import glob

import waflib.Logs as msg
from waflib import Context

from .util import string2list
#from . import pkgconf
from . import pkgconf2 as pkgconf
from . import envmunge

def locate_config_files(pat):
    if os.path.exists(pat):
        return [pat]
    if pat.startswith('/'):
        return glob(pat)

    for cdir in os.environ.get('WORCH_CONFIG_PATH','').split(':') + [Context.waf_dir]:
        maybe = os.path.join(cdir,pat)
        got = glob(maybe)
        if got: return got

    return None
    

def get_orch_config_files(cfg):
    if not cfg.options.orch_config:
        raise RuntimeError('No Orchestration configuration file given (--orch-config)')
    orch_config = [] 
    okay = True
    for pat in string2list(cfg.options.orch_config):
        got = locate_config_files(pat)
        if got:
            orch_config += got
            continue
        msg.error('File not found: "%s"' % pat)
        okay = False
    if not okay:
        raise ValueError('no configuration files')
    return orch_config

def configure(cfg):
    msg.debug('orch: CONFIG CALLED')

    from . import features
    features.load()

    orch_config = get_orch_config_files(cfg)
    cfg.msg('Orch configuration files', '"%s"' % '", "'.join(orch_config))

    extra = dict(cfg.env)
    extra['top'] = cfg.path.abspath()
    out = cfg.bldnode.abspath() # usually {top}/tmp
    assert out, 'No out dir defined'
    extra['out'] = out
    extra['DESTDIR'] = getattr(cfg.options, 'destdir', '')
    msg.debug('orch: top="{top}" out="{out}" DESTDIR="{DESTDIR}"'.format(**extra))

    top = pkgconf.load(cfg, orch_config, start = cfg.options.orch_start, **extra)

    envmunge.decompose(cfg, top)

    check_suite(top)

    #dump_suite(top)

    cfg.msg('Orch configure envs', '"%s"' % '", "'.join(cfg.all_envs.keys()))
    msg.debug('orch: CONFIG CALLED [done]')

    return

def check_suite(top):
    errors = 0
    for node in top.owner().oftype('package'):
        for key, val in node.local_items():
            if val is None:
                msg.error('Unset configuration item for %s: %s' % (node._name, key))
                errors += 1
                continue
            if '{' in val:
                msg.error('Unresolved item in %s: %s = %s' % (node._name, key, val))
                errors += 1
    assert errors == 0, 'Errors found in suite configuration'

def dump_suite(top):
    for name, node in top.owner().nodes().items():
        print '[%s]' % node.secname()
        for k,v in node.local_items():
            print '#%s = %s' % (k,v)
            print '%s = %s' % (k,node[k])
        print
