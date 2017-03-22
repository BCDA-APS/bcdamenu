.. include:: ../../README.rst

* **version**   |version|
* **release**   |release|
* **published** |today|

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
   install
   source_code/*
   license



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
