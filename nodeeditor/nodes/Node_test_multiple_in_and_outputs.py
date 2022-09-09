from PyQt5.QtWidgets import QLabel, QDoubleSpinBox, QGridLayout, QVBoxLayout, QLineEdit, QTextEdit, QWidget

from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):

        self.spinBox1 = self.addInputDoubleSpinBox()
        self.spinBox2 = self.addInputDoubleSpinBox()

        self.addMainWidget(QLabel("+"))

        # self.addOutputLabel()


    def sendData(self):
        self.node.sendDataFromSocket("DATA")


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(220, 91)   # 1IN =65  2In =91  3IN =117  4IN =143  5IN =169  6IN =195  7IN =221  8IN =247
        self.setHiddenSize(220, 57)  # 1OUT=31  2OUT=57  3OUT=83   4OUT=109   5OUT=135  6OUT=161  7OUT=187  8OUT=213


class Node_TestMultipleInAndOutputs(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Test In/Outputs", inputs: list = [VAR_TYPE_FLOAT, VAR_TYPE_FLOAT], outputs: list = [VAR_TYPE_FLOAT]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def receiveData(self, data, inputSocketIndex):
        super().receiveData(data, inputSocketIndex)

        if inputSocketIndex == 0 and self.inputValues[0] is not None:
            self.content.spinBox1.setValue(data)
            self.sendDataFromSocket(self.content.spinBox1.value() + self.content.spinBox2.value())
        if inputSocketIndex == 1 and self.inputValues[0] is not None:
            self.content.spinBox2.setValue(data)
            self.sendDataFromSocket(self.content.spinBox1.value() + self.content.spinBox2.value())
