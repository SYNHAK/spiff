#!/usr/bin/env python

from distutils.core import setup
setup(name='Spiff',
    version='0.1.4',
    description="API to Spaceman Spiff",
    author='Torrie Fischer',
    author_email='tdfischer@hackerbots.net',
    url='http://github.com/synhak/spiff',
    py_modules=['spiff'],
    requires=['requests'],
)
