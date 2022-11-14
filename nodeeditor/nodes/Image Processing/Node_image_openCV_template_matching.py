from nodeeditor.utils import checkForRequiredModules
if not checkForRequiredModules("pathlib", "opencv-python", "uuid", "numpy"):
    raise ImportError

import os
import uuid
from collections import OrderedDict
from pathlib import Path
import cv2
import numpy as np

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QResizeEvent, QMouseEvent, QImage
from PyQt5.QtWidgets import QHBoxLayout, QDial, QPushButton, QLabel, QSizePolicy, QFileDialog, QVBoxLayout
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.utils_no_qt import dumpException, getNodeEditorDirectory
from nodeeditor.var_type_conf import *


class ClickableLable(QLabel):
    rightMouseButtonclicked = pyqtSignal()

    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if event.button() == Qt.RightButton:
            self.rightMouseButtonclicked.emit()

class Content(QDMNodeContentWidget):
    def initUI(self):
        self.pixmap = None

        self.label = ClickableLable()
        self.label.rightMouseButtonclicked.connect(self.checkForTemplate)
        self.label.setFrameStyle(1)
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.label.setAlignment(Qt.AlignCenter)

        self.labelInput1 = QLabel("Image")
        self.labelInput1.setFixedHeight(16)
        self.labelInput2 = QLabel("Template")
        self.labelInput2.setFixedHeight(16)

        self.labelOutput1 = QLabel("max val.")
        self.labelOutput1.setFixedHeight(16)
        self.labelOutput2 = QLabel("max[x,y]")
        self.labelOutput2.setFixedHeight(16)

        layoutInputs = QVBoxLayout()
        layoutInputs.setContentsMargins(0, 0, 0, 0)
        layoutInputs.addWidget(self.labelInput1)
        layoutInputs.addWidget(self.labelInput2)
        layoutInputs.addStretch()

        layoutOutputs = QVBoxLayout()
        layoutOutputs.setContentsMargins(0, 0, 0, 0)
        layoutOutputs.addWidget(self.labelOutput1)
        layoutOutputs.addWidget(self.labelOutput2)
        layoutOutputs.addStretch()


        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(layoutInputs)
        layout.addWidget(self.label)
        layout.addLayout(layoutOutputs)
        self.setLayout(layout)

    def resizeEvent(self, event: QResizeEvent):
        self.setLabelPixmap()

    def checkForTemplate(self):
        if self.node.inputValues[0] is not None and self.node.inputValues[1] is not None:
            result = cv2.matchTemplate(self.node.inputValues[0], self.node.inputValues[1], cv2.TM_CCOEFF_NORMED)

            y, x = np.unravel_index(np.argmax(result), result.shape)
            maxValue = np.max(result)

            self.node.sendDataFromSocket(maxValue, 0)
            self.node.sendDataFromSocket([x,y], 1)

            # threshold = .9
            # loc = np.where(result >= threshold)
            # for pt in zip(*loc[::-1]):  # Switch collumns and rows
            #     pass

    def sendData(self, data):
        self.node.sendDataFromSocket(data)

    def setLabelPixmap(self):
        if self.pixmap:
            self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(190, 148) # -34
        self.setHiddenSize(190, 110)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_ImageOpenCVTemplateMatching(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Template Matching", inputs: list = [VAR_TYPE_LIST, VAR_TYPE_LIST], outputs: list = [VAR_TYPE_FLOAT, VAR_TYPE_LIST]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_TOP
        self.input_socket_position = LEFT_TOP

    def receiveData(self, data, inputSocketIndex):
        super().receiveData(data, inputSocketIndex)
        if inputSocketIndex == 1:
            self.content.small_image = data
            self.content.pixmap = self.openCVToQPixmap(data)
            self.content.setLabelPixmap()
        self.content.checkForTemplate()

    def openCVToQPixmap(self, data):
        data = np.require(data, np.uint8, 'C')
        return QPixmap(QImage(data, data.shape[1], data.shape[0], len(data[0]) * 3, QImage.Format_RGB888))
