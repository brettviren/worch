#!/usr/bin/env python

import os
from .pfi import feature
from orch.ups import simple_setup_table_file as table_file
import waflib.Logs as msg

requirements = dict(
    install_target = None,
    ups_products = None,
    ups_product_install_dir = None,
    ups_tablegen_target = None,
    ups_qualifiers = '',
    )

@feature('upstablegen', **requirements)
def feature_upstablegen(info):
    print '''
UPS crap:
ups_products = %s
ups_product_install_dir = %s
ups_tablegen_target = %s
ups_declare_target = %s
ups_qualifiers = "%s"
ups_flavor = "%s"
''' % (info.ups_products.abspath(),
       info.ups_product_install_dir.abspath(),
       info.ups_tablegen_target.abspath(),
       info.ups_declare_target.abspath(),
       info.ups_qualifiers,
       info.ups_flavor)


    def ups_table_gen_task(task):
        filename = info.ups_tablegen_target.abspath()
        if os.path.exists(filename):
            blah = 'UPS table file already exists: %s' % filename
            print blah
            msg.debug(blah)
            return 0
        upsdir = os.path.dirname(filename)
        if not os.path.exists(upsdir):
            os.makedirs(upsdir)

        print 'UPS writing table file: %s' % filename
        tf = table_file(**dict(info.items()))
        print tf
        with open(filename, 'w') as fp:
            fp.write(tf + '\n')
        return 0

    info.task('upstablegen',
              rule = ups_table_gen_task,
              source = info.install_target,
              target = info.ups_tablegen_target,
              cwd = info.build_dir)
