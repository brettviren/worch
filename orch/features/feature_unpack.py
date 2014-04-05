#!/usr/bin/env python
'''
A feature to unpack an archive.

It follows a download step and provides an install step.
'''
from orch.util import get_unpacker
from waflib.TaskGen import feature
from orch.wafutil import exec_command

import orch.features
orch.features.register_defaults(
    'unpack', 
    unpack_archive = None,
    unpack_area = '.',
    unpack_target = None,
)
@feature('unpack')
def feature_unpack(tgen):

    ddir = tgen.make_node(tgen.worch.download_dir)
    upa = ddir.find_or_declare(tgen.worch.unpack_archive)

    udir = tgen.make_node(tgen.worch.unpack_area)
    udir.mkdir()
    utgt = udir.make_node(tgen.worch.unpack_target)

    def unpack_task(task):
        cmd = get_unpacker(task.inputs[0].abspath(), udir.abspath())
        return exec_command(task, cmd)

    tgen.step('install', rule = unpack_task, source = upa, target = utgt)

    return
