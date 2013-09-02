#!/usr/bin/env python
from waflib import TaskGen
from .pfi import PackageFeatureInfo

from orch.util import urlopen

def get_unpacker(filename, dirname):
    if filename.endswith('.zip'): 
        return 'unzip -d %s %s' % (dirname, filename)
    
    text2flags = {'.tar.gz':'xzf', '.tgz':'xzf', '.tar.bz2':'xjf', '.tar':'xf' }
    for ext, flags in text2flags.items():
        if filename.endswith(ext):
            return 'tar -C %s -%s %s' % (dirname, flags, filename)
    return 'tar -C %s -xf %s' % (dirname, filename)

requirements = {
    'source_urlfile': '{package}-{version}.url',
    'source_url': None,
    'source_url_checksum': None, # md5:xxxxx, sha224:xxxx, sha256:xxxx, ...
    'srcpkg_ext': 'tar.gz',
    'source_package': '{package}-{version}.{srcpkg_ext}',
    'download_dir': 'downloads',
    'download_target': '{download_dir}/{source_package}',
    'source_dir': 'sources',
    'source_unpacked': '{package}-{version}',
    'unpacked_target': 'configure',
}


@TaskGen.feature('tarball')
def feature_tarball(self):
    '''
    Handle a tarball source.  Implements steps seturl, download and unpack
    '''
    pfi = PackageFeatureInfo(self.package_name, 'tarball', self.bld, requirements)


    f_urlfile = pfi.get_node('source_urlfile')
    d_download = pfi.get_node('download_dir')
    f_tarball = pfi.get_node('source_package', d_download)

    d_source = pfi.get_node('source_dir')
    d_unpacked = pfi.get_node('source_unpacked', d_source)
    f_unpack = pfi.get_node('unpacked_target', d_unpacked)

    #print ('source_url: "%s" -> urlfile: "%s"' % (pfi('source_url'), f_urlfile))
    self.bld(name = pfi.format('{package}_seturl'),
             rule = "echo %s > ${TGT}" % pfi('source_url'), 
             update_outputs = True,
             target = f_urlfile,
             depends_on = pfi.get_deps('seturl'),
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
            self.bld.fatal("[%s] problem downloading [%s]" % (pfi.format('{package}_download'), url))

        checksum = pfi.get_var('source_url_checksum')
        if not checksum:
            return
        hasher_name, ref = checksum.split(":")
        import hashlib
        # FIXME: check the hasher method exists. check for typos.
        hasher = getattr(hashlib, hasher_name)()
        hasher.update(tgt.read('rb'))
        data= hasher.hexdigest()
        if data != ref:
            self.bld.fatal(
                "[%s] invalid MD5 checksum:\nref: %s\nnew: %s"
                % (pfi.format('{package}_download'), ref, data))
        return

    self.bld(name = pfi.format('{package}_download'),
             rule = dl_task,
             source = f_urlfile, 
             target = f_tarball,
             depends_on = pfi.get_deps('download'),
             env = pfi.env)

    self.bld(name = pfi.format('{package}_unpack'), 
             rule = get_unpacker(f_tarball.abspath(), f_unpack.parent.parent.abspath()),
             source = f_tarball, target = f_unpack,
             depends_on = pfi.get_deps('unpack'),
             env = pfi.env)

    return
