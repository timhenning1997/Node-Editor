import os
from collections import OrderedDict
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QResizeEvent
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSizePolicy
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.utils_no_qt import dumpException
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.lastOpenedImage = ""
        self.lastOpenedFolder = ""

        self.loadImageButton = QPushButton("Load Image")
        self.loadImageButton.clicked.connect(self.loadImage)
        self.loadImageLabel = QLabel("")

        self.label = QLabel(self)
        self.label.setFrameStyle(1)
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

        self.pixmap = QPixmap()
        self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.label.setAlignment(Qt.AlignCenter)

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.loadImageButton)
        hLayout.addWidget(self.loadImageLabel)

        layout = QVBoxLayout()
        layout.addLayout(hLayout)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def loadImage(self):
        home = str(Path.home()) if self.lastOpenedFolder == "" else self.lastOpenedFolder
        fname, filter = QFileDialog.getOpenFileName(None, 'Open background image', home, "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.pbm *.pgm *.ppm *.xpm *.xbm *.svg)", "", QFileDialog.DontUseNativeDialog)
        suffix = Path(fname).suffix
        self.openImage(fname)

    def openImage(self, fname):
        if fname != '' and os.path.isfile(fname):
            try:
                self.lastOpenedImage = fname
                self.lastOpenedFolder = os.path.dirname(fname)
                self.loadImageLabel.setText("Image: " + fname)
                self.pixmap = QPixmap(fname)
                self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception as e: dumpException(e)

    def showNode(self):
        super().showNode()
        self.loadImageButton.show()
        self.loadImageLabel.show()
        self.label.setFrameStyle(1)

    def hideNode(self):
        super().hideNode()
        self.loadImageButton.hide()
        self.loadImageLabel.hide()
        self.label.setFrameStyle(0)

    def resizeEvent(self, event: QResizeEvent):
        self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def serialize(self) -> OrderedDict:
        orderedDict = super().serialize()
        orderedDict["lastOpenedImageName"] = self.lastOpenedImage
        return orderedDict

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        super().deserialize(data, hashmap, restore_id)
        self.openImage(data["lastOpenedImageName"])
        return True


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(240, 240)
        self.setHiddenSize(240, 240)
        self.setClosedSize(30, 30)

        self.hidden_edge_roundness = 10.0
        self.hidden_edge_padding = 5
        self.hidden_title_height = 0
        self.hidden_title_horizontal_padding = 0
        self.hidden_title_vertical_padding = 0

        self.setShowAndHiddenSameSize = True
        self.drawHovered = False

    def initUI(self):
        super().initUI()
        self.showScaleRotResize(True)
        self.drawEvaluationIcon = False

        self.setZValue(-10)

    def showNode(self):
        super().showNode()
        self.drawBackground = True
        self.drawHovered = True
        self.drawOutline = True
        self.contextMenuInteractable = False

    def hideNode(self):
        super().hideNode()
        self.drawBackground = False
        self.drawHovered = False
        self.drawOutline = False
        self.contextMenuInteractable = True

    def closeNode(self):
        super().closeNode()
        self.drawBackground = True
        self.drawHovered = True
        self.drawOutline = True
        self.contextMenuInteractable = False


class Node_BackgroundImageNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Background Image", inputs: list = [], outputs: list = []):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)
