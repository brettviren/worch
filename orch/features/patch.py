#!/usr/bin/env python
from waflib import TaskGen
from .pfi import PackageFeatureInfo

from orch.util import urlopen, exec_command
from .tarball import requirements as tarball_requirements


requirements = {
    'patch_urlfile': '{package}-{version}.patch.url',
    'patch_url': None,
    'patch_ext': 'patch', # or diff
    'patch_package': '{package}-{version}.{patch_ext}',
    'patch_cmd': 'patch',
    'patch_cmd_options': '-i',
    'patch_target': '{package}-{version}.{patch_ext}.applied',
}


@TaskGen.feature('patch')
def feature_patch(self):
    '''
    Apply a patch on the unpacked sources.
    '''
    reqs = dict(requirements, **tarball_requirements)
    pfi = PackageFeatureInfo(self.package_name, 'patch', self.bld, reqs)

    if not pfi('patch_url'):
        return

    f_urlfile = pfi.get_node('patch_urlfile')
    d_patch = pfi.get_node('source_dir')
    f_patch = pfi.get_node('patch_package', d_patch)
    f_applied = pfi.get_node('patch_target', d_patch)

    d_source = pfi.get_node('source_dir')
    d_unpacked = pfi.get_node('source_unpacked', d_source)
    f_unpack = pfi.get_node('unpacked_target', d_unpacked)
    
    self.bld(name = pfi.format('{package}_urlpatch'),
             rule = "echo %s > ${TGT}" % pfi('patch_url'), 
             update_outputs = True,
             source = f_unpack,
             target = f_urlfile,
             depends_on = pfi.get_deps('patch') + [pfi.format('{package}_unpack')],
             env = pfi.env)

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
            self.bld.fatal("[%s] problem downloading [%s]" % (pfi.format('{package}_dlpatch'), url))

    self.bld(name = pfi.format('{package}_dlpatch'),
             rule = dl_task,
             source = f_urlfile,
             target = f_patch,
             depends_on = pfi.get_deps('dlpatch'),
             env = pfi.env)

    def apply_patch(task):
        src = task.inputs[0].abspath()
        tgt = task.outputs[0].abspath()
        cmd = "%s %s %s" % (
            pfi.get_var('patch_cmd'),
            pfi.get_var('patch_cmd_options'),
            src,
            )
        o = exec_command(task, cmd)
        if o != 0:
            return o
        cmd = "touch %s" % tgt
        o = task.exec_command(cmd)
        return o
    
    step_name = pfi.format('{package}_patch')
    self.bld(name = step_name, 
             rule = apply_patch,
             source = f_patch,
             target = f_applied,
             cwd = pfi.get_node('source_dir').abspath(),
             depends_on = pfi.get_deps('patch'),
             env = pfi.env)

    # make sure {package}_prepare will wait for us to be done.
    tsk = self.bld.get_tgen_by_name(pfi.format('{package}_prepare'))
    tsk.depends_on.append(step_name)
    return
