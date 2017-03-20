#!/usr/bin/env python

'''
BcdaMenu: Creates a GUI menu button to start common beam line software
'''

import datetime
import os
import sys
import argparse
from PyQt4.QtGui import *
from functools import partial
import subprocess
from collections import OrderedDict
try:
    import configparser as iniParser
except:
    import ConfigParser as iniParser


DEFAULT_SECTION_LABEL = 'DEFAULT'
MENU_ITEMS_SECTION_LABEL = 'menu_items'


class MainButtonWindow(QWidget):
    '''the widget that holds the menu button'''

    def __init__(self, parent=None, config=None):
        QWidget.__init__(self, parent)
        self.config = config or {}

        self.popup  = QPushButton('Commands...')
        self.menu   = QMenu()
        self.popup.setMenu(self.menu)
        
        # fallback to empty dictionary if not found
        config_dict = self.config.get(MENU_ITEMS_SECTION_LABEL, {})
        for k, v in config_dict.items():
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
        '''handle commands from menu button'''
        msg = 'BcdaMenu (' 
        msg += str(datetime.datetime.now())
        msg += '), ' + label
        if command is None:
            msg += ': '
        else:
            command = os.path.normpath(command)
        msg += ':  ' + str(command)
        print(msg)
        if command is not None:
            subprocess.Popen(command, shell = True)
    
    def about_box(self):
        '''TODO: should display an About box'''
        print(__doc__)


def gui(config = None):
    '''display the main widget'''
    app = QApplication(sys.argv)
    probe = MainButtonWindow(config=config)
    probe.show()
    sys.exit(app.exec_())


def main():
    '''process any command line options before starting the GUI'''
    doc = __doc__.strip().splitlines()[0]
    #doc += '\n  v' + __init__.__version__
    parser = argparse.ArgumentParser(prog='BcdaMenu', description=doc)
    parser.add_argument('settingsfile', help="Settings file (.ini)")
    params = parser.parse_args()

    if not os.path.exists(params.settingsfile):
        raise IOError('file not found: ' + params.settingsfile)

    config = iniParser.ConfigParser(allow_no_value=True)
    config.read(params.settingsfile)
    
    settings = dict(title='BcdaMenu', menu_items=OrderedDict())
    for k, v in config.items(DEFAULT_SECTION_LABEL):
        settings[k] = v

    # parse the settings file and coordinate numbered labels with commands
    labels = {}
    commands = {}
    menu_items_dict = dict(config.items(MENU_ITEMS_SECTION_LABEL))
    for k, v in menu_items_dict.items():
        if k == 'title': continue
        parts = k.split()
        if parts[0] not in ('command', 'label'):
            msg = 'Error in settings file, section [menu_items]: ' + params.settingsfile
            msg += '\n  line reading: ' + k + ' = ' + v
            raise KeyError(msg)
        item = 'key_%04d' % int(parts[1])
        if parts[0] == 'label':
            labels[parts[1]] = v
        elif parts[0] == 'command':
            if v == 'None':
                v = None
            commands[parts[1]] = v
    
    # add the menu items in numerical order
    for k, label in sorted(labels.items()):
        settings[MENU_ITEMS_SECTION_LABEL][label] = commands[k]

    gui(config = settings)


if __name__ == '''__main__''':
    main()
