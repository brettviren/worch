from setuptools import setup, find_packages
setup(name = 'worch',
      version = '1.0rc',
      description = 'Build orchestration with waf.',
      author = 'Brett Viren',
      author_email = 'brett.viren@gmail.com',
      license = 'GPLv2',
      url = 'http://github.com/brettviren/worch',
      py_modules = ['orchlib'],
      packages = ['orch', 'orch.features'],
      include_package_data = True,
      scripts = ['waf'],
)
