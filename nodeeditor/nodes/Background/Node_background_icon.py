import os
import pathlib
from collections import OrderedDict
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QResizeEvent
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSizePolicy
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.utils_no_qt import dumpException, getNodeEditorDirectory
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.lastOpenedImage = ""
        self.lastOpenedFolder = ""

        self.loadImageButton = QPushButton("Load Image")
        self.loadImageButton.clicked.connect(self.loadImage)

        self.label = QLabel(self)
        self.label.setFrameStyle(0)
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.label.hide()

        self.pixmap = QPixmap()
        self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.label.setAlignment(Qt.AlignCenter)

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.loadImageButton)

        layout = QHBoxLayout()
        layout.addLayout(hLayout)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def loadImage(self):
        home = getNodeEditorDirectory() + "/user_res/icons"  if self.lastOpenedFolder == "" else self.lastOpenedFolder
        fname, filter = QFileDialog.getOpenFileName(None, 'Open background image', home, "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.pbm *.pgm *.ppm *.xpm *.xbm *.svg)", "", QFileDialog.DontUseNativeDialog)
        suffix = Path(fname).suffix
        self.openImage(fname)

    def openImage(self, fname):
        if fname != '' and os.path.isfile(fname):
            try:
                self.lastOpenedImage = fname
                self.lastOpenedFolder = os.path.dirname(fname)
                self.pixmap = QPixmap(fname)

                size = self.pixmap.size()
                self.node.grNode.setHiddenSize(size.width() + 45, size.height() + 45)
                self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.node.grNode.changeHiddenStatus("hidden")
                self.label.show()
            except Exception as e: dumpException(e)

    def showNode(self):
        super().showNode()
        self.loadImageButton.show()

    def hideNode(self):
        super().hideNode()
        self.loadImageButton.hide()

    def resizeEvent(self, event: QResizeEvent):
        self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def serialize(self) -> OrderedDict:
        orderedDict = super().serialize()
        orderedDict["lastOpenedImageName"] = self.lastOpenedImage
        orderedDict["grnode_show_scale_icon"] = self.node.grNode.scale_item.isVisible()
        orderedDict["grnode_show_rotation_icon"] = self.node.grNode.rotate_item.isVisible()
        orderedDict["grnode_show_resize_icon"] = self.node.grNode.resize_item.isVisible()
        return orderedDict

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        super().deserialize(data, hashmap, restore_id)
        width = self.node.grNode.hidden_width
        height = self.node.grNode.hidden_height
        self.openImage(data["lastOpenedImageName"])
        self.node.grNode.setHiddenSize(width, height)
        self.node.grNode.changeContendSize()
        self.node.grNode.showScaleRotResize(data['grnode_show_scale_icon'], "SCALE")
        self.node.grNode.showScaleRotResize(data['grnode_show_rotation_icon'], "ROTATION")
        self.node.grNode.showScaleRotResize(data['grnode_show_resize_icon'], "RESIZE")
        return True


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(180, 64)
        self.setHiddenSize(180, 64)
        self.setClosedSize(30, 30)

        self.hidden_edge_roundness = 10.0
        self.hidden_edge_padding = 5
        self.hidden_title_height = 0
        self.hidden_title_horizontal_padding = 0
        self.hidden_title_vertical_padding = 0

        self.scaleEvenlyByScaleIcon = True
        self.drawHovered = False

    def initUI(self):
        super().initUI()
        self.showScaleRotResize(False)
        self.drawEvaluationIcon = False

        self.setZValue(-10)

    def showNode(self):
        super().showNode()
        self.drawBackground = True
        self.drawHovered = True
        self.drawOutline = True
        self.contextMenuInteractable = False
        self.showScaleRotResize(False)

    def hideNode(self):
        super().hideNode()
        self.drawBackground = False
        self.drawHovered = False
        self.drawOutline = False
        self.contextMenuInteractable = True
        self.showScaleRotResize(True)

    def closeNode(self):
        super().closeNode()
        self.drawBackground = True
        self.drawHovered = True
        self.drawOutline = True
        self.contextMenuInteractable = False


class Node_BackgroundIconNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Background Icon", inputs: list = [], outputs: list = []):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)
