#!/usr/bin/env python
'''
waf tool for features related to installing code the "Fermilab way"
'''

def configure(cfg):
    pass
def build(bld):
    pass



from waflib.TaskGen import feature

from orch.util import urlopen, get_unpacker
from orch.wafutil import exec_command

import orch.features
orch.features.register_defaults(
    'fnalsrcbundle', 
    fnal_srcbundle_file = '{fnal_name}-{version}-source.tar.bz2',
    fnal_srcbundle_url = 'http://oink.fnal.gov/distro/art/{fnal_srcbundle_file}',
    fnal_srcbundle_urlfile = '{package}-{version}.url',
    fnal_srcbundle_checksum = '',
)

@feature('fnalsrcbundle')
def feature_fnalsrcbundle(tgen):
    '''
    Handle a Fermilab source bundle.
    '''

    products_dir = tgen.make_node(tgen.worch.fnal_products_path)


    tgen.step('seturl',
              rule = "echo '%s' > %s" % \
                  (tgen.worch.fnal_srcbundle_url, 
                   tgen.worch.fnal_srcbundle_urlfile),
              update_outputs = True,
              target = tgen.worch.fnal_srcbundle_urlfile)

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
            msg.error(tgen.worch.format("failed to download [{fnal_srcbundle_url}]"))
            raise

        checksum = tgen.worch.fnal_srcbundle_checksum
        if not checksum:
            return
        hasher_name, ref = checksum.split(":")
        import hashlib, os
        # FIXME: check the hasher method exists. check for typos.
        hasher = getattr(hashlib, hasher_name)()
        hasher.update(tgt.read('rb'))
        data= hasher.hexdigest()
        if data != ref:
            msg.error(tgen.worch.format("invalid checksum:\nref: %s\nnew: %s" %\
                                        (ref, data)))
            try:
                os.remove(tgt.abspath())
            except IOError: 
                pass
            return 1
        return

    tgen.step('download',
              rule = dl_task,
              source = tgen.worch.fnal_srcbundle_urlfile, 
              target = tgen.worch.fnal_srcbundle_file)

    def unpack_task(task):
        cmd = get_unpacker(task.inputs[0].abspath(), 
                           tgen.worch.fnal_products_path)
        return exec_command(task, cmd)


    unpack_target = map(products_dir.make_node,
                        tgen.to_list(tgen.worch.fnal_srcbundle_target))
    tgen.step('unpack',
              rule = unpack_task,
              source = tgen.worch.fnal_srcbundle_file,
              target = unpack_target)

    return
