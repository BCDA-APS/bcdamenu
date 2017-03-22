#!/usr/bin/env python

'''starter for development of bcdamenu in the source tree - do not package'''

import os
import sys

sys.path.insert(0, os.path.join('src', ))
import bcdamenu.launcher

sys.argv.append(os.path.join('src', 'bcdamenu', 'bcdamenu.ini'))
bcdamenu.launcher.main()
