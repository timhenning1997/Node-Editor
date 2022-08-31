import inspect
import os

from PyQt5.QtCore import QFile, Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QApplication, QMainWindow, QScrollArea, QGroupBox, \
    QFormLayout, QHBoxLayout, QPushButton, QVBoxLayout, QCheckBox

from nodeeditor.color_button import ColorButton
from nodeeditor.var_type_conf import *


class AppearanceColorWindow(QMainWindow):
    def __init__(self, socket_colors, edge_color, eval_highlight_color):
        super().__init__()

        self.socketColorButtons = []

        # __________ Socket colors __________
        socketColorLayout = QFormLayout()

        defaultSocketColorsButton = QPushButton("default")
        defaultSocketColorsButton.clicked.connect(self.setSocketColorsToDefault)

        socketColorLayout.addRow(QLabel(""), defaultSocketColorsButton)

        for i in range(len(socket_colors)):
            self.socketColorButtons.append(ColorButton(socket_colors[i]))
            socketColorLayout.addRow(QLabel(TYPE_NAMES[i]), self.socketColorButtons[i])

        socketColorGroupbox = QGroupBox("Socket colors")
        socketColorGroupbox.setObjectName("socketColorGroupbox")
        socketColorGroupbox.setStyleSheet("#socketColorGroupbox {color: white}")
        socketColorGroupbox.setLayout(socketColorLayout)

        # __________ Edge color __________
        edgeColorLayout = QFormLayout()

        self.defaultEdgeColorButton = QPushButton("default")
        self.defaultEdgeColorButton.clicked.connect(self.setEdgeColorToDefault)
        self.edgeColorButton = ColorButton(edge_color)
        self.edgeColorFromSocketCB = QCheckBox()
        self.edgeColorFromSocketCB.clicked.connect(self.edgeColorCBChanged)

        edgeColorLayout.addRow(QLabel(""), self.defaultEdgeColorButton)
        edgeColorLayout.addRow(QLabel("EDGE"), self.edgeColorButton)
        edgeColorLayout.addRow(QLabel("Edge color from Socket Color"), self.edgeColorFromSocketCB)


        edgeColorGroupbox = QGroupBox("Edge color")
        edgeColorGroupbox.setObjectName("edgeColorGroupbox")
        edgeColorGroupbox.setStyleSheet("#edgeColorGroupbox {color: white}")
        edgeColorGroupbox.setLayout(edgeColorLayout)

        # __________ Eval highlight color __________
        evalHighlightColorLayout = QFormLayout()

        self.defaultEvalHighlightColorButton = QPushButton("default")
        self.defaultEvalHighlightColorButton.clicked.connect(self.setEvalHighlightColorToDefault)
        self.evalHighlightColorButton = ColorButton(eval_highlight_color)

        evalHighlightColorLayout.addRow(QLabel(""), self.defaultEvalHighlightColorButton)
        evalHighlightColorLayout.addRow(QLabel("EVAL HIGHLIGHT"), self.evalHighlightColorButton)

        evalHighlightGroupbox = QGroupBox("Eval highlight color")
        evalHighlightGroupbox.setObjectName("evalHighlightGroupbox")
        evalHighlightGroupbox.setStyleSheet("#evalHighlightGroupbox {color: white}")
        evalHighlightGroupbox.setLayout(evalHighlightColorLayout)

        # __________ Widget Grid Layout __________
        widgetLayout = QVBoxLayout()
        widgetLayout.addWidget(socketColorGroupbox)
        widgetLayout.addSpacing(10)
        widgetLayout.addWidget(edgeColorGroupbox)
        widgetLayout.addSpacing(10)
        widgetLayout.addWidget(evalHighlightGroupbox)

        widget = QWidget()
        widget.setObjectName("scrollWidget")
        widget.setStyleSheet("#scrollWidget {background-color:transparent;}")
        widget.setLayout(widgetLayout)

        scroll = QScrollArea()
        scroll.setWidget(widget)

        # Scroll Area Properties
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        # __________ Submit Button Layout __________
        self.cancelButton = QPushButton("Cancel")
        self.applyButton = QPushButton("Apply")
        self.okButton = QPushButton("OK")
        self.okButton.setAutoDefault(True)
        QTimer.singleShot(0, self.okButton.setFocus)

        submitButtonLayout = QHBoxLayout()
        submitButtonLayout.addWidget(self.okButton)
        submitButtonLayout.addWidget(self.applyButton)
        submitButtonLayout.addWidget(self.cancelButton)
        self.cancelButton.clicked.connect(self.close)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(scroll)
        mainLayout.addLayout(submitButtonLayout)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)

        self.setCentralWidget(mainWidget)

        self.setGeometry(600, 300, 300, 500)
        self.setWindowTitle("Appearance")

        self.show()

    def setSocketColorsToDefault(self):
        for i in range(len(TYPE_COLORS)):
            self.socketColorButtons[i].setColor(TYPE_COLORS[i])

    def setEdgeColorToDefault(self):
        self.edgeColorButton.setColor(EDGE_COLOR)

    def edgeColorCBChanged(self, value):
        self.edgeColorButton.setDisabled(value)
        self.defaultEdgeColorButton.setDisabled(value)

    def setEvalHighlightColorToDefault(self):
        self.evalHighlightColorButton.setColor(EVAL_HIGHLIGHT_COLOR)
