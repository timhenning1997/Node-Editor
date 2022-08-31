from PyQt5.QtWidgets import QLineEdit, QHBoxLayout
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.lineEdit = QLineEdit("")
        self.lineEdit.textChanged.connect(self.sendData)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.lineEdit)
        self.setLayout(layout)

    def sendData(self):
        self.node.sendDataFromSocket(self.lineEdit.text())


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(180, 64)
        self.setHiddenSize(180, 30)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0


class Node_TextLineInputNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Text Line Input", inputs: list = [], outputs: list = [VAR_TYPE_STR]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_CENTER
