import os
import pathlib
from collections import OrderedDict
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QResizeEvent, QImage
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSizePolicy
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.utils_no_qt import dumpException, getNodeEditorDirectory
from nodeeditor.var_type_conf import *
from nodeeditor.node_socket import Socket, LEFT_BOTTOM, LEFT_CENTER, LEFT_TOP, RIGHT_BOTTOM, RIGHT_CENTER, RIGHT_TOP


class Content(QDMNodeContentWidget):
    def initUI(self):

        self.label = QLabel(self)
        self.label.setFrameStyle(0)
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

        self.pixmap = QPixmap(getNodeEditorDirectory() + "/res/icons/arduino/Arduino_Uno.png")
        self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        #self.label.setPixmap(self.pixmap)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def showNode(self):
        super().showNode()

    def hideNode(self):
        super().hideNode()

    def resizeEvent(self, event: QResizeEvent):
        self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def serialize(self) -> OrderedDict:
        orderedDict = super().serialize()
        return orderedDict

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        super().deserialize(data, hashmap, restore_id)
        return True


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(340, 514)
        self.setHiddenSize(340, 480)
        self.setClosedSize(30, 30)

        self.scaleEvenlyByScaleIcon = True
        #self.drawHovered = True

    def initUI(self):
        super().initUI()
        self.showScaleRotResize(False)
        self.drawEvaluationIcon = False

        self.setZValue(-8)

    def showNode(self):
        super().showNode()
        self.drawBackground = True
        self.drawHovered = True
        self.drawOutline = True
        self.contextMenuInteractable = False
        self.showScaleRotResize(True)

    def hideNode(self):
        super().hideNode()
        self.drawBackground = False
        self.drawHovered = False
        self.drawOutline = False
        self.contextMenuInteractable = True
        self.showScaleRotResize(False)

    def closeNode(self):
        super().closeNode()
        self.drawBackground = True
        self.drawHovered = True
        self.drawOutline = True
        self.contextMenuInteractable = False
        self.showScaleRotResize(False)


class Node_ArduinoUnoNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Arduino Uno", inputs: list = [VAR_TYPE_FLOAT, VAR_TYPE_FLOAT], outputs: list = [VAR_TYPE_FLOAT, VAR_TYPE_FLOAT]):
        super().__init__(scene, title, inputs, outputs)
        self.grNode.hideNode()

        print(self.outputs[0].is_input, self.outputs[0].is_output)
        self.outputs[0].is_input = True
        print(self.outputs[0].is_input, self.outputs[0].is_output)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def getSocketPosition(self, index: int, position: int, num_out_of: int = 1) -> '(x, y)':
        x = self.socket_offsets[position] if (position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM)) else \
            self.grNode.width + self.socket_offsets[position]
        y = self.grNode.height - self.grNode.edge_roundness - self.grNode.title_vertical_padding - index * self.socket_spacing
        return [x, y]
