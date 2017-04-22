#!/usr/bin/env python

'''
test capturing output from multiple processes
'''


import datetime
from functools import partial
import os
import sys
from time import sleep
from PyQt4 import QtGui, QtCore

CAGET = "/usr/local/epics/base/bin/linux-x86_64/caget"
CAMONITOR = "/usr/local/epics/base/bin/linux-x86_64/camonitor"
COMMAND_TIME          = CAGET + " xxx:iso8601"
COMMAND_TEMPERATURE   = CAGET + " garpi:mega:temperature"
COMMAND_HUMIDITY      = CAGET + " garpi:mega:humidity"


class MyExample(QtCore.QObject):

    signal_response = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.command_number = 0
        self.process_dict = {}

        self.gui = Window()
        self._connectSignals()
        self.gui.show()
     
    def _connectSignals(self):
        # actions
        self.gui.b_time.clicked.connect(partial(self.os_command, COMMAND_TIME))
        self.gui.b_temperature.clicked.connect(partial(self.os_command, COMMAND_TEMPERATURE))
        self.gui.b_humidity.clicked.connect(partial(self.os_command, COMMAND_HUMIDITY))

        # responses
        self.signal_response.connect(self.gui.updateStatus)
    
    def os_command(self, command):
        # self.signal_response.emit(str(command))
        self.worker_qprocess(command)
    
    def worker_qprocess(self, command):
        '''handle commands using subprocess'''
        process = QtCore.QProcess(self)
        self.command_number += 1
        process_name = "id_" + str(self.command_number)
        self.process_dict[process_name] = process
        
        process.setReadChannel(QtCore.QProcess.StandardOutput)
        # process.started.connect(partial(self.onStart, process_name))
        process.finished.connect(partial(self.onFinish, process_name))
        # process.stateChanged.connect(partial(self.onStateChanged, process_name))
        process.readyRead.connect(partial(self.onUpdate, process_name))

        status = process.start(command)
        # print("status: " + str(status))
    
    def onStart(self, process_name):
        print("start: " + str(process_name))
    
    def onFinish(self, process_name):
        if process_name in self.process_dict:
            del self.process_dict[process_name]
    
    def onStateChanged(self, process_name, state_number):
        states = ["NotRunning", "Starting", "Running"]
        print("change: ", process_name, states[state_number])
    
    @QtCore.pyqtSlot(str)
    def onUpdate(self, process_name):
        if process_name in self.process_dict:
            process = self.process_dict[process_name]
            msg = str(process.readAllStandardOutput()).strip()
            self.signal_response.emit(msg)
            print(str(datetime.datetime.now()) + ' ' + msg)


class Window(QtGui.QWidget):

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.b_time = QtGui.QPushButton('time', self)
        self.b_temperature = QtGui.QPushButton('temperature', self)
        self.b_humidity = QtGui.QPushButton('humidity', self)
        self.l_status = QtGui.QLabel('', self)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.b_time)
        layout.addWidget(self.b_temperature)
        layout.addWidget(self.b_humidity)
        layout.addWidget(self.l_status)

        self.setFixedSize(400, 200)

    @QtCore.pyqtSlot(str)
    def updateStatus(self, status):
        self.l_status.setText(status)


def command(processor, cmd):
    print("command: " + cmd)
    processor.receiver(cmd)


if __name__ == "__main__":
    # my_example = MyExample()
    # for i in range(30):
    #     print("iteration " + str(i))
    #     if i == 0:
    #         command(my_example, "camonitor xxx:iso8601")
    #     elif i == 4:
    #         command(my_example, "camonitor garpi:mega:temperature")
    #     command(my_example, 'caget garpi:mega:humidity')
    #     sleep(2)

    app = QtGui.QApplication(sys.argv)
    example = MyExample(app)
    sys.exit(app.exec_())
