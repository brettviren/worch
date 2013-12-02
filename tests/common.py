
import os
import sys
worch_dir = '/'.join(os.path.realpath(__file__).split('/')[:-2])
sys.path.insert(0, worch_dir)

# try to find waflib
from glob import glob
for maybe in glob(os.path.join(worch_dir, '.waf*')):
    maybe = os.path.realpath(maybe)
    wafdir = os.path.join(maybe, 'waflib')
    if os.path.exists(wafdir):
        sys.path.insert(0, maybe)
        break

