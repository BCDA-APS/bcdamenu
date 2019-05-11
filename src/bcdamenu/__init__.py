'''
GUI menu button to start common software
'''

__project__     = u'BcdaMenu'
__description__ = u"A GUI menu button to start common software."
__copyright__   = u'2009-2019, UChicago Argonne, LLC'
__authors__     = [u'Pete Jemian', ]
__author__      = ', '.join(__authors__)
__author_name__ = __authors__[0]
__institution__ = u"Advanced Photon Source, Argonne National Laboratory"
__author_email__= u"jemian@anl.gov"
__url__         = u"http://BcdaMenu.readthedocs.io"
__issues__      = u"https://github.com/BCDA-APS/bcdamenu/issues"
__license__     = u"(c) " + __copyright__
__license__     = u"(c) " + __copyright__
__license_url__ = u"https://github.com/BCDA-APS/bcdamenu"
__license_url__ += u"/blob/master/src/bcdamenu/LICENSE.txt"
__platforms__   = 'any'
__zip_safe__    = False

__package_name__ = __project__
__long_description__    = __description__

__keywords__            = ['APS', 'BCDA', 'PyQt4', 'PyQt5']
#__requires__            = ['PyQt4', 'pyepics']
__install_requires__    = ()
__documentation_mocks__ = []       # do NOT mock PyQt4 here, big problems if you do

__classifiers__ = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: Free To Use But Restricted',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development :: Embedded Systems',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
   ]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
