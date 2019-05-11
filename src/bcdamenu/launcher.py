#!/usr/bin/env python

# Copyright (c) 2009-2019, UChicago Argonne, LLC.
# See LICENSE.txt file for details.

'''
BcdaMenu: Creates a GUI menu button to start common software

.. autosummary::

    ~MainButtonWindow
    ~CommandThread
    ~read_settings
    ~gui
    ~timestamp
    ~main

'''

import argparse
from collections import OrderedDict
import datetime
from functools import partial
import os
import sys
import threading

try:
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

try:
    import subprocess32 as subprocess
except:
    import subprocess
from . import config_file_parser


MAIN_SECTION_LABEL = 'BcdaMenu'
DEBUG = False
#DEBUG = True
DEBUG_COLOR_OFF = "white"
DEBUG_COLOR_ON = "#fec"


class MainButtonWindow(QMainWindow):
    '''
    the widget that holds the menu button
    
    .. autosummary::

        ~receiver
        ~reload_settings_file
        ~build_user_menus
        ~showStatus
        ~historyUpdate
        ~toggleAutoScroll
        ~toggleDebug
        ~toggleEcho
        ~hide_history_window
        ~about_box
        ~closeEvent
    
    '''

    process_responded = pyqtSignal(str)

    def __init__(self, parent=None, settingsfilename=None):
        QMainWindow.__init__(self, parent)
        self.settingsfilename = settingsfilename
        if settingsfilename is None:
            raise ValueError('settings file name must be given')
        
        self.command_number = 0
        self.command_echo = True
        
        self._init_gui()

        self.reload_settings_file()

    def _init_gui(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.menubar = QMenuBar()
        self.setMenuBar(self.menubar)
        self.menubar.setNativeMenuBar(False)    # keep menubar in the window
        
        self.historyPane = QPlainTextEdit()
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
        
        self.admin_menu  = QMenu('Help')
        self.menubar.addMenu(self.admin_menu)
        self.admin_menu.addAction('About ...', self.about_box)
        self.admin_menu.addSeparator()
        self.admin_menu.addAction('&Reload User Menus', self.reload_settings_file)
        self.admin_menu.addSeparator()
        self.admin_menu.addAction('(Un)hide &History panel', self.hide_history_window)

        # keyboard shortcuts
        def shortcut(sequence, action):
            cut = QShortcut(QKeySequence(sequence), self)
            cut.activated.connect(action)
            return cut
        shortcut("Ctrl+R", self.reload_settings_file)
        shortcut("Ctrl+H", self.hide_history_window)
        shortcut("Ctrl+D", self.toggleDebug)
        
        action = self.admin_menu.addAction('scroll to new output', self.toggleAutoScroll)
        action.setCheckable(True)
        action.setChecked(self.auto_scroll)
        
        action = self.admin_menu.addAction('command echo', self.toggleEcho)
        action.setCheckable(True)
        action.setChecked(self.command_echo)
        
        action = self.admin_menu.addAction('toggle &Debug flag', self.toggleDebug)
        action.setCheckable(True)
        action.setChecked(self.debug)
        
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

    @pyqtSlot()
    def toggleAutoScroll(self):
        """change whether (or not) to keep new output in view"""
        self.auto_scroll = not self.auto_scroll
        state = {True: "on", False: "off"}[self.auto_scroll]
        self.process_responded.emit("auto scroll: " + state)

    @pyqtSlot()
    def toggleDebug(self, debug_state = None):
        """change whether (or not) to output diagnostic information"""
        if debug_state is not None:
            self.debug = debug_state
        else:
            self.debug = not self.debug
        color = {True: DEBUG_COLOR_ON, False: DEBUG_COLOR_OFF}[self.debug]
        self.historyPane.setStyleSheet("background: " + color)

    @pyqtSlot()
    def toggleEcho(self):
        """change whether (or not) to echo command before running it"""
        self.command_echo = not self.command_echo
        state = {True: "on", False: "off"}[self.command_echo]
        self.process_responded.emit("command echo: " + state)

    def about_box(self):
        '''display an About box'''
        from .__init__ import (__version__, __url__, __author__, 
                __issues__, __copyright__, __license_url__)
        from . import about
        print("DEBUG: about file:" + about.__file__)
        summary = __doc__.strip().splitlines()[0]  # 1st line only
        msg = summary
        msg += '\n  version: ' + __version__
        msg += '\n  URL: ' + __url__
        self.showStatus(msg)

        ui = about.InfoBox(self)

        ui.setTodoURL(__issues__)
        ui.setDocumentationURL(__url__)
        ui.setLicenseURL(__license_url__)
        ui.setTitle(config_file_parser.MAIN_SECTION_LABEL)
        ui.setVersionText("software version: " + __version__)
        ui.setSummaryText(summary)
        ui.setAuthorText(__author__)
        ui.setCopyrightText(__copyright__)

        ui.show()
    
    def showStatus(self, text, isCommand=False):
        """write to the status bar"""
        self.statusbar.showMessage(text.splitlines()[0])
        if not isCommand and self.command_echo:
            self.historyUpdate(text)

    def historyUpdate(self, text):
        """record history where user can see it"""
        if self.historyPane is not None:
            self.historyPane.appendPlainText(text)
            if self.auto_scroll:
                self.historyPane.ensureCursorVisible()
                scroll = self.historyPane.verticalScrollBar()
                scroll.setValue(scroll.maximum())

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
    
    def _build_menu(self, menu, widget):
        for k, v in menu.itemDict.items():
            if isinstance(v, config_file_parser.MenuItem):
                action = widget.addAction(
                    v.label, 
                    partial(self.receiver, v.label, v.command))
            elif isinstance(v, config_file_parser.MenuSeparator):
                widget.addSeparator()
            elif isinstance(v, config_file_parser.Menu):
                subwidget = QMenu(v.title)
                self.user_menus[v.sectionName] = subwidget
                self._build_menu(v, subwidget)
                widget.addMenu(subwidget)
            else:
                raise RuntimeError("unexpected: %s : " % k + str(v))

    def build_user_menus(self, config):
        """build the user menus"""
        for menu in config['menus']:
            widget = QMenu(menu.title)
            self.user_menus[menu.sectionName] = widget
            self._build_menu(menu, widget)
            self.menubar.addMenu(widget)

    @pyqtSlot(QCloseEvent)
    def closeEvent(self, event):
        # TODO: dispose any threads and timers
        pass


class CommandThread(threading.Thread):
    """
    run the command as a subprocess in its own thread, report any output
    
    **Usage**
    
    ::
    
            process = CommandThread()
            process.setName(process_name)
            process.setDebug(self.debug)
            process.setSignal(self.process_responded)
            process.setCommand(command)
            process.start()

    :see: https://docs.python.org/3.3/library/subprocess.html

    **Methods**
    
    .. autosummary::

        ~run
        ~execute
        ~setCommand
        ~setDebug
        ~setSignal
    
    """

    kwargs = {
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
        self.debug = False
        self.command = None
        if os.name == 'nt':     # Windows
            self.kwargs['shell'] = False
    
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
        if self.debug:
            self.signal.emit("thread %s starting" % self.name)
        for line in self.execute():
            if self.debug:
                line = " ".join([self.name, timestamp(), ":", line])
            self.signal.emit(line)
        if self.debug:
            self.signal.emit("thread %s ended" % self.name)

    def execute(self):
        """run the command in a shell, reporting its output as it comes in"""
        if self.debug:
            yield self.name + " started"
        process = subprocess.Popen(self.command, **self.kwargs)
        while not process.stdout.closed:
            stdoutdata, stderrdata = process.communicate()
            if stdoutdata is not None:
                for line in stdoutdata.splitlines():
                    yield line
        if self.debug:
            yield self.name + " finished"
        # try:
        #     with subprocess.Popen(self.command, **self.kwargs) as process:
        #         if self.debug:
        #             yield self.name + " started"
        #         for buffer in iter(process.stdout.readline, ""):
        #             for line in buffer.splitlines():
        #                 yield line
        #         if self.debug:
        #             yield self.name + " finished"
        # except AttributeError:      # happens on Windows
        #     pass


def read_settings(ini_file):
    '''
    read the user menu settings from the .ini file
    '''
    if not os.path.exists(ini_file):
        raise ValueError('settings file not found: ' + ini_file)

    settings = config_file_parser.readConfigFile(ini_file)
    return settings


def gui(settingsfilename = None):
    '''display the main widget'''
    app = QApplication(sys.argv)
    the_gui = MainButtonWindow(settingsfilename=settingsfilename)
    the_gui.show()
    sys.exit(app.exec_())


def timestamp():
    """ISO8601-compliant date & time string"""
    return str(datetime.datetime.now())


def main():
    '''process any command line options before starting the GUI'''
    from .__init__ import __version__
    version = __version__
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
