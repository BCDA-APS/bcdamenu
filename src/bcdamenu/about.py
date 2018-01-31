
# Copyright (c) 2017, UChicago Argonne, LLC.
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
    ~loadUi

'''

import os, sys
from PyQt4 import QtCore, QtGui, uic

UI_FILE = os.path.join(os.path.dirname(__file__), 'about.ui')


class InfoBox(QtGui.QDialog):
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
        QtGui.QDialog.__init__(self, parent)
        loadUi(UI_FILE, baseinstance=self)
        
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
        url = QtCore.QUrl(url)
        service = QtGui.QDesktopServices()
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
        """set the description in the About box"""
        self.description.setText(text)

    def setAuthorText(self, text):
        """set the author list in the About box"""
        self.authors.setText(text)

    def setCopyrightText(self, text):
        """set the copyright string in the About box"""
        self.copyright.setText(text)


def loadUi(ui_file, baseinstance=None, **kw):
    '''
    load a .ui file for use in building a GUI
    
    Wraps `uic.loadUi()` with code that finds our program's
    *resources* directory.
    
    :see: http://nullege.com/codes/search/PyQt4.uic.loadUi
    :see: http://bitesofcode.blogspot.ca/2011/10/comparison-of-loading-techniques.html
    
    inspired by:
    http://stackoverflow.com/questions/14892713/how-do-you-load-ui-files-onto-python-classes-with-pyside?lq=1
    
    .. rubric:: Basic Procedure

    #. Use Qt Designer to create a .ui file.
    #. Create a python class of the same type as the widget you created in the .ui file.
    #. When initializing the python class, use uic to dynamically load the .ui file onto the class.

    Here is an example:

    .. code-block:: python
        :linenos:

        from PyQt4 import QtGui
        import resources
        
        UI_FILE = 'plainTextEdit.ui'
        
        class TextWindow(QtGui.QDialog, form_class):
        
            def __init__(self, title, text):
                QtGui.QDialog.__init__(self, parent)
                resources.loadUi(UI_FILE, baseinstance=self)
                self.setWindowTitle(title)
                self.plainTextEdit.setPlainText(text)

        import sys
        app = QtGui.QApplication(sys.argv)
        win = TextWindow('the title', __doc__)
        win.show()
        sys.exit(app.exec_())

    '''
    return uic.loadUi(ui_file, baseinstance=baseinstance, **kw)
