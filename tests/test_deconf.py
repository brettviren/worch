#!/usr/bin/env python
'''
Test the orch.deconf module
'''

import os
import sys
orch_dir = '/'.join(os.path.realpath(__file__).split('/')[:-2] + ['orch'])
#print ('Using orch modules from: %s' % orch_dir)
sys.path.insert(0, orch_dir)

import deconf

example_dir = '/'.join(os.path.realpath(__file__).split('/')[:-2] + ['examples'])

def check_values(cfg, what):
    for isec, sec in enumerate(cfg['sections']):
        isec += 1
        for issec, ssec in enumerate(sec['subsections']):
            issec += 1
            print (isec,issec,ssec)
            assert ssec['section'] == "sec%d" % isec, (isec, issec, ssec)
            assert ssec['name'] == "sec%d" % isec, (isec, issec, ssec)

            assert ssec['subsec'] == "ssec%d" % issec, (isec, issec, ssec)
            assert ssec['subname'] == "ssec%d" % issec, (isec, issec, ssec)
            assert ssec['what'] == what

def test_parse_self_contained():
    if 'DECONF_INCLUDE_PATH' in os.environ:
        os.environ.pop('DECONF_INCLUDE_PATH')
    cfg = deconf.load(os.path.join(example_dir, 'test_deconf.cfg'))
    check_values(cfg, "self contained")

def test_parse_include_cwd():
    if 'DECONF_INCLUDE_PATH' in os.environ:
        os.environ.pop('DECONF_INCLUDE_PATH')
    cfg = deconf.load(os.path.join(example_dir, 'test_deconf_main.cfg'))
    check_values(cfg, "included from local directory")

def test_parse_include_env():
    os.environ['DECONF_INCLUDE_PATH'] = os.path.join(example_dir,'include')
    cfg = deconf.load(os.path.join(example_dir, 'test_deconf_main2.cfg'))
    check_values(cfg, "included from environment path variable")

if '__main__' == __name__:
    test_parse_self_contained()
    test_parse_include_cwd()
    test_parse_include_env()

