import binascii
import os
from collections import OrderedDict

import libscrc
import numpy as np
from PyQt5.QtCore import QTimer, QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QDoubleSpinBox, QGridLayout, QVBoxLayout, QLineEdit, QTextEdit, QWidget, QComboBox, \
    QHBoxLayout, QSpinBox, QPushButton, QFormLayout, QGroupBox, QRadioButton, QButtonGroup, QCheckBox, QFrame, \
    QMessageBox

from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget, QDMComboBox
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.utils_no_qt import *
from nodeeditor.var_type_conf import *

import serial
import serial.tools.list_ports

import platform
import os
from datetime import datetime
from time import time, sleep


class SerialParameters:
    def __init__(self, port=None, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE, timeout=0.3, xonxoff=False, rtscts=False,
                 write_timeout=1, dsrdtr=False, inter_byte_timeout=1, exclusive=None,
                 local_echo=False, appendCR=False, appendLF=False):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.xonxoff = xonxoff
        self.rtscts = rtscts
        self.write_timeout = write_timeout
        self.dsrdtr = dsrdtr
        self.inter_byte_timeout = inter_byte_timeout
        self.exclusive = exclusive
        self.readTextIndex = "read_line"
        self.readBytes = 1
        self.readUntil = ''
        self.DTR = False
        self.maxSignalRate = 5  # Hz
        self.Kennbin = ""

        self.local_echo = local_echo
        self.appendCR = appendCR
        self.appendLF = appendLF

    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('port', self.port),
            ('baudrate', self.baudrate),
            ('bytesize', self.bytesize),
            ('parity', self.parity),
            ('stopbits', self.stopbits),
            ('timeout', self.timeout),
            ('xonxoff', self.xonxoff),
            ('rtscts', self.rtscts),
            ('write_timeout', self.write_timeout),
            ('dsrdtr', self.dsrdtr),
            ('inter_byte_timeout', self.inter_byte_timeout),
            ('exclusive', self.exclusive),
            ('readTextIndex', self.readTextIndex),
            ('readBytes', self.readBytes),
            ('readUntil', self.readUntil),
            ('DTR', self.DTR),
            ('maxSignalRate', self.maxSignalRate),
            ('Kennbin', self.Kennbin),
            ('local_echo', self.local_echo),
            ('appendCR', self.appendCR),
            ('appendLF', self.appendLF),
        ])

    def deserialize(self, data: dict) -> bool:
        self.port = data["port"]
        self.baudrate = data["baudrate"]
        self.bytesize = data["bytesize"]
        self.parity = data["parity"]
        self.stopbits = data["stopbits"]
        self.timeout = data["timeout"]
        self.xonxoff = data["xonxoff"]
        self.rtscts = data["rtscts"]
        self.write_timeout = data["write_timeout"]
        self.dsrdtr = data["dsrdtr"]
        self.inter_byte_timeout = data["inter_byte_timeout"]
        self.exclusive = data["exclusive"]
        self.readTextIndex = data["readTextIndex"]
        self.readBytes = data["readBytes"]
        self.readUntil = data["readUntil"]
        self.DTR = data["DTR"]
        self.maxSignalRate = data["maxSignalRate"]
        self.Kennbin = data["Kennbin"]

        self.local_echo = data["local_echo"]
        self.appendCR = data["appendCR"]
        self.appendLF = data["appendLF"]
        return True


class SerialConnectWindow(QWidget):
    def __init__(self, serialParam: SerialParameters):
        super().__init__()

        self.setWindowTitle("Port connection")

        # __________ Port Configuration Group Box __________
        portLabel = QLabel("Port")
        baudrateLabel = QLabel("Baud rate")
        dataBitsLabel = QLabel("Data bits")
        stopBitsLabel = QLabel("Stop bits")
        parityLabel = QLabel("Parity")
        flowControlLabel = QLabel("Flow control")

        self.portCombobox = QComboBox()
        self.portCombobox.setEditable(True)
        self.portCombobox.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        for port in serial.tools.list_ports.comports():
            self.portCombobox.addItem(port.name)
        if self.portCombobox.findText(serialParam.port) > -1:
            self.portCombobox.setCurrentText(serialParam.port)

        self.baudrateCombobox = QComboBox()
        self.baudrateCombobox.setEditable(True)
        self.baudrateCombobox.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.baudrateCombobox.addItem("300")
        self.baudrateCombobox.addItem("1200")
        self.baudrateCombobox.addItem("2400")
        self.baudrateCombobox.addItem("4800")
        self.baudrateCombobox.addItem("9600")
        self.baudrateCombobox.addItem("19200")
        self.baudrateCombobox.addItem("38400")
        self.baudrateCombobox.addItem("57600")
        self.baudrateCombobox.addItem("74880")
        self.baudrateCombobox.addItem("115200")
        self.baudrateCombobox.addItem("230400")
        self.baudrateCombobox.addItem("250000")
        self.baudrateCombobox.addItem("500000")
        self.baudrateCombobox.addItem("1000000")
        self.baudrateCombobox.addItem("2000000")
        if self.baudrateCombobox.findText(str(serialParam.baudrate)) > -1:
            self.baudrateCombobox.setCurrentText(str(serialParam.baudrate))

        self.dataBitsCombobox = QComboBox()
        self.dataBitsCombobox.addItem("5")
        self.dataBitsCombobox.addItem("6")
        self.dataBitsCombobox.addItem("7")
        self.dataBitsCombobox.addItem("8")
        self.dataBitsCombobox.setCurrentText(str(serialParam.bytesize))

        self.stopBitsCombobox = QComboBox()
        self.stopBitsCombobox.addItem("1")
        self.stopBitsCombobox.addItem("1.5")
        self.stopBitsCombobox.addItem("2")
        self.stopBitsCombobox.setCurrentText(str(serialParam.stopbits))

        self.parityCombobox = QComboBox()
        self.parityCombobox.addItem("none")
        self.parityCombobox.addItem("even")
        self.parityCombobox.addItem("odd")
        self.parityCombobox.addItem("mark")
        self.parityCombobox.addItem("space")
        self.parityCombobox.setCurrentText(serialParam.parity)

        self.flowControlCombobox = QComboBox()
        self.flowControlCombobox.addItem("none")
        self.flowControlCombobox.addItem("xonxoff")
        self.flowControlCombobox.addItem("rtscts")
        self.flowControlCombobox.addItem("dsrdtr")
        self.flowControlCombobox.setCurrentText("none")
        if serialParam.xonxoff:
            self.flowControlCombobox.setCurrentText("xonxoff")
        if serialParam.rtscts:
            self.flowControlCombobox.setCurrentText("rtscts")
        if serialParam.dsrdtr:
            self.flowControlCombobox.setCurrentText("dsrdtr")

        portConfigLayout = QFormLayout()
        portConfigLayout.addRow(portLabel, self.portCombobox)
        portConfigLayout.addRow(baudrateLabel, self.baudrateCombobox)
        portConfigLayout.addRow(dataBitsLabel, self.dataBitsCombobox)
        portConfigLayout.addRow(stopBitsLabel, self.stopBitsCombobox)
        portConfigLayout.addRow(parityLabel, self.parityCombobox)
        portConfigLayout.addRow(flowControlLabel, self.flowControlCombobox)

        portConfigGroupbox = QGroupBox("Port configuration")
        portConfigGroupbox.setLayout(portConfigLayout)

        # __________ Transmitted Text Group Box __________
        self.appendNothingRB = QRadioButton("Append nothing")
        self.appendCRRB = QRadioButton("Append CR")
        self.appendLFRB = QRadioButton("Append LF")
        self.appendCRLFRB = QRadioButton("Append CR-LF")

        appendButtonGroup = QButtonGroup()
        appendButtonGroup.addButton(self.appendNothingRB)
        appendButtonGroup.addButton(self.appendCRRB)
        appendButtonGroup.addButton(self.appendLFRB)
        appendButtonGroup.addButton(self.appendCRLFRB)

        if not serialParam.appendCR and not serialParam.appendLF: self.appendNothingRB.setChecked(True)
        if serialParam.appendCR and not serialParam.appendLF: self.appendCRRB.setChecked(True)
        if not serialParam.appendCR and serialParam.appendLF: self.appendLFRB.setChecked(True)
        if serialParam.appendCR and serialParam.appendLF: self.appendCRLFRB.setChecked(True)

        self.localEchoCB = QCheckBox("Local echo")
        self.localEchoCB.setChecked(serialParam.local_echo)

        transmittedTextVLayout = QVBoxLayout()
        transmittedTextVLayout.addWidget(self.appendNothingRB)
        transmittedTextVLayout.addWidget(self.appendCRRB)
        transmittedTextVLayout.addWidget(self.appendLFRB)
        transmittedTextVLayout.addWidget(self.appendCRLFRB)
        transmittedTextVLayout.addWidget(self.localEchoCB)

        transmittedTextGroupbox = QGroupBox("Transmitted text")
        transmittedTextGroupbox.setLayout(transmittedTextVLayout)

        # __________ Received Text Group Box __________
        timeoutLabel = QLabel("Timeout [s]")

        self.timeoutCombobox = QComboBox()
        self.timeoutCombobox.setEditable(True)
        self.timeoutCombobox.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.timeoutCombobox.addItem("none")
        self.timeoutCombobox.addItem("0")
        self.timeoutCombobox.addItem("0.1")
        self.timeoutCombobox.addItem("0.2")
        self.timeoutCombobox.addItem("0.3")
        self.timeoutCombobox.addItem("0.4")
        self.timeoutCombobox.addItem("0.5")
        self.timeoutCombobox.addItem("1")
        self.timeoutCombobox.addItem("1.5")
        self.timeoutCombobox.addItem("2")
        self.timeoutCombobox.addItem("3")
        self.timeoutCombobox.addItem("4")
        self.timeoutCombobox.addItem("5")
        self.timeoutCombobox.addItem("10")
        self.timeoutCombobox.setCurrentText(str(serialParam.timeout))

        self.readLinesRB = QRadioButton("Read line")
        self.readBytesRB = QRadioButton("Read bytes")
        self.readUntilRB = QRadioButton("Read until")
        self.readWUDRB = QRadioButton('Read WU_Device')
        self.readLoggingRawRB = QRadioButton('Log Raw')
        self.readLinesRB.setChecked(True)
        self.readLinesRB.toggled.connect(self.changeReadTextAvailable)
        self.readWUDRB.toggled.connect(self.changeReadTextAvailable)
        self.readLoggingRawRB.toggled.connect(self.changeReadTextAvailable)
        self.readBytesRB.toggled.connect(self.changeReadTextAvailable)
        self.readUntilRB.toggled.connect(self.changeReadTextAvailable)
        if serialParam.readTextIndex == "read_line": self.readLinesRB.setChecked(True)
        if serialParam.readTextIndex == "read_WU_device": self.readWUDRB.setChecked(True)
        if serialParam.readTextIndex == "logging_raw": self.readLoggingRawRB.setChecked(True)
        if serialParam.readTextIndex == "read_bytes": self.readBytesRB.setChecked(True)
        if serialParam.readTextIndex == "read_until": self.readUntilRB.setChecked(True)

        self.readBytesSpinBox = QSpinBox()
        self.readBytesSpinBox.setRange(1, 1000)
        self.readUntilLineEdit = QLineEdit("?")
        self.readUntilLineEdit.setMaxLength(1)
        self.readUntilLineEdit.setFixedWidth(20)
        self.readBytesSpinBox.setEnabled(False)
        self.readUntilLineEdit.setEnabled(False)

        appendButtonGroup = QButtonGroup()
        appendButtonGroup.addButton(self.readLinesRB)
        appendButtonGroup.addButton(self.readWUDRB)
        appendButtonGroup.addButton(self.readLoggingRawRB)
        appendButtonGroup.addButton(self.readBytesRB)
        appendButtonGroup.addButton(self.readUntilRB)

        receivedTextLayout = QGridLayout()
        receivedTextLayout.addWidget(timeoutLabel, 0, 0, 1, 1)
        receivedTextLayout.addWidget(self.timeoutCombobox, 0, 1, 1, 1)
        receivedTextLayout.addWidget(self.readLinesRB, 1, 0, 1, 1)
        receivedTextLayout.addWidget(self.readWUDRB, 2, 0, 1, 1)
        receivedTextLayout.addWidget(self.readLoggingRawRB, 3, 0, 1, 1)
        receivedTextLayout.addWidget(self.readBytesRB, 4, 0, 1, 1)
        receivedTextLayout.addWidget(self.readBytesSpinBox, 4, 1, 1, 1)
        receivedTextLayout.addWidget(self.readUntilRB, 5, 0, 1, 1)
        receivedTextLayout.addWidget(self.readUntilLineEdit, 5, 1, 1, 1)

        receivedTextGroupbox = QGroupBox("Received text")
        receivedTextGroupbox.setLayout(receivedTextLayout)

        # __________ Options Group Box __________
        maxSignalRateLabel = QLabel("Max signal rate [Hz]")

        self.maxSignalRateSpinBox = QSpinBox()
        self.maxSignalRateSpinBox.setRange(1, 9999)
        self.maxSignalRateSpinBox.setValue(serialParam.maxSignalRate)

        optionsLayout = QFormLayout()
        optionsLayout.addRow(maxSignalRateLabel, self.maxSignalRateSpinBox)
        # optionsLayout.addWidget(-------------, 0, 0, 1, 1)

        optionsGroupbox = QGroupBox("Options")
        optionsGroupbox.setLayout(optionsLayout)

        horizontalLine = QFrame()
        horizontalLine.setFrameShape(QFrame.Shape.HLine)
        horizontalLine.setFrameShadow(QFrame.Shadow.Sunken)

        # __________ Submit Button Layout __________
        self.cancelButton = QPushButton("Cancel")
        self.okButton = QPushButton("OK")
        self.okButton.setAutoDefault(True)
        QTimer.singleShot(0, self.okButton.setFocus)

        submitButtonLayout = QHBoxLayout()
        submitButtonLayout.addWidget(self.okButton)
        submitButtonLayout.addWidget(self.cancelButton)

        # __________ Main Grid Layout __________
        gridLayout = QGridLayout()
        gridLayout.addWidget(portConfigGroupbox, 0, 0, 2, 1)
        gridLayout.addWidget(transmittedTextGroupbox, 0, 1, 1, 1)
        gridLayout.addWidget(receivedTextGroupbox, 1, 1, 1, 1)
        gridLayout.addWidget(optionsGroupbox, 0, 2, 2, 1)
        gridLayout.addWidget(horizontalLine, 3, 0, 1, 3)
        gridLayout.addLayout(submitButtonLayout, 4, 2, 1, 1)

        self.setLayout(gridLayout)

        # __________ QPushButton Function __________
        self.cancelButton.clicked.connect(self.close)

    def changeReadTextAvailable(self, checked: bool):
        if not checked:
            return
        if self.sender().text() == "Read line":
            self.readBytesSpinBox.setEnabled(False)
            self.readUntilLineEdit.setEnabled(False)
        elif self.sender().text() == 'Read WU_Device':
            self.readBytesSpinBox.setEnabled(False)
            self.readUntilLineEdit.setEnabled(False)
        elif self.sender().text() == "Read bytes":
            self.readBytesSpinBox.setEnabled(True)
            self.readUntilLineEdit.setEnabled(False)
        elif self.sender().text() == "Read until":
            self.readBytesSpinBox.setEnabled(False)
            self.readUntilLineEdit.setEnabled(True)

    def getSerialParameter(self):
        serialParam = SerialParameters()
        if self.portCombobox.currentText().strip() != "":
            serialParam.port = self.portCombobox.currentText()
        if isInt(self.baudrateCombobox.currentText()):
            serialParam.baudrate = returnInt(self.baudrateCombobox.currentText())
        if {"5": serial.FIVEBITS, "6": serial.SIXBITS, "7": serial.SEVENBITS, "8": serial.EIGHTBITS}.get(self.dataBitsCombobox.currentText()):
            serialParam.bytesize = {"5": serial.FIVEBITS, "6": serial.SIXBITS, "7": serial.SEVENBITS, "8": serial.EIGHTBITS}.get(self.dataBitsCombobox.currentText())
        if {"1": serial.STOPBITS_ONE, "1.5": serial.STOPBITS_ONE_POINT_FIVE, "2": serial.STOPBITS_TWO}.get(self.stopBitsCombobox.currentText()):
            serialParam.stopbits = {"1": serial.STOPBITS_ONE, "1.5": serial.STOPBITS_ONE_POINT_FIVE, "2": serial.STOPBITS_TWO}.get(self.stopBitsCombobox.currentText())
        if {"none": serial.PARITY_NONE, "even": serial.PARITY_EVEN, "odd": serial.PARITY_ODD, "mark": serial.PARITY_MARK, "space": serial.PARITY_SPACE}.get(self.parityCombobox.currentText()):
            serialParam.parity = {"none": serial.PARITY_NONE, "even": serial.PARITY_EVEN, "odd": serial.PARITY_ODD, "mark": serial.PARITY_MARK, "space": serial.PARITY_SPACE}.get(self.parityCombobox.currentText())
        if self.flowControlCombobox.currentText() == "xonxoff":
            serialParam.xonxoff = True
        if self.flowControlCombobox.currentText() == "rtscts":
            serialParam.rtscts = True
        if self.flowControlCombobox.currentText() == "dsrdtr":
            serialParam.dsrdtr = True
        if self.appendCRRB.isChecked():
            serialParam.appendCR = True
        if self.appendLFRB.isChecked():
            serialParam.appendLF = True
        if self.appendCRLFRB.isChecked():
            serialParam.appendCR = True
            serialParam.appendLF = True
        if self.localEchoCB.isChecked():
            serialParam.local_echo = True
        if isFloat(self.timeoutCombobox.currentText()):
            serialParam.timeout = returnFloat(self.timeoutCombobox.currentText())
        if self.readLinesRB.isChecked():
            serialParam.readTextIndex = "read_line"
        if self.readWUDRB.isChecked():
            serialParam.readTextIndex = "read_WU_device"
        if self.readLoggingRawRB.isChecked():
            serialParam.readTextIndex = "logging_raw"
        if self.readBytesRB.isChecked():
            serialParam.readTextIndex = "read_bytes"
            serialParam.readBytes = self.readBytesSpinBox.value()
        if self.readUntilRB.isChecked():
            serialParam.readTextIndex = "read_until"
            serialParam.readUntil = self.readUntilLineEdit.text()[0]
        serialParam.maxSignalRate = self.maxSignalRateSpinBox.value()

        return serialParam


class SerialSignals(QObject):
    # Signals
    receivedData = pyqtSignal(object, object)
    madeConnection = pyqtSignal(object)
    lostConnection = pyqtSignal(object)
    failedSendData = pyqtSignal(object, object)


class SerialThread(QRunnable):
    def __init__(self, serialParameters: SerialParameters):
        super().__init__()
        self.serialParameters = serialParameters
        self.serialArduino = serial.Serial()
        self.serialArduino.port = self.serialParameters.port
        self.serialArduino.baudrate = self.serialParameters.baudrate
        self.serialArduino.bytesize = self.serialParameters.bytesize
        self.serialArduino.parity = self.serialParameters.parity
        self.serialArduino.stopbits = self.serialParameters.stopbits
        self.serialArduino.timeout = self.serialParameters.timeout
        self.serialArduino.xonxoff = self.serialParameters.xonxoff
        self.serialArduino.rtscts = self.serialParameters.rtscts
        self.serialArduino.write_timeout = self.serialParameters.write_timeout
        self.serialArduino.dsrdtr = self.serialParameters.dsrdtr
        self.serialArduino.inter_byte_timeout = self.serialParameters.inter_byte_timeout
        self.serialArduino.exclusive = self.serialParameters.exclusive
        self.serialArduino.setDTR(self.serialParameters.DTR)

        self.signals = SerialSignals()
        self.is_killed = False
        self.is_paused = False
        self.lostConnectionTimer = -1

        self.recordingStarted = False
        self.record = False
        self.recordFilePath = os.getcwd() + "/test2.txt"
        self.lastRefreshTime = 0
        self.failCounter = 0

        self.lastRefreshTimeDict = {}

        if platform.system() == "Linux":
            self.serialArduino.port = "/dev/" + self.serialParameters.port


    @pyqtSlot()  # Decorator function to show that this method is a slot
    def run(self):
        if not self.serialArduino.isOpen():
            try:
                self.serialArduino.open()
                self.signals.madeConnection.emit(self.serialParameters)
            except:
                print("Connecting to: " + self.serialParameters.port + " failed")
                return None

        while not self.is_killed:
            if not self.is_paused:
                #try:
                    if self.serialArduino.isOpen():
                        if self.serialParameters.readTextIndex == "read_line":
                            readLine = self.read_line()  # self.serialArduino.readline()
                            if not readLine == b'':
                                #try:
                                #readLine.decode('utf-8')
                                #except UnicodeDecodeError as e:
                                #    if self.lostConnectionTimer == -1:
                                #        self.lostConnectionTimer = datetime.now().timestamp() + 1
                                #    if datetime.now().timestamp() > self.lostConnectionTimer:
                                #        print(e)
                                #        self.signals.lostConnection.emit(self.serialParameters)
                                #        return None
                                #    continue
                                if time() > self.lastRefreshTime + (1 / self.serialParameters.maxSignalRate):
                                    self.lastRefreshTime = time()
                                    self.signals.receivedData.emit(self.serialParameters, readLine)
                        elif self.serialParameters.readTextIndex == "read_bytes":
                            readLine = self.serialArduino.read(self.serialParameters.readBytes)
                            if not readLine == b'':
                                #try:
                                #    readLine.decode('utf-8')
                                #except UnicodeDecodeError as e:
                                #    print(e)
                                #    self.signals.lostConnection.emit(self.serialParameters)
                                #    return None
                                if time() > self.lastRefreshTime + (1 / self.serialParameters.maxSignalRate):
                                    self.lastRefreshTime = time()
                                    self.signals.receivedData.emit(self.serialParameters, readLine)
                        elif self.serialParameters.readTextIndex == "read_until":
                            readLine = self.serialArduino.read_until(
                                self.serialParameters.readUntil.encode('utf-8'))  # self.serialParameters.readUntil)
                            if not readLine == b'':
                                try:
                                    readLine.decode('utf-8')
                                except UnicodeDecodeError as e:
                                    print(e)
                                    self.signals.lostConnection.emit(self.serialParameters)
                                    return None
                                if time() > self.lastRefreshTime + (1 / self.serialParameters.maxSignalRate):
                                    self.lastRefreshTime = time()
                                    self.signals.receivedData.emit(self.serialParameters, readLine)
                        elif self.serialParameters.readTextIndex == "logging_raw":
                            with open('loggingRaw.txt', 'a') as file:
                                readChar = self.serialArduino.read(1)
                                if readChar != b'':
                                    file.write(str(readChar))
                        elif self.serialParameters.readTextIndex == "read_WU_device":
                            if self.serialArduino.read(1) == b'\xaa':
                                if self.serialArduino.read(1) == b'\x55':
                                    Kennbin = self.serialArduino.read(2)
                                    Kennung = int(binascii.hexlify(Kennbin[:1]), 16)
                                    readLine = self.serialArduino.read(2 * Kennung + 2 + 2)
                                    if not readLine == b'':
                                        crc16send = readLine[-2:]
                                        crc16 = libscrc.modbus(Kennbin + readLine[0:-2])
                                        crc_check = crc16 == int(binascii.hexlify(crc16send), 16)

                                        data = []
                                        for n in range(len(readLine) // 2):
                                            data.append(str(binascii.hexlify(readLine[2 * n:2 * n + 2]))[2:6])
                                        singleLine = np.asarray(data)
                                        if not crc_check:
                                            singleLine = np.append(singleLine, '4650')
                                            if self.record:
                                                self.failCounter += 1
                                        else:
                                            singleLine = np.append(singleLine, '4f4b')
                                        # if not crc_check:
                                        #     singleLine[-1] = 'aaaa'

                                        if self.record:
                                            self.recordData(singleLine)

                                        if Kennbin not in self.lastRefreshTimeDict:
                                            self.lastRefreshTimeDict[Kennbin] = 0

                                        if time() > self.lastRefreshTimeDict[Kennbin] + (1 / self.serialParameters.maxSignalRate):
                                            self.lastRefreshTimeDict[Kennbin] = time()
                                            self.serialParameters.Kennbin = Kennbin
                                            self.signals.receivedData.emit(self.serialParameters, singleLine)
                    else:
                        self.signals.lostConnection.emit(self.serialParameters)
                        return None
                #except Exception as e:
                #    try:
                #        print(e)
                #        self.signals.lostConnection.emit(self.serialParameters)
                #    except:
                #        pass
                #    return None
            # QApplication.processEvents()
        self.serialArduino.close()
        try:
            self.signals.lostConnection.emit(self.serialParameters)
        except:
            pass

    def startRecordData(self, port, filePath, fileName):
        if not port.upper() == "ALL" and not port.upper() == self.serialParameters.port.upper():
            return None
        if not os.path.exists(filePath):
            return None

        if self.recordingStarted:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Port already recording!")
            msg.setInformativeText('Stop current recording before starting a new one.')
            msg.setWindowTitle("Recording error")
            msg.exec_()
            return

        if filePath[-1] != "/":
            filePath += "/"
        if fileName.strip() == "":
            fileName += datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".txt"
        if port.upper() == "ALL":
            fileName = fileName.split(".")[0] + "_" + str(self.serialParameters.port) + ".txt"
        self.recordFilePath = filePath + fileName
        self.failCounter = 0
        self.recordingStarted = True
        self.record = True

        if self.serialParameters.readTextIndex == "read_WU_device":
            with open(self.recordFilePath, 'a') as file:
                file.write(float.hex(time()) + "\n")

    def stopRecordData(self, port):
        if not port.upper() == "ALL" and not port.upper() == self.serialParameters.port.upper():
            return None

        self.recordingStarted = False
        self.record = False

        if not self.recordingStarted:
            return None

        if self.serialParameters.readTextIndex == "read_WU_device":
            #occurrences = 0
            #with open(self.recordFilePath, 'r') as file:
            #    occurrences = file.read().count("aaaa")
            #with open(self.recordFilePath, 'a') as file:
            #    file.write(float.hex(time()) + "\n")
            #    file.write("FatalError = " + str(occurrences) + "\n")

            with open(self.recordFilePath, 'a') as file:
                file.write(float.hex(time()) + "\n")
                file.write("FatalError = " + str(self.failCounter) + "\n")

    def pauseRecordData(self, port):
        if not port.upper() == "ALL" and not port.upper() == self.serialParameters.port.upper():
            return None
        self.record = False

    def resumeRecordData(self, port):
        if not port.upper() == "ALL" and not port.upper() == self.serialParameters.port.upper():
            return None
        self.record = True

    def writeDataToFile(self, text, port, filePath, fileName):
        if not port.upper() == "ALL" and not port.upper() == self.serialParameters.port.upper():
            return None

        lastRecord = self.record
        self.record = False
        if filePath != "":
            if not os.path.exists(filePath):
                self.record = lastRecord
                return None

            if filePath[-1] != "/":
                filePath += "/"
            if fileName.strip() == "":
                fileName += datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".txt"
            if port.upper() == "ALL":
                fileName = fileName.split(".")[0] + "_" + str(self.serialParameters.port) + ".txt"
            self.recordFilePath = filePath + fileName
            self.failCounter = 0

        if self.serialParameters.readTextIndex == "read_WU_device":
            with open(self.recordFilePath, 'a') as file:
                file.write(text)
        self.record = lastRecord

    def recordData(self, data):
        with open(self.recordFilePath, 'a') as file:
            file.write(' '.join(data) + "\n")

    def writeSerial(self, port, data):
        if port.upper() == "ALL" or port.upper() == self.serialParameters.port.upper():
            try:
                if self.serialArduino.isOpen():
                    self.serialArduino.write(data)
                    self.serialArduino.flush()
                    if self.serialParameters.local_echo:
                        self.signals.receivedData.emit(self.serialParameters, data)
                else:
                    self.signals.lostConnection.emit(self.serialParameters)
                    return None
            except:
                self.signals.failedSendData.emit(self.serialParameters, data)
                return None

    def kill(self, port):
        if port.upper() == "ALL" or port.upper() == self.serialParameters.port.upper():
            self.is_killed = True

    def pause(self, port):
        if port.upper() == "ALL" or port.upper() == self.serialParameters.port.upper():
            self.is_paused = True

    def resume(self, port):
        if port.upper() == "ALL" or port.upper() == self.serialParameters.port.upper():
            self.is_paused = False

    def read_line(self):
        startTime = time()
        byte_str = b''
        while True:
            if self.serialArduino.timeout is None:
                if self.is_killed:
                    break
                byte = self.serialArduino.read()
                byte_str += byte
                if byte == b'\n':
                    break
            else:
                if self.is_killed or time() - startTime >= self.serialArduino.timeout:
                    break
                byte = self.serialArduino.read()
                byte_str += byte
                if byte == b'\n':
                    break
        return byte_str

    def changeMaxSignalRate(self, port, maxSignalRate: int):
        if port.upper() == "ALL" or port.upper() == self.serialParameters.port.upper():
            self.serialParameters.maxSignalRate = maxSignalRate


class PortCombobox(QDMComboBox):
    def __init__(self):
        super().__init__()
        for port in serial.tools.list_ports.comports():
            self.addItem(port.name)
        self.lastText = self.currentText()
        self.activated.connect(self.handleActivated)
        self.adjustSize()

    def showPopup(self):
        self.clear()
        for port in serial.tools.list_ports.comports():
            self.addItem(port.name)
        self.setCurrentText(self.lastText)
        super().showPopup()

    def handleActivated(self, index):
        self.lastText = self.itemText(index)

class Content(QDMNodeContentWidget):
    sendSerialWriteSignal = pyqtSignal(str, object)
    killSerialConnectionSignal = pyqtSignal(str)
    pauseSerialConnectionSignal = pyqtSignal(str)
    resumeSerialConnectionSignal = pyqtSignal(str)
    startSerialRecordSignal = pyqtSignal(str, str, str)
    stopSerialRecordSignal = pyqtSignal(str)
    pauseSerialRecordSignal = pyqtSignal(str)
    resumeSerialRecordSignal = pyqtSignal(str)
    writeToFileSignal = pyqtSignal(str, str, str, str)
    changeMaxSignalRateSignal = pyqtSignal(str, int)

    def initUI(self):

        self.serialParam = SerialParameters()

        portLabel = QLabel("Port")
        baudrateLabel = QLabel("Baud rate")
        maxSignalRateLabel = QLabel("Max signal rate [Hz]")

        self.portCombobox = PortCombobox()
        self.portCombobox.setEditable(True)
        self.portCombobox.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.portCombobox.currentTextChanged.connect(self.updateSerialParam)

        self.baudrateCombobox = QDMComboBox()
        self.baudrateCombobox.setEditable(True)
        self.baudrateCombobox.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.baudrateCombobox.addItem("300")
        self.baudrateCombobox.addItem("1200")
        self.baudrateCombobox.addItem("2400")
        self.baudrateCombobox.addItem("4800")
        self.baudrateCombobox.addItem("9600")
        self.baudrateCombobox.addItem("19200")
        self.baudrateCombobox.addItem("38400")
        self.baudrateCombobox.addItem("57600")
        self.baudrateCombobox.addItem("74880")
        self.baudrateCombobox.addItem("115200")
        self.baudrateCombobox.addItem("230400")
        self.baudrateCombobox.addItem("250000")
        self.baudrateCombobox.addItem("500000")
        self.baudrateCombobox.addItem("1000000")
        self.baudrateCombobox.addItem("2000000")
        self.baudrateCombobox.setCurrentText(str(self.serialParam.baudrate))
        self.baudrateCombobox.currentTextChanged.connect(self.updateSerialParam)

        self.maxSignalRateSpinBox = QSpinBox()
        self.maxSignalRateSpinBox.setRange(1, 9999)
        self.maxSignalRateSpinBox.setValue(self.serialParam.maxSignalRate)
        self.maxSignalRateSpinBox.valueChanged.connect(self.sendChangeMaxSignalRate)
        self.maxSignalRateSpinBox.valueChanged.connect(self.updateSerialParam)

        self.connectButton = QPushButton("Disconnected")
        self.connectButton.setStyleSheet("background-color : red")
        self.connectButton.clicked.connect(self.connectToSerial)

        self.disconnectButton = QPushButton("Connected")
        self.disconnectButton.setStyleSheet("background-color : green")
        self.disconnectButton.clicked.connect(self.disconnectSerialConnection)
        self.disconnectButton.hide()

        self.optionButton = QPushButton()
        self.optionButton.setIcon(QIcon(getStartNodeEditorDirectory() + "/res/icons/option_icon.png"))
        self.optionButton.setFixedSize(20, 20)
        self.optionButton.clicked.connect(self.openSerialConnectWindow)

        connectLayout = QHBoxLayout()
        connectLayout.addWidget(self.connectButton)
        connectLayout.addWidget(self.disconnectButton)
        connectLayout.addWidget(self.optionButton)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(portLabel, 0, 0)
        layout.addWidget(baudrateLabel, 1, 0)
        layout.addWidget(maxSignalRateLabel, 2, 0)
        layout.addWidget(self.portCombobox, 0, 1)
        layout.addWidget(self.baudrateCombobox, 1, 1)
        layout.addWidget(self.maxSignalRateSpinBox, 2, 1)
        layout.addLayout(connectLayout, 3, 0, 1, 2)

        self.setLayout(layout)

    def sendData(self):
        self.node.sendDataFromSocket("DATA")

    def updateSerialParam(self):
        self.serialParam.port = self.portCombobox.currentText()
        if isInt(self.baudrateCombobox.currentText()): self.serialParam.baudrate = int(
            self.baudrateCombobox.currentText())
        self.serialParam.maxSignalRate = self.maxSignalRateSpinBox.value()

    def openSerialConnectWindow(self):
        self.serialConnectWindow = SerialConnectWindow(self.serialParam)
        self.serialConnectWindow.okButton.clicked.connect(self.okOptionWindow)
        self.serialConnectWindow.show()

    def disconnectSerialConnection(self):
        self.killSerialConnectionSignal.emit("ALL")

    def okOptionWindow(self):
        self.serialParam = self.serialConnectWindow.getSerialParameter()
        self.portCombobox.addItem(self.serialParam.port)
        self.portCombobox.setCurrentText(self.serialParam.port)
        self.baudrateCombobox.setCurrentText(str(self.serialParam.baudrate))
        self.maxSignalRateSpinBox.setValue(self.serialParam.maxSignalRate)
        self.serialConnectWindow.close()

    def connectToSerial(self):
        if self.portCombobox.currentText() != "":
            self.serialParam.port = self.portCombobox.currentText()
        else:
            self.serialParam.port = "COM1"
        if self.portCombobox.currentText() != "":
            self.serialParam.baudrate = int(self.baudrateCombobox.currentText())
        else:
            self.serialParam.baudrate = 9600
        self.serialParam.maxSignalRate = self.maxSignalRateSpinBox.value()

        serialThread = SerialThread(self.serialParam)
        serialThread.signals.madeConnection.connect(self.madeSerialConnection)
        serialThread.signals.lostConnection.connect(self.lostSerialConnection)
        serialThread.signals.receivedData.connect(self.receiveSerialData)
        serialThread.signals.failedSendData.connect(self.failedSendSerialData)

        self.sendSerialWriteSignal.connect(serialThread.writeSerial)
        self.killSerialConnectionSignal.connect(serialThread.kill)
        self.pauseSerialConnectionSignal.connect(serialThread.pause)
        self.resumeSerialConnectionSignal.connect(serialThread.resume)
        self.startSerialRecordSignal.connect(serialThread.startRecordData)
        self.stopSerialRecordSignal.connect(serialThread.stopRecordData)
        self.pauseSerialRecordSignal.connect(serialThread.pauseRecordData)
        self.resumeSerialRecordSignal.connect(serialThread.resumeRecordData)
        self.writeToFileSignal.connect(serialThread.writeDataToFile)
        self.changeMaxSignalRateSignal.connect(serialThread.changeMaxSignalRate)

        QThreadPool.globalInstance().start(serialThread)

    def sendChangeMaxSignalRate(self):
        self.changeMaxSignalRateSignal.emit("ALL", self.maxSignalRateSpinBox.value())

    def madeSerialConnection(self, obj: SerialParameters):
        self.portCombobox.setDisabled(True)
        self.baudrateCombobox.setDisabled(True)
        self.optionButton.setDisabled(True)
        self.connectButton.hide()
        self.disconnectButton.show()
        try:
            title = self.node.grNode.title
            self.node.grNode.title = title.split(":")[0] + ": " + obj.port
        except:
            pass

    def lostSerialConnection(self, obj: SerialParameters):
        self.portCombobox.setEnabled(True)
        self.baudrateCombobox.setEnabled(True)
        self.optionButton.setEnabled(True)
        self.disconnectButton.hide()
        self.connectButton.show()
        try:
            title = self.node.grNode.title
            self.node.grNode.title = title.split(":")[0]
        except:
            pass

    def receiveSerialData(self, obj: SerialParameters, data):
        self.node.sendDataFromSocket(data)

    def failedSendSerialData(self, obj: SerialParameters, data):
        print("FAILED TO SEND", obj.port, data)

    def removeContent(self):
        self.disconnectSerialConnection()

    def serialize(self) -> OrderedDict:
        orderedDict = super().serialize()
        orderedDict["serialParameters"] = self.serialParam.serialize()
        return orderedDict

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        super().deserialize(data, hashmap, restore_id)
        self.serialParam.deserialize(data["serialParameters"])
        if self.portCombobox.findText(self.serialParam.port) > -1:
            self.portCombobox.setCurrentText(self.serialParam.port)
        if self.baudrateCombobox.findText(str(self.serialParam.baudrate)) > -1:
            self.baudrateCombobox.setCurrentText(str(self.serialParam.baudrate))
        self.maxSignalRateSpinBox.setValue(self.serialParam.maxSignalRate)
        return True


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(220, 143)   # 1IN =65  2In =91  3IN =117  4IN =143  5IN =169  6IN =195  7IN =221  8IN =247
        self.setHiddenSize(220, 109)  # 1OUT=31  2OUT=57  3OUT=83   4OUT=109   5OUT=135  6OUT=161  7OUT=187  8OUT=213


class Node_SerialConnection(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Serial Connection", inputs: list = [VAR_TYPE_STR], outputs: list = [VAR_TYPE_STR]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def receiveData(self, data, inputSocketIndex):
        super().receiveData(data, inputSocketIndex)
