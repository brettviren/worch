
import os
import sys

try:
    myfilename = __file__
except NameError:
    import inspect
    myfilename = inspect.getframeinfo(inspect.currentframe()).filename

mydir = os.path.dirname(os.path.realpath(myfilename))

worch_dir = '/'.join(os.path.realpath(myfilename).split('/')[:-2])
sys.path.insert(0, worch_dir)

# try to find waflib
from glob import glob
for maybe in glob(os.path.join(worch_dir, '.waf*')):
    maybe = os.path.realpath(maybe)
    wafdir = os.path.join(maybe, 'waflib')
    if os.path.exists(wafdir):
        sys.path.insert(0, maybe)
        break


class FakeEnv:
    def __init__(self, **kwds):
        self.__dict__.update(**kwds)
        self.env = dict(os.environ)
    def __setattr__(self, name, value):
        self.__dict__[name] = value
    def derive(self):
        return FakeEnv(**self.__dict__)
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)

class FakeCfg:
    def __init__(self):
        self.env = FakeEnv()
    def setenv(self, name, value):
        self.__dict__[name] = value
    def __str__(self):
        return (self.__dict__)
