from collections import OrderedDict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QTextEdit, QSpinBox
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.color_button import ColorButton
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.textEdit = QTextEdit("")
        self.textEdit.setLineWrapMode(QTextEdit.NoWrap)
        self.textEdit.setObjectName("BackgroundTextObj")
        self.textEdit.setStyleSheet("#BackgroundTextObj {background: rgba(0,0,0,25%)}")
        self.textEdit.setTextColor(QColor(Qt.white))

        self.color = QColor(Qt.white)
        self.colorButton = ColorButton(self.color)

        self.fontSizeSpinBox = QSpinBox()
        self.fontSizeSpinBox.setValue(8)
        self.fontSizeSpinBox.setRange(1, 100)

        self.fontSizeSpinBox.valueChanged.connect(self.changeFont)
        self.colorButton.newColor.connect(self.changeFont)

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.fontSizeSpinBox)
        hLayout.addWidget(self.colorButton)

        layout = QVBoxLayout()
        layout.addLayout(hLayout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.textEdit)

        self.setLayout(layout)

    def changeFont(self):
        self.color = self.colorButton.color
        self.textEdit.selectAll()
        self.textEdit.setTextColor(self.color)
        self.textEdit.moveCursor(QTextCursor.End)
        font = QFont()
        font.setPointSize(self.fontSizeSpinBox.value())
        self.textEdit.setFont(font)

    def showNode(self):
        super().showNode()
        self.fontSizeSpinBox.show()
        self.colorButton.show()
        self.textEdit.setStyleSheet("#BackgroundTextObj {background: rgba(0,0,0,25%)}")
        self.textEdit.setEnabled(True)

    def hideNode(self):
        super().hideNode()
        self.fontSizeSpinBox.hide()
        self.colorButton.hide()
        self.textEdit.setStyleSheet("#BackgroundTextObj {background: transparent}")
        self.textEdit.setEnabled(False)

    def lockNode(self):
        self.textEdit.setEnabled(False)
        self.textEdit.moveCursor(QTextCursor.End)

    def editNode(self):
        if self.colorButton.isVisible():
            self.textEdit.setEnabled(True)

    def serialize(self) -> OrderedDict:
        orderedDict = super().serialize()
        orderedDict["text_color"] = self.color.name(QColor.HexArgb)
        orderedDict["text_size"] = self.fontSizeSpinBox.value()
        return orderedDict

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        super().deserialize(data, hashmap, restore_id)
        self.colorButton.setColor(QColor(data["text_color"]))
        self.fontSizeSpinBox.setValue(data["text_size"])
        self.changeFont()
        return True


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(240, 240)
        self.setHiddenSize(240, 240)
        self.setClosedSize(30, 30)

        self.setShowAndHiddenSameSize = True

        self.hidden_edge_roundness = 10.0
        self.hidden_edge_padding = 10
        self.hidden_title_height = 0
        self.hidden_title_horizontal_padding = 0
        self.hidden_title_vertical_padding = 0

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


class Node_BackgroundTextNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Background Text", inputs: list = [], outputs: list = []):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)
