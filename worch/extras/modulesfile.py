#!/usr/bin/env python
'''
A waf tool to supply the modulesfile worch feature.
'''

import os
from waflib.TaskGen import feature
import waflib.Logs as msg

import orch.features


def configure(cfg):
    orch.features.register_defaults(
        'modulesfile',
        modulesfile_version = '3.2.10',
        modulesfile_dir = '{PREFIX}/modules',
        modulesfile_store_dir = '{PREFIX}',
        modulesfile_store_envvar = 'STOREDIR',
        modulesfile = 'modulefile', # singular
        modulesfile_path = '{modulesfile_dir}/{package}/{version}/{modulesfile}',
    )
    return


def build(bld):

    @feature('modulesfile')
    def feature_modulesfile(tgen):

        w = tgen.worch
        mfd = tgen.make_node(tgen.worch.modulesfile_store_dir)

        def wash_path(path):
            'Turn absolute paths ones relative to modulesfile_store_dir via modulesfile_store_envvar'
            if not path.startswith('/'):
                return path
            pnode = tgen.make_node(path)
            tcl_env_var = "$::env(%s)" % tgen.worch.modulesfile_store_envvar
            ret = os.path.join(tcl_env_var, pnode.path_from(mfd))
            return ret
            

        def gen_modulefile(task):
            mfname = w.modulesfile_path
            with open(mfname, 'w') as fp:
                fp.write('#%Module1.0 #-*-tcl-*-#\n')

                for mystep, deppkg, deppkgstep in w.dependencies():
                    o = w.others[deppkg]
                    load = 'module load %s/%s' % (deppkg, o.version)
                    load = w.format(load)
                    fp.write(load + '\n')

                for var, val, oper in tgen.worch.exports():
                    val = wash_path(val)
                    if oper == 'set':
                        fp.write('setenv %s %s\n' % (var, val))
                    if oper == 'prepend':
                        fp.write('prepend-path %s %s\n' % (var, val))
                    if oper == 'append':
                        fp.write('append-path %s %s\n' % (var, val))

            return 0

        def gen_env(task):
            vars = dict(sdpath = tgen.worch.modulesfile_store_dir,
                        sdvar = tgen.worch.modulesfile_store_envvar,
                        mver = tgen.worch.modulesfile_version,
                    )
            sh = task.outputs[0].abspath()

            with open(sh,'w') as fp:
                fp.write('''#!/bin/sh
export %(sdvar)s MODULE_VERSION MODULESHOME LOADEDMODULES MODULEPATH
%(sdvar)s=%(sdpath)s
MODULEPATH=${%(sdvar)s}
MODULE_VERSION=%(mver)s
MODULEHOME=${%(sdvar)s}/Modules/${MODULE_VERSION}
module() { eval `${MODULEHOME}/bin/modulecmd sh $*`; }
''' % vars)
            csh = sh.replace('.sh','.csh')
            with open(csh,'w') as fp:
                fp.write('''#!/bin/csh
setenv %(sdvar)s "%(sdpath)s"
setenv MODULEPATH "${%(sdvar)s}"
source "${%(sdvar)s}/Modules/%(mver)s"
''' % vars)
            return 0

        tgen.step('modulesfile_env',
                  rule = gen_env,
                  target = tgen.make_node(os.path.join(tgen.worch.modulesfile_store_dir, "env.sh")))

        tgen.step('modulesfile',
                  rule = gen_modulefile,
                  source = tgen.control_node('install'),
                  target = tgen.make_node(tgen.worch.modulesfile_path))
        
    return
