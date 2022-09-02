from PyQt5.QtWidgets import QHBoxLayout, QDial
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.dial = QDial()
        self.dial.valueChanged.connect(self.sendData)
        self.dial.setNotchesVisible(True)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.dial)
        self.setLayout(layout)

    def sendData(self):
        self.node.sendDataFromSocket(self.dial.value())


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(120, 144) # -34
        self.setHiddenSize(120, 110)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

    def hideNode(self):
        super().hideNode()
        self.drawBackground = False
        self.drawOutline = False


class Node_DialInputNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Dial Input", inputs: list = [VAR_TYPE_NOT_DEFINED], outputs: list = [VAR_TYPE_INT]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def receiveData(self, data, inputSocketIndex):
        super().receiveData(data, inputSocketIndex)

        self.content.sendData()
