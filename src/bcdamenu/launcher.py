#!/usr/bin/env python

'''
BcdaMenu: Creates a GUI menu button to start common beam line software
'''

import datetime
import os
import sys
import argparse
import sip
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

    def __init__(self, parent=None, settingsfilename=None):
        QWidget.__init__(self, parent)
        self.settingsfilename = settingsfilename
        if settingsfilename is None:
            raise ValueError('settings file name must be given')
        
        self.admin_popup  = PopupMenuButton('Help')
        self.admin_popup.addAction('About ...', self.about_box)
        self.admin_popup.addSeparator()
        self.admin_popup.addAction('Reload User Menus', self.reload_settings_file)
        # TODO: self.admin_popup.addAction('show log window') (issue #14)
        # TODO: edit settings file (issue #10)

        self.reload_settings_file()
    
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
    
    def reload_settings_file(self):
        '''(re)load the settings file and (re)create the popup button(s)'''
        # remove the existing popup menu buttons
        layout = self.layout()
        if layout is not None:
            for key, widget in self.user_popups.items():
                layout.removeWidget(widget)
                widget.deleteLater()
            layout.removeWidget(self.admin_popup)
            sip.delete(layout)

        # read the settings file (again)
        self.config = read_settings(self.settingsfilename)

        hv = 'horizontal'
        if str(self.config.get('layout', hv)).lower() == hv:
            layout = QHBoxLayout()
        else:
            layout = QVBoxLayout()
        self.setLayout(layout)

        # install the new user popup menu buttons
        self.user_popups = OrderedDict()
        self.layout_user_menus(self.config)
        layout.addWidget(self.admin_popup)
        self.setWindowTitle(self.config['title'])

    def layout_user_menus(self, config):
        '''
        '''
        for menu_name in reversed(config['menus']):
            popup = PopupMenuButton(menu_name)
            self.user_popups[menu_name] = popup

            # fallback to empty list if not found
            config_list = config.get(menu_name, [])
            for entry in config_list:
                k, v = entry
                if k == 'title':
                    popup.setText(v)
                elif k == 'separator' and v is None:
                    popup.addSeparator()
                else:
                    action = popup.addAction(k, partial(self.receiver, k, v))
            self.layout().insertWidget(0, popup)
    

def read_settings(ini_file):
    '''
    read the user menu settings from the .ini file
    '''
    if not os.path.exists(ini_file):
        raise ValueError('settings file not found: ' + ini_file)

    config = iniParser.ConfigParser(allow_no_value=True)
    config.optionxform = str    # do not make labels lower case
    config.read(ini_file)
    
    settings = dict(title='BcdaMenu', menus='', version='unknown')
    for k, v in config.items(MAIN_SECTION_LABEL):
        settings[k] = v
    settings['menus'] = settings['menus'].split()

    for menu_name in settings['menus']:
        settings[menu_name] = []

        # parse the settings file and coordinate numbered labels with commands
        labels = {}
        commands = {}
        menu_items_dict = dict(config.items(menu_name))
        for k, v in menu_items_dict.items():
            if k == 'title':
                settings[menu_name].append([k, v])
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
            settings[menu_name].append([label, commands[k]])
    
    return settings


def gui(settingsfilename = None):
    '''display the main widget'''
    app = QApplication(sys.argv)
    the_gui = MainButtonWindow(settingsfilename=settingsfilename)
    the_gui.show()
    sys.exit(app.exec_())


def main():
    '''process any command line options before starting the GUI'''
    import __init__
    version = __init__.__version__
    doc = __doc__.strip().splitlines()[0]
    doc += '\n  v' + version
    parser = argparse.ArgumentParser(prog='BcdaMenu', description=doc)
    parser.add_argument('settingsfile', help="Settings file (.ini)")
    parser.add_argument('-v', '--version', action='version', version=version)
    params = parser.parse_args()

    if not os.path.exists(params.settingsfile):
        raise IOError('file not found: ' + params.settingsfile)

    gui(settingsfilename = params.settingsfile)


if __name__ == '''__main__''':
    main()
