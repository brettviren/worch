#!/usr/bin/env python
'''
Features to produce a source directory from an online tar/zip archive.

It requires no previous steps.  It provides the 'seturl', 'download' and 'unpack' steps.
'''

from waflib.TaskGen import feature

from orch.util import get_unpacker, download_mirror
from orch.wafutil import exec_command

import orch.features
orch.features.register_defaults(
    'tarball', 
    source_urlfile = '{urlfile_dir}/{package}-{version}.url',
    source_archive_ext = 'tar.gz',
    source_archive_file = '{source_unpacked}.{source_archive_ext}',
    source_archive_path = '{download_dir}/{source_archive_file}',
    source_archive_checksum = '',
    source_unpacked = '{package}-{version}',
    source_unpacked_path = '{source_dir}/{source_unpacked}',
    unpacked_target = 'README-{package}',
    source_unpacked_target = '{source_unpacked_path}/{unpacked_target}',
)

@feature('tarball')
def feature_tarball(tgen):
    '''
    Handle a tarball source.  Implements steps seturl, download and unpack
    '''

    #print ('source_url: "%s" -> urlfile: "%s"' % (info.source_url, info.source_urlfile))
    tgen.step('seturl',
              rule = "echo '%s' > %s" % (tgen.worch.source_url, tgen.worch.source_urlfile),
              update_outputs = True,
              target = tgen.worch.source_urlfile)

    def dl_task(task):
        src = task.inputs[0]
        tgt = task.outputs[0]
        urls = [x.strip() for x in src.read().split()]
        download_mirror(urls, tgt.abspath(), tgen.worch.source_archive_checksum)
        return

    tgen.step('download',
              rule = dl_task,
              source = tgen.worch.source_urlfile, 
              target = tgen.worch.source_archive_path)


    def unpack_task(task):
        cmd = get_unpacker(task.inputs[0].abspath())
        return exec_command(task, cmd)

    tgen.step('unpack',
              rule = unpack_task,
              source = tgen.worch.source_archive_path, 
              target = tgen.worch.source_unpacked_target)

    return
