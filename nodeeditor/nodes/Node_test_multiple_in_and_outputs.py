from random import randint, random

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QDoubleSpinBox, QGridLayout, QVBoxLayout

from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):
        inputLabel1 = QLabel("Input 1")
        inputLabel2 = QLabel("Input 2")
        inputLabel3 = QLabel("Input 3")
        inputLabel4 = QLabel("Input 4")

        outputLabel1 = QLabel("Output 1")
        outputLabel1.setAlignment(Qt.AlignRight)
        outputLabel2 = QLabel("Output 2")
        outputLabel2.setAlignment(Qt.AlignRight)
        outputLabel3 = QLabel("Output 3")
        outputLabel3.setAlignment(Qt.AlignRight)
        outputLabel4 = QLabel("Output 4")
        outputLabel4.setAlignment(Qt.AlignRight)

        inputLayout = QVBoxLayout()
        # inputLayout.setSizeConstraint()
        inputLayout.setContentsMargins(0, 0, 0, 0)
        inputLayout.addWidget(inputLabel1)
        inputLayout.addWidget(inputLabel2)
        inputLayout.addWidget(inputLabel3)
        inputLayout.addWidget(inputLabel4)

        self.setLayout(inputLayout)

    def sendData(self):
        self.node.sendDataFromSocket("DATA")


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(190, 194)
        self.setHiddenSize(190, 160)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_TestMultipleInAndOutputs(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Test In/Outputs", inputs: list = [VAR_TYPE_NOT_DEFINED, VAR_TYPE_NOT_DEFINED, VAR_TYPE_NOT_DEFINED], outputs: list = [VAR_TYPE_NOT_DEFINED, VAR_TYPE_NOT_DEFINED, VAR_TYPE_NOT_DEFINED, VAR_TYPE_NOT_DEFINED]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_TOP
        self.input_socket_position = LEFT_TOP

    def receiveData(self, data, inputSocketIndex):
        super().receiveData(data, inputSocketIndex)

        if self.inputValues[inputSocketIndex] is not None:
            self.content.sendData()
