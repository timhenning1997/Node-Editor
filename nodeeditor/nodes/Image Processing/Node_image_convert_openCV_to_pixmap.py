from nodeeditor.utils import checkForRequiredModules
if not checkForRequiredModules("pathlib", "opencv-python", "matplotlib", "numpy"):
    raise ImportError

import os
from collections import OrderedDict
from pathlib import Path
import cv2
from matplotlib import pyplot as plt
import numpy as np

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QResizeEvent, QMouseEvent, QImage
from PyQt5.QtWidgets import QHBoxLayout, QDial, QPushButton, QLabel, QSizePolicy, QFileDialog, QVBoxLayout
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.utils_no_qt import dumpException
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
        self.label.rightMouseButtonclicked.connect(self.sendData)
        self.label.setFrameStyle(1)
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.setLabelPixmap()
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def sendData(self):
        if self.pixmap is not None:
            self.node.sendDataFromSocket(self.pixmap)

    def resizeEvent(self, event: QResizeEvent):
        self.setLabelPixmap()

    def setLabelPixmap(self):
        if self.pixmap:
            self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def showNode(self):
        super().showNode()
        self.label.setFrameStyle(1)

    def hideNode(self):
        super().hideNode()
        self.label.setFrameStyle(0)


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(150, 148) # -34
        self.setHiddenSize(150, 110)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_ImageConvertOpenCVToPixmapNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "OpenCV To Pixmap", inputs: list = [VAR_TYPE_LIST], outputs: list = [VAR_TYPE_PIXMAP]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_CENTER
        self.input_socket_position = LEFT_CENTER

    def receiveData(self, data, inputSocketIndex):
        super().receiveData(data, inputSocketIndex)

        self.content.pixmap = self.openCVToQPixmap(data)
        self.content.setLabelPixmap()

        self.sendDataFromSocket(self.content.pixmap)

    def openCVToQPixmap(self, data):
        data = np.require(data, np.uint8, 'C')
        return QPixmap(QImage(data, data.shape[1], data.shape[0], len(data[0]) * 3, QImage.Format_RGB888))

