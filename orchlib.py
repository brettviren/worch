#!/usr/bin/env python
# encoding: utf-8

import sys
import os, imp
from waflib import Context, Options, Utils, Logs, Scripting

import orch.tools

def options(opt):
    #opt.load('orch.tools', tooldir='.')
    orch.tools.options(opt)
    opt.add_option('--dot', action = 'store', default = None,
                   help = 'Produce a dot file of given name with dependency graph')
    opt.add_option('--dump-suite', action = 'store_true', default = False,
                   help = 'Dump the processed suite configuration data')

def configure(cfg):
    #cfg.load('orch.tools', tooldir='.')
    cfg.options = Options.options
    orch.tools.configure(cfg)

def dot(ctx):
    import orch.dot as odot
    bld = ctx.exec_dict['bld']
    #print 'TG:\n', '\n'.join([tg.name for tg in bld.get_all_task_gen()])
    odot.write(bld, ctx.options.dot)
    Logs.msg.info('orch: Wrote %s' % ctx.options.dot)
    sys.exit(0)

def dump(ctx):
    bld = ctx.exec_dict['bld']
    suite = bld.env.orch_package_dict
    from pprint import PrettyPrinter
    pp = PrettyPrinter(indent=2)
    pp.pprint(suite)
    sys.exit(0)

def build(bld):
    #bld.load('orch.tools', tooldir='.')
    orch.tools.build(bld)
    if bld.options.dot:
        # needs to be a pre-fun, not a post-fun
        bld.add_pre_fun(dot)
        #bld.add_post_fun(dot)
    if bld.options.dump_suite:
        bld.add_pre_fun(dump)



def recurse_rep(x, y):
    f = getattr(Context.g_module, x.cmd or x.fun, Utils.nada)
    return f(x)


def start(cwd, version, wafdir):
    print ("cwd: %s" % cwd)
    print ("version: %s" % version)
    print ("wafdir: %s" % wafdir)
    Logs.init_log()
    Context.waf_dir = wafdir
    Context.launch_dir = Context.out_dir = Context.top_dir = Context.run_dir = cwd
    Context.g_module = imp.new_module('wscript')
    Context.g_module.root_path = cwd
    Context.Context.recurse = recurse_rep

    Context.g_module.configure = configure
    Context.g_module.build = build
    Context.g_module.options = options
    Context.g_module.top = Context.g_module.out = '.'

    Options.OptionsContext().execute()

    do_config = 'configure' in sys.argv
    try:
        os.stat(cwd + os.sep + 'c4che')
    except:
        do_config = True
    if do_config:
        Scripting.run_command('configure')

    if 'clean' in sys.argv:
        Scripting.run_command('clean')

    if 'build' in sys.argv:
        Scripting.run_command('build')
 
