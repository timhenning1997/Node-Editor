from nodeeditor.node_node import Node


class Abstract_Node(Node):
    def __init__(self, scene: 'Scene', title: str="Abstract_Node", inputs: list = [], outputs: list = []):
        super().__init__(scene, title, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.grNode.drawEvaluationIcon = False
        if self.content:
            self.input_socket_position = self.content.socketInputPosition
            self.output_socket_position = self.content.socketOutputPosition