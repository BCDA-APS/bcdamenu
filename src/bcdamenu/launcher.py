#!/usr/bin/env python

'''
BcdaMenu: Creates a GUI menu button to start common beam line software
'''

import argparse
from collections import OrderedDict
import datetime
try:
    import configparser as iniParser
except:
    import ConfigParser as iniParser
from functools import partial
import os
import subprocess
import sys
from threading import Thread
from PyQt4 import QtGui, QtCore
from six import StringIO


MAIN_SECTION_LABEL = 'BcdaMenu'


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
        self.environment = QtCore.QProcessEnvironment().systemEnvironment()

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
        #self.hide_history_window()
        #self.resize(300,0)

        self.process_responded.connect(self.historyUpdate)
        
        self.showStatus('starting %s ...' % sys.argv[0])
        
        self.admin_menu  = QtGui.QMenu('Help')
        self.menubar.addMenu(self.admin_menu)
        self.admin_menu.addAction('About ...', self.about_box)
        self.admin_menu.addSeparator()
        self.admin_menu.addAction('Reload User Menus', self.reload_settings_file)
        self.admin_menu.addAction('(Un)Hide history window', self.hide_history_window)
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

            process = QtCore.QProcess(self)
            self.process_dict[process_name] = process
            
            process.setReadChannel(QtCore.QProcess.StandardOutput)
            process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
            process.setProcessEnvironment(self.environment)
    
            process.error.connect(partial(self.onError, process_name))
            process.started.connect(partial(self.onStart, process_name))
            # process.stateChanged.connect(partial(self.onStateChanged, process_name))
            process.readyRead.connect(partial(self.onUpdate, process_name))
            process.finished.connect(partial(self.onFinish, process_name))
    
            status = process.start(command)
            self.process_responded.emit("state: " + str(process.state()))
            self.process_responded.emit("pid: " + str(process.pid()))
    
    def _writeBufferToHistory(self, proc_id, caller_name):
        process = self.process_dict[proc_id]
        self.process_responded.emit("state: " + str(process.state()))
        buffer = process.readAll()
        for line in str(buffer).splitlines():
            self.process_responded.emit(caller_name + ": " + line)
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
        self.process_responded.emit("start: " + proc_id)
 
    @QtCore.pyqtSlot(str)
    def onUpdate(self, proc_id):
        if proc_id not in self.process_dict:
            msg = proc_id + ' not found during update event!'
            raise RuntimeError(msg)
        self._writeBufferToHistory(proc_id, "onUpdate")
 
    @QtCore.pyqtSlot(str)
    def onFinish(self, proc_id):
        if proc_id in self.process_dict:
            self._writeBufferToHistory(proc_id, "onFinish")

            self.process_responded.emit("last error string: " + self.process_dict[proc_id].errorString())
            self.process_responded.emit("last error code: " + str(self.process_dict[proc_id].error()))
            self.process_responded.emit("exitCode: " + str(self.process_dict[proc_id].exitCode()))
            self.process_responded.emit("exitStatus: " + str(self.process_dict[proc_id].exitStatus()))

            del self.process_dict[proc_id]
            self.showStatus(proc_id + ' ended')
        else:
            self.showStatus(proc_id + ' ended but not found in db')

    @QtCore.pyqtSlot(str, int)
    def onStateChanged(self, process_name, state_number):
        states = ["NotRunning", "Starting", "Running"]
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
