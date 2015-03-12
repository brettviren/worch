#!/usr/bin/env python
'''
Features to produce a tarball package of an install_dir.

'''

import os
import tarfile

from waflib.TaskGen import feature

import orch.features
orch.features.register_defaults(
    'tarpack', 
    install_dir = None,         # must be supplied
    tarpack_prefix='',          # prefix to give to all files in tarpack, end in '/' if desired
    tarpack_filename='{package}-{version}.tgz',
)

@feature('tarpack')
def feature_tarpack(tgen):
    '''
    Pack up the install_dir as a tar file.  Implements pack
    '''

    idir = tgen.make_node(tgen.worch.install_dir)

    def packit(task):
        fn = str(task.outputs[0])
        mode = 'w:'
        ext = os.path.splitext(fn)[1][1:]
        if ext in ['gz','tgz']:
            mode += 'gz'
        elif ext in ['bz','bz2','tbz','tbz2']:
            mode += 'bz2'
        tf = tarfile.open(task.outputs[0].abspath(), mode=mode)
        tf.add(idir.abspath(), arcname = tgen.worch.tarpack_prefix, recursive=True)
        tf.close()

    tgen.step('pack',
              rule = packit,
              source = [tgen.control_node('install')],
              target = tgen.worch.format('tarpack/{tarpack_filename}'))

