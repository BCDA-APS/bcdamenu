########
bcdamenu
########

Creates a GUI menu button to start common beam line software

Provides
########

* **bcdamenu**       : the button menu

Package Information
###################

* **author**         Pete R. Jemian
* **email**          jemian@anl.gov
* **copyright**      2009-2019, Pete R. Jemian
* **license**        ANL OPEN SOURCE LICENSE (see `LICENSE.txt <http://BcdaMenu.readthedocs.io/en/latest/license.html>`_ file)
* **documentation**  http://bcdamenu.readthedocs.io
* **source**         https://github.com/BCDA-APS/bcdamenu
* **PyPI**           https://pypi.python.org/pypi/bcdamenu
* **version**        |version|
* **release**        |release|
* **published**      |today|

Usage
=====

:typical:

   ::
   
      user@linux > bcdamenu path/to/settings_file.ini &

:bash starter file:

   ::
   
      #!/bin/bash
      bcdamenu path/to/settings_file.ini &

:usage:

   ::
   
      user@linux > bcdamenu
      usage: BcdaMenu [-h] settingsfile
      BcdaMenu: error: too few arguments

:help:

   ::
   
      user@linux > bcdamenu -h
      usage: BcdaMenu [-h] settingsfile
      
      BcdaMenu: Creates a GUI menu button to start common beam line software
      
      positional arguments:
        settingsfile  Settings file (.ini)
      
      optional arguments:
        -h, --help    show this help message and exit

Contents
========

.. toctree::
   :maxdepth: 2
   :glob:

   settings
   examples
   history
   install
   source_code/*
   changes
   license



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
