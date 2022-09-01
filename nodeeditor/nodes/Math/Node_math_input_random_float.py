from random import randint, random

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QDoubleSpinBox, QGridLayout

from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.minSpinBox = QDoubleSpinBox()
        self.minSpinBox.setRange(-1000000000, 1000000000)
        self.minSpinBox.valueChanged.connect(self.sendData)
        self.maxSpinBox = QDoubleSpinBox()
        self.maxSpinBox.setRange(-1000000000, 1000000000)
        self.maxSpinBox.valueChanged.connect(self.sendData)

        minLabel = QLabel("min")
        maxLabel = QLabel("max")
        self.outputLabel = QLabel("")
        self.outputLabel.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(minLabel, 0, 0)
        layout.addWidget(self.minSpinBox, 0, 1)
        layout.addWidget(maxLabel, 1, 0)
        layout.addWidget(self.maxSpinBox, 1, 1)
        layout.addWidget(self.outputLabel, 0, 2, 2, 1)

        self.setLayout(layout)

    def sendData(self):
        if self.minSpinBox.value() <= self.maxSpinBox.value():
            data = random() * (self.maxSpinBox.value() - self.minSpinBox.value()) + self.minSpinBox.value()
            self.outputLabel.setText("%.2f" % (data))
            self.node.sendDataFromSocket(data)
        else:
            self.node.grNode.setToolTip("Minimum value is bigger then maximum value!")
            self.node.grNode.errorAnimation.startAnimation()


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(190, 94)
        self.setHiddenSize(190, 60)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_MathInputRandomFloat(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Random Float", inputs: list = [VAR_TYPE_NOT_DEFINED], outputs: list = [VAR_TYPE_FLOAT]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_CENTER
        self.input_socket_position = LEFT_TOP

    def receiveData(self, data, inputSocketIndex):
        super().receiveData(data, inputSocketIndex)

        if self.inputValues[0] is not None:
            self.content.sendData()
