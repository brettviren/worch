#!/usr/bin/env python
'''
Utility functions
'''
import os.path as osp
import waflib.Logs as msg

try:    from urllib import request
except: from urllib import urlopen
else:   urlopen = request.urlopen

def exec_command(task, cmd, **kw):
    '''
    helper function to:
     - run a command
     - log stderr and stdout into worch_<taskname>.log.txt
     - printout the content of that file when the command fails
    '''
    msg.debug('orch: %s...' % task.name)
    cwd = getattr(task, 'cwd', task.generator.bld.out_dir)
    flog = open(osp.join(cwd, "worch_%s.log.txt" % task.name), 'w')
    cmd_dict = dict(kw)
    cmd_dict.update({
        'cwd': cwd,
        'env': kw.get('env', task.env.env),
        'stdout': flog,
        'stderr': flog,
        })
    try:
        ret = task.exec_command(cmd, **cmd_dict)
    except KeyboardInterrupt:
        raise
    finally:
        flog.close()
    if msg.verbose and ret == 0 and 'orch' in msg.zones:
        with open(flog.name) as f:
            msg.pprint('NORMAL','orch: %s (%s)\n%s' % (task.name, flog.name, ''.join(f.readlines())))
            pass
        pass
    if ret != 0:
        msg.error('orch: %s (%s)\n%s' % (task.name, flog.name, ''.join(open(flog.name).readlines())))
    return ret
