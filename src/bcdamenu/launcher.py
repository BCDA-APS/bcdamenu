#!/usr/bin/env python

'''
BcdaMenu: Creates a GUI menu button to start common beam line software
'''

import argparse
from collections import OrderedDict
import datetime
from functools import partial
import os
import sys
import threading
from PyQt4 import QtGui, QtCore
try:
    import configparser as iniParser
except:
    import ConfigParser as iniParser
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess


MAIN_SECTION_LABEL = 'BcdaMenu'
DEBUG = False
#DEBUG = True
DEBUG_COLOR_OFF = "white"
DEBUG_COLOR_ON = "#fec"


class MainButtonWindow(QtGui.QMainWindow):
    '''the widget that holds the menu button'''

    process_responded = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, settingsfilename=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.settingsfilename = settingsfilename
        if settingsfilename is None:
            raise ValueError('settings file name must be given')
        
        self.command_number = 0
        self.command_echo = True
        
        self._init_gui()

        self.reload_settings_file()

    def _init_gui(self):
        self.statusbar = QtGui.QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.menubar = QtGui.QMenuBar()
        self.setMenuBar(self.menubar)
        self.menubar.setNativeMenuBar(False)    # keep menubar in the window
        
        self.history = ''
        self.historyPane = QtGui.QPlainTextEdit()
        self.setCentralWidget(self.historyPane)
        self.historyPane.setLineWrapMode(False)
        self.historyPane.setReadOnly(True)
        self.toggleDebug(DEBUG)
        self.auto_scroll = True
        if self.debug:
            self.resize(500,300)
            self.historyPane.setStyleSheet("background: " + DEBUG_COLOR_ON)
        else:
            self.hide_history_window()
            self.resize(400,0)
            self.historyPane.setStyleSheet("background: " + DEBUG_COLOR_OFF)

        self.process_responded.connect(self.historyUpdate)
        
        self.showStatus('starting %s ...' % sys.argv[0])
        
        self.admin_menu  = QtGui.QMenu('Help')
        self.menubar.addMenu(self.admin_menu)
        self.admin_menu.addAction('About ...', self.about_box)
        self.admin_menu.addSeparator()
        self.admin_menu.addAction('Reload User Menus', self.reload_settings_file)
        self.admin_menu.addSeparator()
        self.admin_menu.addAction('(Un)hide history panel', self.hide_history_window)
        self.admin_menu.addAction('scroll to new output', self.toggleAutoScroll)
        self.admin_menu.addAction('command echo', self.toggleEcho)
        self.admin_menu.addAction('toggle Debug flag', self.toggleDebug)
        self.user_menus = OrderedDict()

    def receiver(self, label, command):
        '''handle commands from menu button'''
        msg = MAIN_SECTION_LABEL + ' (' + timestamp() + '), ' + label
        if command is None:
            msg += ': '
        else:
            command = os.path.normpath(command)
        msg += ':  ' + str(command)
        self.showStatus(msg, isCommand=True)
        if command is not None:
            self.command_number += 1
            process_name = "id_" + str(self.command_number)
            
            # ref: https://docs.python.org/3.3/library/subprocess.html
            process = CommandThread()
            process.setName(process_name)
            process.setDebug(self.debug)
            process.setSignal(self.process_responded)
            process.setCommand(command)
            process.start()

    @QtCore.pyqtSlot()
    def toggleAutoScroll(self):
        """change whether (or not) to keep new output in view"""
        self.auto_scroll = not self.auto_scroll
        state = {True: "on", False: "off"}[self.auto_scroll]
        self.process_responded.emit("auto scroll: " + state)

    @QtCore.pyqtSlot()
    def toggleDebug(self, debug_state = None):
        """change whether (or not) to output diagnostic information"""
        if debug_state is not None:
            self.debug = debug_state
        else:
            self.debug = not self.debug
        color = {True: DEBUG_COLOR_ON, False: DEBUG_COLOR_OFF}[self.debug]
        self.historyPane.setStyleSheet("background: " + color)

    @QtCore.pyqtSlot()
    def toggleEcho(self):
        """change whether (or not) to echo command before running it"""
        self.command_echo = not self.command_echo
        state = {True: "on", False: "off"}[self.command_echo]
        self.process_responded.emit("command echo: " + state)

    def about_box(self):
        '''TODO: should display an About box'''
        from bcdamenu import __version__, __url__
        # TODO: issue #13
        msg = __doc__.strip()
        msg += '\n  version: ' + __version__
        msg += '\n  URL: ' + __url__
        self.showStatus(msg)
    
    def showStatus(self, text, isCommand=False):
        """write to the status bar"""
        self.statusbar.showMessage(text.splitlines()[0])
        if isCommand and self.command_echo:
            self.historyUpdate(text)

    def historyUpdate(self, text):
        """record history where user can see it"""
        if len(self.history) != 0:
            self.history += '\n'
        self.history += text
        if self.historyPane is not None:
            self.historyPane.appendPlainText(text)
            if self.auto_scroll:
                self.historyPane.ensureCursorVisible()

    def hide_history_window(self):
        """toggle the visibility of the history panel"""
        self.historyPane.setHidden(not self.historyPane.isHidden())
    
    def reload_settings_file(self):
        '''(re)load the settings file and (re)create the menu(s)'''
        self.showStatus('(re)load settings: ' + self.settingsfilename)

        # read the settings file (again)
        self.config = read_settings(self.settingsfilename)
  
        # install the new user popup menu buttons
        self.menubar.clear()
        self.user_menus = OrderedDict()
        self.build_user_menus(self.config)
        self.menubar.addMenu(self.admin_menu)
        self.setWindowTitle(self.config['title'])

    def build_user_menus(self, config):
        """build the user menus"""
        for menu_name in config['menus']:
            menu = QtGui.QMenu(menu_name)
            self.user_menus[menu_name] = menu

            # fallback to empty list if not found
            config_list = config.get(menu_name, [])
            for entry in config_list:
                k, v = entry
                if k == 'title':
                    menu.setTitle(v)
                elif k == 'separator' and v is None:
                    menu.addSeparator()
                else:
                    action = menu.addAction(k, partial(self.receiver, k, v))
            self.menubar.addMenu(menu)

    @QtCore.pyqtSlot(QtGui.QCloseEvent)
    def closeEvent(self, event):
        # TODO: dispose any threads and timers
        pass


class CommandThread(threading.Thread):
    """
    run the command as a subprocess in its own thread, report any output
    """

    subprocess_parameters = {
        'bufsize': 1,
        'shell': True,
        'stderr': subprocess.STDOUT,
        'stdout': subprocess.PIPE,
        'universal_newlines': True,
    }

    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)
        self.signal = None
        self.command = None
    
    def setCommand(self, command):
        """user's command to be run"""
        self.command = command
    
    def setDebug(self, value):
        """`True` to output more diagnostics"""
        self.debug = value

    def setSignal(self, signal):
        """designate the signal to use when subprocess output has been received"""
        self.signal = signal

    def run(self):
        """print any/all output when command is run"""
        for line in self.execute():
            if self.debug:
                line = " ".join(self.name, timestamp(), line)
            self.signal.emit(line)

    def execute(self):
        """run the command in a shell, reporting its output as it comes in"""
        with subprocess.Popen(self.command, **self.subprocess_parameters) as process:
            if self.debug:
                yield self.name + " started"
            for buffer in iter(process.stdout.readline, ""):
                for line in buffer.splitlines():
                    yield line
            if self.debug:
                yield self.name + " started"


def read_settings(ini_file):
    '''
    read the user menu settings from the .ini file
    '''
    if not os.path.exists(ini_file):
        raise ValueError('settings file not found: ' + ini_file)

    config = iniParser.ConfigParser(allow_no_value=True)
    config.optionxform = str    # do not make labels lower case
    config.read(ini_file)
    
    settings = dict(title=MAIN_SECTION_LABEL, menus='', version='unknown')
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
    app = QtGui.QApplication(sys.argv)
    the_gui = MainButtonWindow(settingsfilename=settingsfilename)
    the_gui.show()
    sys.exit(app.exec_())


def timestamp():
    """ISO8601-compliant date & time string"""
    return str(datetime.datetime.now())


def main():
    '''process any command line options before starting the GUI'''
    import __init__
    version = __init__.__version__
    doc = __doc__.strip().splitlines()[0]
    doc += '\n  v' + version
    parser = argparse.ArgumentParser(prog=MAIN_SECTION_LABEL, description=doc)
    parser.add_argument('settingsfile', help="Settings file (.ini)")
    parser.add_argument('-v', '--version', action='version', version=version)
    params = parser.parse_args()

    if not os.path.exists(params.settingsfile):
        raise IOError('file not found: ' + params.settingsfile)

    gui(settingsfilename = params.settingsfile)


if __name__ == '''__main__''':
    main()
