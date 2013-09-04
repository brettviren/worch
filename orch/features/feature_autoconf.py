#!/usr/bin/env python
'''
This feature is a specific "prepare" feature to set Autoconf related
configuration items.
'''
from .pfi import feature
from .feature_prepare import generic

requirements = {
    'unpacked_target': 'configure',
    'source_unpacked': None,
    'prepare_cmd': '../../{source_unpacked}/configure',
    'prepare_cmd_options': '--prefix={install_dir}',
    'prepare_target': 'config.status',
    'build_dir': None,
}

@feature('autoconf', **requirements)
def feature_autoconf(info):
    return generic(info)


