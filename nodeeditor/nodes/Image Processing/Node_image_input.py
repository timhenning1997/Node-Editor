from nodeeditor.utils import checkForRequiredModules
if not checkForRequiredModules("pathlib"):
    raise ImportError

import os
from collections import OrderedDict
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QResizeEvent, QMouseEvent
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
        self.lastOpenedImage = ""
        self.lastOpenedFolder = ""

        self.loadImageButton = QPushButton("Load Image")
        self.loadImageButton.clicked.connect(self.loadImage)

        self.pixmap = None

        self.label = ClickableLable()
        self.label.rightMouseButtonclicked.connect(self.sendData)
        self.label.setFrameStyle(1)
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.setLabelPixmap()
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.loadImageButton)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def resizeEvent(self, event: QResizeEvent):
        self.setLabelPixmap()

    def loadImage(self):
        home = str(Path.home()) if self.lastOpenedFolder == "" else self.lastOpenedFolder
        fname, filter = QFileDialog.getOpenFileName(None, 'Open background image', home, "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.pbm *.pgm *.ppm *.xpm *.xbm *.svg)", "", QFileDialog.DontUseNativeDialog)
        self.openImage(fname)

    def openImage(self, fname):
        if fname != '' and os.path.isfile(fname):
            try:
                self.lastOpenedImage = fname
                self.lastOpenedFolder = os.path.dirname(fname)
                self.pixmap = QPixmap(fname)
                self.setLabelPixmap()
                self.sendData()
            except Exception as e: dumpException(e)

    def sendData(self):
        self.node.sendDataFromSocket(self.pixmap)

    def setLabelPixmap(self):
        if self.pixmap:
            self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def serialize(self) -> OrderedDict:
        orderedDict = super().serialize()
        orderedDict["lastOpenedImageName"] = self.lastOpenedImage
        return orderedDict

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        super().deserialize(data, hashmap, restore_id)
        self.openImage(data["lastOpenedImageName"])
        return True

    def showNode(self):
        super().showNode()
        self.loadImageButton.show()
        self.label.setFrameStyle(1)

    def hideNode(self):
        super().hideNode()
        self.loadImageButton.hide()
        self.label.setFrameStyle(0)


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(120, 162) # -34
        self.setHiddenSize(120, 110)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_ImageInputNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Image Input", inputs: list = [], outputs: list = [VAR_TYPE_PIXMAP]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_CENTER
