from PyQt5.QtWidgets import QHBoxLayout, QTextEdit
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.textEdit = QTextEdit("")
        self.textEdit.textChanged.connect(self.sendData)
        self.textEdit.setLineWrapMode(QTextEdit.NoWrap)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.textEdit)
        self.setLayout(layout)

    def sendData(self):
        self.node.sendDataFromSocket(self.textEdit.toPlainText())


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(180, 146)
        self.setHiddenSize(180, 112)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0


class Node_TextInputNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Text Input", inputs: list = [], outputs: list = [VAR_TYPE_STR]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_CENTER