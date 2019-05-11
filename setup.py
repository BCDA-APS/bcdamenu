#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2009-2019, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE, distributed with this software.
#-----------------------------------------------------------------------------

from setuptools import setup, find_packages
import os
import re
import sys

import versioneer

# pull in some definitions from the package's __init__.py file
sys.path.insert(0, os.path.join('src', ))
import bcdamenu


verbose=1
long_description = open('README.rst', 'r').read()


setup (
    name             = bcdamenu.__package_name__,
    version          = versioneer.get_version(),
    cmdclass         = versioneer.get_cmdclass(),
    license          = bcdamenu.__license__,
    description      = bcdamenu.__description__,
    long_description = long_description,
    author           = bcdamenu.__author_name__,
    author_email     = bcdamenu.__author_email__,
    url              = bcdamenu.__url__,
    #download_url=bcdamenu.__download_url__,
    keywords         = bcdamenu.__keywords__,
    platforms        = 'any',
    install_requires = bcdamenu.__install_requires__,
    package_dir      = {'': 'src'},
    packages         = ['bcdamenu', ],
    #packages=find_packages(),
    package_data     = {
         'bcdamenu': [
            'bcdamenu.ini',
            'LICENSE.txt',
            'about.ui',
            ],
         },
    classifiers      = bcdamenu.__classifiers__,
    entry_points     = {
         # create & install scripts in <python>/bin
        'console_scripts': [
             'bcdamenu=bcdamenu.launcher:main',
        ],
         'gui_scripts': [
		 ],
    },
)
