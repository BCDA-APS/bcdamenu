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


MAIN_SECTION_LABEL = 'BcdaMenu'


class PopupMenuButton(QPushButton):
    '''
    a QPushButton that provides a popup menu
    '''
    
    def __init__(self, button_name, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.setText(button_name)
        self.menu = QMenu()
        self.setMenu(self.menu)
    
    def addAction(self, text, action):
        self.menu.addAction(text, action)
    
    def addSeparator(self):
        self.menu.addSeparator()


class MainButtonWindow(QWidget):
    '''the widget that holds the menu button'''

    def __init__(self, parent=None, config=None):
        QWidget.__init__(self, parent)
        self.config = config or {}
        
        self.user_popups = OrderedDict()
        layout = QHBoxLayout()

        self.layout_user_menus(self.config, layout)

        self.admin_popup  = PopupMenuButton('Help...')
        self.admin_popup.addAction('About ...', self.about_box)
        # TODO: self.admin_popup.addAction('show log window') (issue #14)
        # TODO: edit settings file (issue #10)
        # TODO: reload settings file (issue #11)

        layout.addWidget(self.admin_popup)

        self.setLayout(layout)
        self.setWindowTitle(self.config.get('title', 'BCDA Menu'))
    
    def layout_user_menus(self, config, layout):
        '''
        '''
        for menu_name in config['menus']:
            popup = PopupMenuButton(menu_name)
            self.user_popups[menu_name] = popup

            title = config[menu_name].get('title', None)
            if title is not None:
                popup.setText(title)
                del config[menu_name]['title']

            # fallback to empty dictionary if not found
            config_dict = config.get(menu_name, {})
            for k, v in config_dict.items():
                if k == 'separator' and v is None:
                    popup.addSeparator()
                else:
                    action = popup.addAction(k, partial(self.receiver, k, v))
            layout.addWidget(popup)
    
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
        # TODO: issue #13
        print(__doc__)


def read_settings(ini_file):
    '''
    read the user menu settings from the .ini file
    '''
    config = iniParser.ConfigParser(allow_no_value=True)
    config.optionxform = str    # do not make labels lower case
    config.read(ini_file)
    
    settings = dict(title='BcdaMenu', menus='', version='unknown')
    for k, v in config.items(MAIN_SECTION_LABEL):
        settings[k] = v
    settings['menus'] = settings['menus'].split()

    for menu_name in settings['menus']:
        settings[menu_name] = OrderedDict()

        # parse the settings file and coordinate numbered labels with commands
        labels = {}
        commands = {}
        menu_items_dict = dict(config.items(menu_name))
        for k, v in menu_items_dict.items():
            if k == 'title':
                settings[menu_name][k] = v
            else:
                parts = k.split()
                if len(parts) < 2:
                    msg = 'Error in settings file, section [%s]: ' % menu_name + ini_file
                    msg += '\n  line reading: ' + k + ' = ' + v
                    raise KeyError(msg)
                key = 'key_%04d' % int(parts[0])
                label = k[k.find(' '):].strip()
                if label == 'submenu':   # TODO: support submenus issue #12
                    labels[key] = label + ': planned feature #12'
                    commands[key] = None
                else:
                    labels[key] = label
                    if len(v) == 0:
                        v = None
                    commands[key] = v
    
        # add the menu items in numerical order
        for k, label in sorted(labels.items()):
            settings[menu_name][label] = commands[k]
    
    return settings


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

    settings = read_settings(params.settingsfile)
    gui(config = settings)


if __name__ == '''__main__''':
    main()
