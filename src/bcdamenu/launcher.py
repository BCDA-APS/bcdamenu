#!/usr/bin/env python

'''
BcdaMenu: Creates a GUI menu button to start common beam line software
'''

import os
import sys
# TODO: import argparse
from PyQt4.QtGui import *       # QWidget, QLabel, QLineEdit, QGridLayout, QApplication, QPushButton
from functools import partial
import subprocess


USAXS_CONFIG = {
    'title': '9-ID-C USAXS menu',
    'menu_items': {
        "9-ID-C USAXS controls (MEDM)": "start_epics",
        "separator": None,
        "USAXS Q calculator": "qToolUsaxs.csh",
        "sample and detector XY position tool": "wxmtxy.csh",
        "USAXS sample stage tool": "/home/beams/USAXS/Apps/wxmtusaxs/wxmtusaxs",
        "PyMca": "/APSshare/bin/pymca",
        "SAXS Imaging tool": "/APSshare/epd/rh6-x86/bin/python /home/beams/USAXS/Apps/USAXS_dataworker/Main.py",
        "Save Instr. status to Elog": "saveToElog.csh",
    }
}


class MainButtonWindow(QWidget):
    '''the widget that holds the menu button'''

    def __init__(self, parent=None, config=None):
        QWidget.__init__(self, parent)
        self.config = config or USAXS_CONFIG

        self.popup  = QPushButton('Commands...')
        self.menu   = QMenu()
        self.popup.setMenu(self.menu)
        for k, v in self.config.get('menu_items', {}).items():
            if k == 'separator' and v is None:
                self.menu.addSeparator()
            else:
                action = self.menu.addAction(k, partial(self.receiver, k, v))

        self.admin_popup  = QPushButton('Help...')
        self.admin_menu   = QMenu()
        self.admin_popup.setMenu(self.admin_menu)
        self.admin_menu.addAction('About ...', self.about_box)
        # TODO: self.admin_menu.addAction('show log window')

        layout = QHBoxLayout()
        layout.addWidget(self.popup)
        layout.addWidget(self.admin_popup)

        self.setLayout(layout)
        self.setWindowTitle(self.config.get('title', 'BCDA Menu'))
    
    def receiver(self, label, command):
        print(label, os.path.normpath(command))
        # TODO: subprocess.Popen(cmd, shell = True)
    
    def about_box(self):
        '''TODO: should display an About box'''
        print(__doc__)


def gui():
    app = QApplication(sys.argv)
    probe = MainButtonWindow()
    probe.show()
    sys.exit(app.exec_())


def main():
    gui()
    # raise NotImplementedError('this program is under development')


if __name__ == '''__main__''':
    main()
