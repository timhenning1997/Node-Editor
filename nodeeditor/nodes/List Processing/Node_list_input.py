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


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.lastOpenedFile = ""
        self.lastOpenedFolder = ""

        self.loadListButton = QPushButton("Load List")
        self.loadListButton.clicked.connect(self.loadList)

        self.loadedList = None

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.loadListButton)
        layout.addStretch()
        self.setLayout(layout)

    def resizeEvent(self, event: QResizeEvent):
        pass

    def loadList(self):
        home = str(Path.home()) if self.lastOpenedFolder == "" else self.lastOpenedFolder
        fname, filter = QFileDialog.getOpenFileName(None, 'Open text file', home, "Text Files (*.txt *.csv)\nAll Files (*.*)", "", QFileDialog.DontUseNativeDialog)
        self.openList(fname)

    def openList(self, fname):
        if fname != '' and os.path.isfile(fname):
            try:
                self.lastOpenedFile = fname
                self.lastOpenedFolder = os.path.dirname(fname)
                # TODO do something with the list
                self.sendData()
            except Exception as e: dumpException(e)

    def sendData(self):
        self.node.sendDataFromSocket(self.loadedList)

    def serialize(self) -> OrderedDict:
        orderedDict = super().serialize()
        orderedDict["lastOpenedFileName"] = self.lastOpenedFile
        return orderedDict

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        super().deserialize(data, hashmap, restore_id)
        self.openList(data["lastOpenedFileName"])
        return True

    def showNode(self):
        super().showNode()
        self.loadListButton.show()

    def hideNode(self):
        super().hideNode()
        self.loadListButton.hide()


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(120, 162) # -34
        self.setHiddenSize(120, 110)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_ListInputNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "List Input", inputs: list = [], outputs: list = [VAR_TYPE_LIST]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_CENTER
