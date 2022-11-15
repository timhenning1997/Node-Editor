from PyQt5.QtWidgets import QHBoxLayout, QDial, QSpinBox, QVBoxLayout
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.minSpinBox = QSpinBox()
        self.minSpinBox.setRange(-100000, 100000)
        self.minSpinBox.valueChanged.connect(self.setDialRange)
        self.maxSpinBox = QSpinBox()
        self.maxSpinBox.setRange(-100000, 100000)
        self.maxSpinBox.setValue(99)
        self.maxSpinBox.valueChanged.connect(self.setDialRange)

        minMaxLayout = QHBoxLayout()
        minMaxLayout.addWidget(self.minSpinBox)
        minMaxLayout.addWidget(self.maxSpinBox)

        self.dial = QDial()
        self.dial.valueChanged.connect(self.sendData)
        self.dial.setNotchesVisible(True)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(minMaxLayout)
        layout.addWidget(self.dial)
        self.setLayout(layout)

    def sendData(self):
        self.node.sendDataFromSocket(self.dial.value())

    def setDialRange(self):
        self.dial.setRange(self.minSpinBox.value(), self.maxSpinBox.value())

    def showNode(self):
        super().showNode()
        self.minSpinBox.show()
        self.maxSpinBox.show()

    def hideNode(self):
        super().hideNode()
        self.minSpinBox.hide()
        self.maxSpinBox.hide()


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
