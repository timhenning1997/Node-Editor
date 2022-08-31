from collections import OrderedDict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QTextEdit, QSpinBox, QLabel, QGraphicsItem
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.color_button import ColorButton
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.colorButton = ColorButton(QColor(255, 140, 0, 150))
        self.colorBackgroundButton = ColorButton(QColor(255, 255, 255, 20))
        self.borderWidthSpinBox = QSpinBox()
        self.borderWidthSpinBox.setValue(5)
        self.borderWidthSpinBox.setRange(0, 1000)

        self.label = QLabel(self)
        self.label.setFrameStyle(1)
        self.label.setObjectName("BackgroundLabelObj")
        self.label.setLineWidth(5)

        self.colorButton.newColor.connect(self.changeFrame)
        self.colorBackgroundButton.newColor.connect(self.changeFrame)
        self.borderWidthSpinBox.valueChanged.connect(self.changeFrame)

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.colorButton)
        hLayout.addWidget(self.colorBackgroundButton)
        hLayout.addWidget(self.borderWidthSpinBox)

        layout = QVBoxLayout()
        layout.addLayout(hLayout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)

        self.setLayout(layout)
        self.changeFrame()

    def changeFrame(self):
        self.label.setStyleSheet("#BackgroundLabelObj {background: " +
                                 self.colorBackgroundButton.color.name(QColor.HexArgb) +
                                 "; border: " +
                                 str(self.borderWidthSpinBox.value()) +
                                 "px solid " +
                                 self.colorButton.color.name(QColor.HexArgb) +
                                 "}")

    def showNode(self):
        super().showNode()
        self.colorButton.show()
        self.colorBackgroundButton.show()
        self.borderWidthSpinBox.show()

    def hideNode(self):
        super().hideNode()
        self.colorButton.hide()
        self.colorBackgroundButton.hide()
        self.borderWidthSpinBox.hide()

    def serialize(self) -> OrderedDict:
        orderedDict = super().serialize()
        orderedDict["frame_border_color"] = self.colorButton.color.name(QColor.HexArgb)
        orderedDict["frame_background_color"] = self.colorBackgroundButton.color.name(QColor.HexArgb)
        orderedDict["frame_border_width"] = self.borderWidthSpinBox.value()
        return orderedDict

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        super().deserialize(data, hashmap, restore_id)
        self.colorButton.setColor(QColor(data["frame_border_color"]))
        self.colorBackgroundButton.setColor(QColor(data["frame_background_color"]))
        self.borderWidthSpinBox.setValue(data["frame_border_width"])
        self.changeFrame()
        return True


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(240, 240)
        self.setHiddenSize(240, 240)
        self.setClosedSize(30, 30)

        self.hidden_edge_roundness = 10.0
        self.hidden_edge_padding = 10
        self.hidden_title_height = 0
        self.hidden_title_horizontal_padding = 0
        self.hidden_title_vertical_padding = 0

        self.setShowAndHiddenSameSize = True

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


class Node_BackgroundFrameNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Background Frame", inputs: list = [], outputs: list = []):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)
