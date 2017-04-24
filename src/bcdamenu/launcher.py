#!/usr/bin/env python

'''
BcdaMenu: Creates a GUI menu button to start common beam line software
'''

import argparse
from collections import OrderedDict
import datetime
from functools import partial
import os
import shlex
import sys
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
DEBUG_COLOR_OFF = "white"
DEBUG_COLOR_ON = "#fec"
OUTPUT_POLL_INTERVAL_MS = 50    # any way to avoid polling?


class MainButtonWindow(QtGui.QMainWindow):
    '''the widget that holds the menu button'''

    process_responded = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, settingsfilename=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.settingsfilename = settingsfilename
        if settingsfilename is None:
            raise ValueError('settings file name must be given')
        
        self.command_number = 0
        self.process_dict = {}
        self.timer_dict = {}
        self.debug = DEBUG

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
        self.admin_menu.addAction('toggle Debug flag', self.toggleDebug)
        self.user_menus = OrderedDict()

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
        self.showStatus(msg)
        if command is not None:
            self.command_number += 1
            process_name = "id_" + str(self.command_number)
            
            # ref: https://docs.python.org/3.3/library/subprocess.html
            args = shlex.split(str(command))
            process = subprocess.Popen(
                args,
                shell = True,
                stderr = subprocess.STDOUT,
                stdout = subprocess.PIPE,
                universal_newlines = True,
            )

            self.process_dict[process_name] = process
            timer = QtCore.QTimer()
            self.timer_dict[process_name] = timer
            timer.setSingleShot(False)
            timer.timeout.connect(partial(self.process_reporter, process_name))
            timer.start(OUTPUT_POLL_INTERVAL_MS)
            if self.debug:
                msg = " ".join([process_name, str(datetime.datetime.now()), "started"])
                self.process_responded.emit(msg)


    @QtCore.pyqtSlot(str)
    def process_reporter(self, proc_name):
        """write any process output to history"""
        if proc_name in self.process_dict:
            process = self.process_dict[proc_name]
            buffer = process.stdout.read()
            if len(buffer) > 0:
                for line in buffer.splitlines():
                    if self.debug:
                        line = " ".join([proc_name, str(datetime.datetime.now()), line])
                    self.process_responded.emit(line)
            result = process.poll()
            if result is not None:
                if self.debug:
                    msg = " ".join([proc_name, str(datetime.datetime.now()), "ended"])
                    self.process_responded.emit(msg)
                del self.process_dict[proc_name]
                if proc_name in self.timer_dict:
                    self.timer_dict[proc_name].stop()
                    del self.timer_dict[proc_name]
    
    @QtCore.pyqtSlot()
    def toggleDebug(self):
        self.debug = not self.debug
        color = {True: DEBUG_COLOR_ON, False: DEBUG_COLOR_OFF}[self.debug]
        self.historyPane.setStyleSheet("background: " + color)

    def _writeBufferToHistory(self, proc_id, caller_name = None):
        process = self.process_dict[proc_id]
        if self.debug:
            self.process_responded.emit("state: " + str(process.state()))
        buffer = process.readAll()
        for line in str(buffer).splitlines():
            msg = line
            if self.debug:
                msg = caller_name + ": " + line
            self.process_responded.emit(msg)
            if self.debug:
                print(' '.join([proc_id, caller_name, str(datetime.datetime.now()), line]))

    @QtCore.pyqtSlot(str)
    def onError(self, proc_id):
        self.process_responded.emit("error: " + proc_id)
        if proc_id in self.process_dict:
            self._writeBufferToHistory(proc_id, "onError")
            self.process_responded.emit("error string: " + self.process_dict[proc_id].errorString())

            self.process_responded.emit("last error code: " + str(self.process_dict[proc_id].error()))
            self.process_responded.emit("exitCode: " + str(self.process_dict[proc_id].exitCode()))
            self.process_responded.emit("exitStatus: " + str(self.process_dict[proc_id].exitStatus()))
    
    @QtCore.pyqtSlot(str)
    def onStart(self, proc_id):
        if self.debug:
            self.process_responded.emit("start: " + proc_id)
 
    @QtCore.pyqtSlot(str)
    def onUpdate(self, proc_id):
        if proc_id not in self.process_dict:
            msg = proc_id + ' not found during update event!'
            raise RuntimeError(msg)
        if self.debug:
            self._writeBufferToHistory(proc_id, "onUpdate")
        else:
            self._writeBufferToHistory(proc_id)
 
    @QtCore.pyqtSlot(str)
    def onFinish(self, proc_id):
        if proc_id in self.process_dict:
            self._writeBufferToHistory(proc_id, "onFinish")

            if self.debug:
                self.process_responded.emit("last error string: " + self.process_dict[proc_id].errorString())
                self.process_responded.emit("last error code: " + str(self.process_dict[proc_id].error()))
                self.process_responded.emit("exitCode: " + str(self.process_dict[proc_id].exitCode()))
                self.process_responded.emit("exitStatus: " + str(self.process_dict[proc_id].exitStatus()))

            del self.process_dict[proc_id]
            if self.debug:
                self.showStatus(proc_id + ' ended')
        else:
            self.showStatus(proc_id + ' ended but not found in db')

    @QtCore.pyqtSlot(str, int)
    def onStateChanged(self, process_name, state_number):
        states = ["NotRunning", "Starting", "Running"]
        if self.debug:
            print("change: ", process_name, states[state_number])

    def about_box(self):
        '''TODO: should display an About box'''
        from bcdamenu import __version__, __url__
        # TODO: issue #13
        msg = __doc__.strip()
        msg += '\n  version: ' + __version__
        msg += '\n  URL: ' + __url__
        self.showStatus(msg)
    
    def showStatus(self, text):
        """write to the status bar"""
        self.statusbar.showMessage(text.splitlines()[0])
        self.historyUpdate(text)

    def historyUpdate(self, text):
        """record history where user can see it"""
        if len(self.history) != 0:
            self.history += '\n'
        self.history += text
        if self.historyPane is not None:
            self.historyPane.appendPlainText(text)

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
        # delete any subprocesses as application exits
        for k, process in self.process_dict.items():
            process.close()
        self.process_dict = {}


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
    app = QtGui.QApplication(sys.argv)
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
