#!/usr/bin/env python

'''starter for development of bcdamenu in the source tree - do not package'''

import os
import sys

sys.path.insert(0, os.path.join('src', ))
import bcdamenu.launcher


candidates = [
    os.path.join(os.environ.get('HOME', 'not defined'), 'bin', 'bcdamenu.ini'),
    os.path.join(os.environ.get('HOMEPATH', 'not defined'), '.bcdamenu.ini'),
    os.path.join('src', 'bcdamenu', 'bcdamenu.ini')
]
for path in candidates:
    if os.path.exists(path):
        sys.argv.append(path)
        break
    
bcdamenu.launcher.main()
