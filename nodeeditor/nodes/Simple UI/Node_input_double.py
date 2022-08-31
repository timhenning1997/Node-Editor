from PyQt5.QtWidgets import QHBoxLayout, QDoubleSpinBox, QAbstractSpinBox
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.doubleSpinBox = QDoubleSpinBox()
        self.doubleSpinBox.valueChanged.connect(self.sendData)
        self.doubleSpinBox.setDecimals(3)
        self.doubleSpinBox.setRange(-1e200, 1e200)
        self.doubleSpinBox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.doubleSpinBox)
        self.setLayout(layout)

    def sendData(self):
        self.node.sendDataFromSocket(self.doubleSpinBox.value())


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(120, 64)
        self.setHiddenSize(120, 30)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0


class Node_DoubleNumberInputNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Double Input", inputs: list = [], outputs: list = [VAR_TYPE_FLOAT]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_CENTER
