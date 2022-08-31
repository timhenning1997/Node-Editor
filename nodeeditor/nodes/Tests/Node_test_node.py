from PyQt5.QtWidgets import QLabel, QVBoxLayout

from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode


class InputContent(QDMNodeContentWidget):
    def initUI(self):
        self.lbl = QLabel("Test Label")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.lbl)
        self.setLayout(layout)


class InputGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(180, 140)
        self.setHiddenSize(180, 140)
        self.setClosedSize(30, 30)


class Node_TestNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str="TestNode", inputs: list = [1, 1, 1, 1], outputs: list = [1, 1, 1, 1]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = InputContent(self)
        self.grNode = InputGraphicsNode(self)

    def receiveData(self, data, inputSocketIndex):
        super().receiveData(data, inputSocketIndex)
        self.content.lbl.setText(str(data))
        self.sendDataFromSocket(data, inputSocketIndex)
