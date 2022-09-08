from PyQt5.QtWidgets import QLabel, QDoubleSpinBox, QGridLayout, QVBoxLayout, QLineEdit, QTextEdit, QWidget

from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.label = self.addInputCheckBox("INPUT", True, False)
        self.addOutputWidget(QLabel("OUT 1"))

        self.addMainWidget(QLineEdit("Hallo Welt!"))


    def sendData(self):
        self.node.sendDataFromSocket("DATA")


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(120, 83)   # 1IN =61  2In =83  3IN =105  4IN =127  5IN =149  6IN =171  7IN =193  8IN =215
        self.setHiddenSize(120, 49)  # 1OUT=27  2OUT=49  3OUT=71   4OUT=93   5OUT=115  6OUT=137  7OUT=159  8OUT=181


class Node_TestMultipleInAndOutputs(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Test In/Outputs", inputs: list = [VAR_TYPE_NOT_DEFINED], outputs: list = [VAR_TYPE_NOT_DEFINED, VAR_TYPE_NOT_DEFINED, VAR_TYPE_NOT_DEFINED, VAR_TYPE_NOT_DEFINED, VAR_TYPE_NOT_DEFINED, VAR_TYPE_NOT_DEFINED, VAR_TYPE_NOT_DEFINED, VAR_TYPE_NOT_DEFINED]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def receiveData(self, data, inputSocketIndex):
        super().receiveData(data, inputSocketIndex)

        if self.inputValues[inputSocketIndex] is not None:
            self.content.sendData()
