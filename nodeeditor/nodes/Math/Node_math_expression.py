from io import StringIO
from contextlib import redirect_stdout

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QTextDocument, QSyntaxHighlighter, QFont, QTextCharFormat

from PyQt5.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QVBoxLayout
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *
from math import *



class Content(QDMNodeContentWidget):
    def initUI(self):
        self.evalLineEdit = QLineEdit("")
        self.evalLineEdit.returnPressed.connect(self.evaluateScript)
        self.evalLineEdit.setObjectName("evalLineEditObj")
        self.evalLineEdit.setStyleSheet("#evalLineEditObj {background-color: #111111; color: #eeeeee}")
        # self.evalLineEdit.setTabStopDistance(20)
        self.evalLineEdit.setText("x^2")

        label = QLabel("y(x)=")


        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addSpacing(3)
        layout.addWidget(label)
        layout.addWidget(self.evalLineEdit)

        self.setLayout(layout)

    def sendData(self, data):
        self.node.sendDataFromSocket(data)

    def evaluateScript(self, obj = None):
        if self.node.inputValues[0] is None:
            return
        
        x = self.node.inputValues[0]
        text = self.evalLineEdit.text()
        try:
            self.sendData(eval(text))
        except Exception as inst:
            print("ERROR_____________________________")
            print(inst)


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(150, 64)
        self.setHiddenSize(150, 30)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_MathExpressionNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Math Expression", inputs: list = [[VAR_TYPE_FLOAT, VAR_TYPE_INT]], outputs: list = [[VAR_TYPE_FLOAT, VAR_TYPE_INT]]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_CENTER
        self.input_socket_position = LEFT_CENTER

    def receiveData(self, data, inputSocketIndex):
        super().receiveData(data, inputSocketIndex)

        self.content.evaluateScript(data)
        #self.sendDataFromSocket(None)