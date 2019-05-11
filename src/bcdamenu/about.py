
# Copyright (c) 2009-2019, UChicago Argonne, LLC.
# See LICENSE.txt file for details.

'''
show the About box
    
**Usage** (example)

::

    ui = about.InfoBox(self)

    ui.setTodoURL(__issues__)
    ui.setDocumentationURL(__url__)
    ui.setLicenseURL(__license_url__)
    ui.setTitle(config_file_parser.MAIN_SECTION_LABEL)
    ui.setVersionText("software version: " + __version__)
    ui.setSummaryText(__doc__.strip())
    ui.setAuthorText(__author__)
    ui.setCopyrightText(__copyright__)

    ui.show()

.. autosummary::

    ~InfoBox
    ~myLoadUi

'''

import os, sys
try:
    from PyQt5.QtCore import QUrl
    from PyQt5.QtWidgets import QDialog
    from PyQt5.QtGui import QDesktopServices
    from PyQt5.uic import loadUi as uicLoadUi
except ImportError:
    from PyQt4.QtCore import QUrl
    from PyQt4.QtGui import QDialog, QDesktopServices
    from PyQt4.uic import loadUi as uicLoadUi

UI_FILE = os.path.join(os.path.dirname(__file__), 'about.ui')


class InfoBox(QDialog):
    '''
    a Qt GUI for the About box
    
    .. autosummary::
    
       ~setTodoURL
       ~setDocumentationURL
       ~setLicenseURL
       ~setTitle
       ~setVersionText
       ~setSummaryText
       ~setAuthorText
       ~setCopyrightText
      
    '''

    def __init__(self, parent=None, settings=None):
        from __init__ import __project__, __url__, __license_url__

        self.settings = settings
        QDialog.__init__(self, parent)
        myLoadUi(UI_FILE, baseinstance=self)
        
        self.license_url = __license_url__
        self.documentation_url = __url__
        
        self.setWindowTitle("About " + __project__)

        self.docs_pb.clicked.connect(self.doDocsUrl)
        self.issues_pb.clicked.connect(self.doIssuesUrl)
        self.license_pb.clicked.connect(self.doLicense)
        self.setModal(False)

    def closeEvent(self, event):
        '''
        called when user clicks the big [X] to quit
        '''
        event.accept() # let the window close

    def doUrl(self, url):
        '''opening URL in default browser'''
        url = QUrl(url)
        service = QDesktopServices()
        service.openUrl(url)

    def doDocsUrl(self):
        '''show documentation URL in default browser'''
        if self.documentation_url is not None:
            self.doUrl(self.documentation_url)

    def doIssuesUrl(self):
        '''show issues URL in default browser'''
        if self.issues_url is not None:
            self.doUrl(self.issues_url)

    def doLicense(self):
        '''show the license URL in default browser'''
        if self.license_url is not None:
            self.doUrl(self.license_url)

    def setTodoURL(self, url):
        """set the URL for the issue tracker"""
        self.issues_url = url

    def setDocumentationURL(self, url):
        """set the URL for the documentation"""
        self.documentation_url = url
        self.docs_pb.setText("Docs:  " + url + " ...")

    def setLicenseURL(self, url):
        """set the URL for the software license text"""
        self.license_url = url

    def setTitle(self, text):
        """set the title in the About box"""
        self.title.setText(text)

    def setVersionText(self, text):
        """set the version text in the About box"""
        self.version.setText(text)

    def setSummaryText(self, text):
        """set the description in th
        e About box"""
        self.description.setText(text)

    def setAuthorText(self, text):
        """set the author list in the About box"""
        self.authors.setText(text)

    def setCopyrightText(self, text):
        """set the copyright string in the About box"""
        self.copyright.setText(text)


def myLoadUi(ui_file, baseinstance=None, **kw):
    '''
    load a .ui file for use in building a GUI
    
    Wraps `uic.loadUi()` with code that finds our program's
    *resources* directory.
    
    :see: http://nullege.com/codes/search/PyQt4.uic.loadUi
    :see: http://bitesofcode.blogspot.ca/2011/10/comparison-of-loading-techniques.html
    
    inspired by:
    http://stackoverflow.com/questions/14892713/how-do-you-load-ui-files-onto-python-classes-with-pyside?lq=1
    '''
    return uicLoadUi(ui_file, baseinstance=baseinstance, **kw)
