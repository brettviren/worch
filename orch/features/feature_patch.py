#!/usr/bin/env python
'''
Features to apply a patch to an unpacked source directory.

It requires the 'unpack' step and provides the 'patch' step.
'''
import os
import sys
from waflib.TaskGen import feature
import waflib.Logs as msg

from orch.util import urlopen, get_unpacker
from orch.wafutil import exec_command

import orch.features
orch.features.register_defaults(
    'patch',
    patch_url = "",
    patch_urlfile = '{urlfile_dir}/{package}-{version}.patch.url',
    patch_file = '{package}-{version}.patch',
    patch_checksum = '',
    patch_cmd = 'patch -i',
    patch_cmd_std_opts = '',
    patch_cmd_options = '',
    )

def resolve_url(url, filetype='patches'):
    '''
    Return a full URL given a maybe partial one.

    If the URL is a relative path, look for the file in a few places.
    '''
    if not url: 
        return
    if ':' in url:
        return url
    if url.startswith('/'):
        return 'file://' + url
    trials = ['.', sys.prefix, sys.prefix+'/share/worch', sys.prefix+'/share/worch/'+filetype]
    for maybe in trials:
        fullpath = os.path.realpath(os.path.join(maybe, url))
        #print 'MAYBE:',fullpath
        if os.path.exists(fullpath):
            return 'file://' + fullpath
        continue
    return                      # fail

@feature('patch')
def feature_patch(tgen):
    '''
    Apply a patch
    '''
    w = tgen.worch
    patch_url = resolve_url(w.patch_url)
    if not patch_url:
        msg = 'No patch file found (%s) for package "%s"' % (w.patch_url, w.package)
        raise ValueError,msg

    tgen.step('urlpatch',
              rule = "echo '%s' > %s" % (patch_url, w.patch_urlfile),
              update_outputs = True,
              target = w.patch_urlfile)

    # fixme: this is mostly a cut-and-paste from feature_tarball.
    # Both should be factored out to common spot....
    def dl_task(task):
        src = task.inputs[0]
        tgt = task.outputs[0]
        url = src.read().strip()
        try:
            web = urlopen(url)
            tgt.write(web.read(),'wb')
        except Exception:
            import traceback
            traceback.print_exc()
            msg.error(w.format("[{package}_dlpatch] problem downloading [{patch_urlfile}]"))
            raise

        checksum = w.patch_checksum
        if not checksum:
            return
        hasher_name, ref = checksum.split(":")
        import hashlib, os
        # FIXME: check the hasher method exists. check for typos.
        hasher = getattr(hashlib, hasher_name)()
        hasher.update(tgt.read('rb'))
        data= hasher.hexdigest()
        if data != ref:
            msg.error(w.format("[{package}_dlpatch] invalid checksum:\nref: %s\nnew: %s" %\
                                        (ref, data)))
            try:
                os.remove(tgt.abspath())
            except IOError: 
                pass
            return 1
        return
    tgen.step('dlpatch',
              rule = dl_task,
              source = w.patch_urlfile,
              target = w.patch_file)

    def apply_patch(task):
        src = task.inputs[0].abspath()
        tgt = task.outputs[0].abspath()
        cmd = "%s %s %s" % ( w.patch_cmd, src, w.patch_cmd_options )
        ret = exec_command(task, cmd)
        return ret

    after =  w.package + '_unpack'
    before = w.package + '_prepare'

    tgen.step('patch',
              rule = apply_patch,
              source = [w.patch_file, tgen.control_node('unpack')],
              target = [tgen.control_node('patch')],
              depends_on = [after],
              after = [after], before = [before])

    
