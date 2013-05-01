#!/usr/bin/env python

from distutils.core import setup
setup(name='bonehead-plugin-spiff',
    version='0.1.0',
    description='A set of Spiff plugins for Bonehead',
    author='Trever Fischer',
    author_email='wm161@wm161.net',
    url='http://github.com/synhak/spiff',
    data_files=[('/usr/share/bonehead/plugins/spiff/', [
      'spiff/frontDoor.py',
      'spiff/spiff-open-close.bonehead-plugin',
      'spiff/resources.py',
      'spiff/resources.ui',
      'spiff/resource-label.latex',
      'spiff/spiff-resources.bonehead-plugin',
    ])]
)
