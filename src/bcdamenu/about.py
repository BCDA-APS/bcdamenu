
# Copyright (c) 2017, UChicago Argonne, LLC.
# See LICENSE.txt file for details.

'''
show the About box
'''

import os, sys
from PyQt4 import QtCore, QtGui, uic

from bcdamenu import __version__, __url__, __issues__

UI_FILE = os.path.join(os.path.dirname(__file__), 'about.ui')
DOCS_URL = __url__
ISSUES_URL = __issues__
LICENSE_FILE = os.path.join(os.path.dirname(__file__), 'LICENSE.txt')


class InfoBox(QtGui.QDialog):
    '''
    a Qt GUI for the About box
    '''

    def __init__(self, parent=None, settings=None):
        self.settings = settings
        QtGui.QDialog.__init__(self, parent)
        loadUi(UI_FILE, baseinstance=self)
        
        self.license_box = None
        
        self.version.setText('software version: ' + str(__version__))

        self.docs_pb.clicked.connect(self.doDocsUrl)
        self.issues_pb.clicked.connect(self.doIssuesUrl)
        self.license_pb.clicked.connect(self.doLicense)
        self.setModal(False)

    def closeEvent(self, event):
        '''
        called when user clicks the big [X] to quit
        '''
        if self.license_box is not None:
            self.license_box.close()
        event.accept() # let the window close

    def doUrl(self, url):
        '''opening URL in default browser'''
        url = QtCore.QUrl(url)
        service = QtGui.QDesktopServices()
        service.openUrl(url)

    def doDocsUrl(self):
        '''opening documentation URL in default browser'''
        self.doUrl(DOCS_URL)

    def doIssuesUrl(self):
        '''opening issues URL in default browser'''
        self.doUrl(ISSUES_URL)

    def doLicense(self):
        '''show the license'''
        # if self.license_box is None:
        #     lfile = resources.resource_file(LICENSE_FILE, '.')
        #     license_text = open(lfile, 'r').read()
        #     ui = plainTextEdit.TextWindow(None, 
        #                                   'LICENSE', 
        #                                   license_text, 
        #                                   self.settings)
        #     ui.setMinimumSize(700, 500)
        #     self.license_box = ui
        #     #ui.setWindowModality(QtCore.Qt.ApplicationModal)
        # self.license_box.show()
        license_url = "https://raw.githubusercontent.com/BCDA-APS/bcdamenu"
        license_url += "/master/src/bcdamenu/LICENSE.txt"
        self.doUrl(license_url)


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

    Here is an example from this code:

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
