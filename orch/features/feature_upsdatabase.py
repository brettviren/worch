#!/usr/bin/env python

import os
import shutil
from .pfi import feature

requirements = dict(
    ups_products = None,
    ups_setups_file = None,
    )
@feature('upsdatabase', **requirements)
def feature_upsdatabase(info):
    
    def write_upsfiles(task):
        upsfiles_dir = info.ups_products.abspath() + '/.upsfiles'
        if not os.path.exists(upsfiles_dir):
            os.makedirs(upsfiles_dir)
        dbconfig_file = upsfiles_dir + '/dbconfig'
        with open(dbconfig_file, 'w') as fp:
            fp.write('''\
FILE = DBCONFIG
AUTHORIZED_NODES = *
VERSION_SUBDIR = 1
PROD_DIR_PREFIX = ${UPS_THIS_DB}
''')
# try to leave UPD out of this....
# UPD_USERCODE_DIR = ${UPS_THIS_DB}/.updfiles

        src = info.build_dir.abspath() + '/ups/setup'
        dst = task.outputs[0].abspath()
        print 'COPY: SRC=',src,'DST=',dst
        shutil.copy(src,dst)


        return

    info.task('upsdatabase',
              rule = write_upsfiles,
              source = info.build_target, 
              target = info.ups_setup_file)
    

    return
