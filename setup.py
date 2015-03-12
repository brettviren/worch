import os
from setuptools import setup, find_packages
setup(name = 'worch',
      version = '1.3.3-dev',
      description = 'Build orchestration with waf.',
      author = 'Brett Viren',
      author_email = 'brett.viren@gmail.com',
      license = 'GPLv2',
      url = 'http://github.com/brettviren/worch',
      py_modules = ['orchlib'],
      packages = ['orch', 'orch.features', 'worch', 'worch.extras'],
      scripts = ['waf'],
      data_files = [
          ('share/worch/wscripts/worch', ['wscript']),
          ] + [('share/worch/config/'+x[0],
                map(lambda y: x[0]+'/'+y, x[2])) for x in os.walk('examples')],
)
