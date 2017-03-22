.. _installation:

Installation
############

.. index:: 
   installation
   pip

Install this program from the Python Package Index (PyPI) 
using the *pip* command::

    pip install bcdamenu
    pip install --no-deps bcdamenu

The ``--no-deps`` option tells *pip* not to download and attempt 
to build newer versions of other required packages.

.. _requirements:

Requirements
************

.. index:: 
   requirements; Python 2.7
   requirements; Anaconda Python
   requirements; PyQt4

* **Python 2.7**
* **PyQt4**

Your system will need to have the package **PyQt4.QtGui** 
already installed.  A Python 2.7 distribution, such as 
`Anaconda Python <http://continuum.io>`_ provides this package.

This program was developed on a Windows workstation and tested
with various Linux distributions (RHEL7, Linux Mint, Raspberry Pi).
It is expected to run on any host that provides the standard 
Python 2.7 packages *and* **PyQt4**.
