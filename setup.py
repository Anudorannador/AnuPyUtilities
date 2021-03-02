# anupyutilities/initfuncs.py
# Copyright (C) 2021 AnuPyUtilities
# <see TUTHORS file>
#
# This module is part of AnuPyUtilities and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
setup file for package easyview python 3 libs.
'''

from setuptools import setup

setup(
    name='anupyutilities',
    version='0.1.0',
    description='Some Python utilities/toolkits',
    author='anduorannador',
    author_email='anudorannador@gmail.com',
    url='https://github.com/Anudorannador/AnuPyUtilities',
    packages=['easyview_pylibs'],
    install_requires=[
        "SQLAlchemy",
        "requests",
        "PyMySQL"
    ]
)
