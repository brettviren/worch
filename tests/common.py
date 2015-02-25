
import os
import sys
from glob import glob

try:
    myfilename = __file__
except NameError:
    import inspect
    myfilename = inspect.getframeinfo(inspect.currentframe()).filename

tests_dir = os.path.dirname(os.path.realpath(myfilename))
src_dir = os.path.dirname(tests_dir)
example_dir = os.path.join(src_dir,'examples')

worch_dir = '/'.join(os.path.realpath(myfilename).split('/')[:-2])
sys.path.insert(0, worch_dir)

# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

# try to find waflib
wafprog = which('waf')
if wafprog:
    for maybe in glob(os.path.join(os.path.dirname(wafprog), '.waf*')):
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
    def envmunger(self, env): 
        return dict(self.env, **env)
class FakeCfg:
    def __init__(self):
        self.env = FakeEnv()
    def setenv(self, name, value):
        self.__dict__[name] = value
    def __str__(self):
        return (self.__dict__)
