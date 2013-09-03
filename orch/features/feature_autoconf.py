#!/usr/bin/env python
from .pfi import feature
from .feature_prepare import generic

requirements = {
    'unpacked_target': 'configure',
    'source_unpacked': 'config.status',
    'prepare_cmd': '../../{source_unpacked}/configure',
    'prepare_cmd_options': '--prefix={install_dir}',
    'prepare_target': 'config.status',
    'build_dir': None,
}

@feature('autoconf', **requirements)
def feature_autoconf(info):
    return generic(info)


