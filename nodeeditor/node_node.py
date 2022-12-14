# -*- coding: utf-8 -*-
"""
A module containing NodeEditor's class for representing `Node`.
"""
from collections import OrderedDict
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_serializable import Serializable
from nodeeditor.node_socket import Socket, LEFT_BOTTOM, LEFT_CENTER, LEFT_TOP, RIGHT_BOTTOM, RIGHT_CENTER, RIGHT_TOP
from nodeeditor.utils_no_qt import dumpException, pp

DEBUG = False


class Node(Serializable):
    """
    Class representing `Node` in the `Scene`.
    """
    GraphicsNode_class = QDMGraphicsNode
    NodeContent_class = QDMNodeContentWidget
    Socket_class = Socket

    def __init__(self, scene: 'Scene', title: str="Undefined Node", inputs: list=[], outputs: list=[]):
        """

        :param scene: reference to the :class:`~nodeeditor.node_scene.Scene`
        :type scene: :class:`~nodeeditor.node_scene.Scene`
        :param title: Node Title shown in Scene
        :type title: str
        :param inputs: list of :class:`~nodeeditor.node_socket.Socket` types from which the `Sockets` will be auto created
        :param outputs: list of :class:`~nodeeditor.node_socket.Socket` types from which the `Sockets` will be auto created

        :Instance Attributes:

            - **scene** - reference to the :class:`~nodeeditor.node_scene.Scene`
            - **grNode** - Instance of :class:`~nodeeditor.node_graphics_node.QDMGraphicsNode` handling graphical representation in the ``QGraphicsScene``. Automatically created in the constructor
            - **content** - Instance of :class:`~nodeeditor.node_graphics_content.QDMGraphicsContent` which is child of ``QWidget`` representing container for all inner widgets inside of the Node. Automatically created in the constructor
            - **inputs** - list containin Input :class:`~nodeeditor.node_socket.Socket` instances
            - **outputs** - list containin Output :class:`~nodeeditor.node_socket.Socket` instances

        """

        super().__init__()
        self._title = title
        self.scene = scene

        self.value = None
        self.inputValues = []

        # just to be sure, init these variables
        self.content = None
        self.grNode = None

        self.initInnerClasses()
        self.initSettings()

        self.title = title
        self._path = ""
        self._filename = ""
        self.locked = False

        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

        # create socket for inputs and outputs
        self.inputs = []
        self.outputs = []
        self.initSockets(inputs, outputs)

        # dirty and evaluation
        self._is_dirty = False
        self._is_invalid = False

        # it's really important to mark all nodes Dirty by default
        self.markDirty()


    def __str__(self):
        return "<%s:%s %s..%s>" % (self.title, self.__class__.__name__,hex(id(self))[2:5], hex(id(self))[-3:])

    @property
    def title(self):
        """
        Title shown in the scene

        :getter: return current Node title
        :setter: sets Node title and passes it to Graphics Node class
        :type: ``str``
        """
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = self._title

    @property
    def pos(self):
        """
        Retrieve Node's position in the Scene

        :return: Node position
        :rtype: ``QPointF``
        """
        return self.grNode.pos()        # QPointF

    def setPos(self, x: float, y: float):
        """
        Sets position of the Graphics Node

        :param x: X `Scene` position
        :param y: Y `Scene` position
        """
        self.grNode.setPos(x, y)


    def initInnerClasses(self):
        """Sets up graphics Node (PyQt) and Content Widget"""
        node_content_class = self.getNodeContentClass()
        graphics_node_class = self.getGraphicsNodeClass()
        if node_content_class is not None: self.content = node_content_class(self)
        if graphics_node_class is not None: self.grNode = graphics_node_class(self)

    def getNodeContentClass(self):
        """Returns class representing nodeeditor content"""
        return self.__class__.NodeContent_class

    def getGraphicsNodeClass(self):
        return self.__class__.GraphicsNode_class

    def initSettings(self):
        """Initialize properties and socket information"""
        self._socket_spacing = 26
        self._socket_y_offset = 6
        self.socket_spacing = self._socket_spacing
        self.socket_y_offset = self._socket_y_offset

        self.input_socket_position = LEFT_TOP
        self.output_socket_position = RIGHT_BOTTOM
        self.input_multi_edged = False
        self.output_multi_edged = True
        self.socket_offsets = {
            LEFT_BOTTOM: -1,
            LEFT_CENTER: -1,
            LEFT_TOP: -1,
            RIGHT_BOTTOM: 1,
            RIGHT_CENTER: 1,
            RIGHT_TOP: 1,
        }

    def initSockets(self, inputs: list, outputs: list, reset: bool=True):
        """
        Create sockets for inputs and outputs

        :param inputs: list of Socket Types (int)
        :type inputs: ``list``
        :param outputs: list of Socket Types (int)
        :type outputs: ``list``
        :param reset: if ``True`` destroys and removes old `Sockets`
        :type reset: ``bool``
        """

        if reset:
            # clear old sockets
            if hasattr(self, 'inputs') and hasattr(self, 'outputs'):
                # remove grSockets from scene
                for socket in (self.inputs+self.outputs):
                    self.scene.grScene.removeItem(socket.grSocket)
                self.inputs = []
                self.outputs = []

        # create new sockets
        counter = 0
        for item in inputs:
            socket = self.__class__.Socket_class(
                node=self, index=counter, position=self.input_socket_position,
                socket_type=item[0] if type(item) == list else item, multi_edges=self.input_multi_edged,
                count_on_this_node_side=len(inputs), is_input=True,
                supportedTypes=item if type(item) == list else [item]
            )
            counter += 1
            self.inputs.append(socket)
            self.inputValues.append(None)

        counter = 0
        for item in outputs:
            socket = self.__class__.Socket_class(
                node=self, index=counter, position=self.output_socket_position,
                socket_type=item[0] if type(item) == list else item, multi_edges=self.output_multi_edged,
                count_on_this_node_side=len(outputs), is_input=False,
                supportedTypes=item if type(item) == list else [item]
            )
            counter += 1
            self.outputs.append(socket)


    def onEdgeConnectionChanged(self, new_edge: 'Edge'):
        """
        Event handling that any connection (`Edge`) has changed. Currently not used...

        :param new_edge: reference to the changed :class:`~nodeeditor.node_edge.Edge`
        :type new_edge: :class:`~nodeeditor.node_edge.Edge`
        """
        pass

    def onInputChanged(self, socket: 'Socket'):
        """Event handling when Node's input Edge has changed. We auto-mark this `Node` to be `Dirty` with all it's
        descendants

        :param socket: reference to the changed :class:`~nodeeditor.node_socket.Socket`
        :type socket: :class:`~nodeeditor.node_socket.Socket`
        """
        self.markDirty()
        #self.markDescendantsDirty()

    def onOutputChanged(self, socket: 'Socket'):
        """Event handling when Node's output Edge has changed. We auto-mark this `Node` to be `Dirty` with all it's
        descendants

        :param socket: reference to the changed :class:`~nodeeditor.node_socket.Socket`
        :type socket: :class:`~nodeeditor.node_socket.Socket`
        """
        pass

    def onDeserialized(self, data: dict):
        """Event manually called when this node was deserialized. Currently called when node is deserialized from scene
        Passing `data` containing the data which have been deserialized """
        pass

    def onDoubleClicked(self, event):
        """Event handling double click on Graphics Node in `Scene`"""
        pass

    def doSelect(self, new_state: bool=True):
        """Shortcut method for selecting/deselecting the `Node`

        :param new_state: ``True`` if you want to select the `Node`. ``False`` if you want to deselect the `Node`
        :type new_state: ``bool``
        """
        self.grNode.doSelect(new_state)

    def isSelected(self):
        """Returns ``True`` if current `Node` is selected"""
        return self.grNode.isSelected()

    def hasConnectedEdge(self, edge: 'Edge'):
        """Returns ``True`` if edge is connected to any :class:`~nodeeditor.node_socket.Socket` of this `Node`"""
        for socket in (self.inputs + self.outputs):
            if socket.isConnected(edge):
                return True
        return False

    def recalculateSocketPosition(self):
        for socket in (self.inputs + self.outputs):
            socket.setSocketPosition()

    def getSocketPosition(self, index: int, position: int, num_out_of: int=1) -> '(x, y)':
        """
        Get the relative `x, y` position of a :class:`~nodeeditor.node_socket.Socket`. This is used for placing
        the `Graphics Sockets` on `Graphics Node`.

        :param index: Order number of the Socket. (0, 1, 2, ...)
        :type index: ``int``
        :param position: `Socket Position Constant` describing where the Socket is located. See :ref:`socket-position-constants`
        :type position: ``int``
        :param num_out_of: Total number of Sockets on this `Socket Position`
        :type num_out_of: ``int``
        :return: Position of described Socket on the `Node`
        :rtype: ``x, y``
        """
        x = self.socket_offsets[position] if (position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM)) else self.grNode.width + self.socket_offsets[position]

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # start from bottom
            y = self.grNode.height - self.grNode.edge_roundness - self.grNode.title_vertical_padding - index * self.socket_spacing
        elif position in (LEFT_CENTER, RIGHT_CENTER):
            num_sockets = num_out_of
            node_height = self.grNode.height
            top_offset = self.grNode.title_height + 2 * self.grNode.title_vertical_padding + self.grNode.edge_padding + self.socket_y_offset
            available_height = node_height - top_offset

            total_height_of_all_sockets = num_sockets * self.socket_spacing
            new_top = available_height - total_height_of_all_sockets

            # y = top_offset + index * self.socket_spacing + new_top / 2
            y = top_offset + available_height/2.0 + (index-0.5)*self.socket_spacing
            if num_sockets > 1:
                y -= self.socket_spacing * (num_sockets-1)/2

        elif position in (LEFT_TOP, RIGHT_TOP):
            # start from top
            y = self.grNode.title_height + self.grNode.title_vertical_padding + self.grNode.edge_padding + self.socket_y_offset + index * self.socket_spacing
        else:
            # this should never happen
            y = 0

        return [x, y]

    def getSocketScenePosition(self, socket: 'Socket') -> '(x, y)':
        """
        Get absolute Socket position in the Scene

        :param socket: `Socket` which position we want to know
        :return: (x, y) Socket's scene position
        """
        nodepos = self.grNode.pos()
        socketpos = self.getSocketPosition(socket.index, socket.position, socket.count_on_this_node_side)
        scaleFactor = self.grNode.scale()
        scaledSocketpos = [socketpos[0] * scaleFactor, socketpos[1] * scaleFactor]
        return (nodepos.x() + scaledSocketpos[0], nodepos.y() + scaledSocketpos[1])

    def updateConnectedEdges(self):
        """Recalculate (Refresh) positions of all connected `Edges`. Used for updating Graphics Edges"""
        for socket in self.inputs + self.outputs:
            # if socket.hasEdge():
            for edge in socket.edges:
                edge.updatePositions()

    def remove(self):
        """
        Safely remove this Node
        """
        if DEBUG: print("> Removing Node", self)
        if DEBUG: print(" - remove all edges from sockets")
        for socket in (self.inputs+self.outputs):
            # if socket.hasEdge():
            for edge in socket.edges.copy():
                if DEBUG: print("    - removing from socket:", socket, "edge:", edge)
                edge.remove()
        if DEBUG: print(" - remove grNode")
        self.grNode.removeGrNode()
        if self.content: self.content.removeContent()
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        if DEBUG: print(" - remove node from the scene")
        self.scene.removeNode(self)
        if DEBUG: print(" - everything was done.")


    # node evaluation stuff

    def isDirty(self) -> bool:
        """Is this node marked as `Dirty`

        :return: ``True`` if `Node` is marked as `Dirty`
        :rtype: ``bool``
        """
        return self._is_dirty

    def markDirty(self, new_value: bool=True):
        """Mark this `Node` as `Dirty`. See :ref:`evaluation` for more

        :param new_value: ``True`` if this `Node` should be `Dirty`. ``False`` if you want to un-dirty this `Node`
        :type new_value: ``bool``
        """
        self._is_dirty = new_value
        if self._is_dirty: self.onMarkedDirty()

    def onMarkedDirty(self):
        """Called when this `Node` has been marked as `Dirty`. This method is supposed to be overridden"""
        pass

    def markChildrenDirty(self, new_value: bool=True):
        """Mark all first level children of this `Node` to be `Dirty`. Not this `Node` it self. Not other descendants

        :param new_value: ``True`` if children should be `Dirty`. ``False`` if you want to un-dirty children
        :type new_value: ``bool``
        """
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)

    def markDescendantsDirty(self, new_value: bool=True):
        """Mark all children and descendants of this `Node` to be `Dirty`. Not this `Node` it self

        :param new_value: ``True`` if children and descendants should be `Dirty`. ``False`` if you want to un-dirty children and descendants
        :type new_value: ``bool``
        """
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)
            other_node.markDescendantsDirty(new_value)

    def isInvalid(self) -> bool:
        """Is this node marked as `Invalid`?

        :return: ``True`` if `Node` is marked as `Invalid`
        :rtype: ``bool``
        """
        return self._is_invalid

    def markInvalid(self, new_value: bool=True):
        """Mark this `Node` as `Invalid`. See :ref:`evaluation` for more

        :param new_value: ``True`` if this `Node` should be `Invalid`. ``False`` if you want to make this `Node` valid
        :type new_value: ``bool``
        """
        self._is_invalid = new_value
        if self._is_invalid: self.onMarkedInvalid()

    def onMarkedInvalid(self):
        """Called when this `Node` has been marked as `Invalid`. This method is supposed to be overridden"""
        pass

    def markChildrenInvalid(self, new_value: bool=True):
        """Mark all first level children of this `Node` to be `Invalid`. Not this `Node` it self. Not other descendants

        :param new_value: ``True`` if children should be `Invalid`. ``False`` if you want to make children valid
        :type new_value: ``bool``
        """
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)

    def markDescendantsInvalid(self, new_value: bool=True):
        """Mark all children and descendants of this `Node` to be `Invalid`. Not this `Node` it self

        :param new_value: ``True`` if children and descendants should be `Invalid`. ``False`` if you want to make children and descendants valid
        :type new_value: ``bool``
        """
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)
            other_node.markDescendantsInvalid(new_value)

    def evalAfterDeserialize(self):
        """Evaluate this `Node` after the deserialize method was called. This is supposed to be overridden."""
        pass

    def eval(self, index=0):
        """Evaluate this `Node`. This is supposed to be overridden. See :ref:`evaluation` for more"""
        self.markDirty(False)
        self.markInvalid(False)
        return 0

    def evalChildren(self):
        """Evaluate all children of this `Node`"""
        for node in self.getChildrenNodes():
            node.eval()

    def showNode(self):
        self.socket_spacing = self._socket_spacing
        self.socket_y_offset = self._socket_y_offset
        for socket in (self.inputs+self.outputs):
            socket.changeSocketPositionToStartPosition()
        if self.content:
            self.content.showNode()

    def hideNode(self):
        self.socket_spacing = self._socket_spacing
        self.socket_y_offset = self._socket_y_offset
        for socket in (self.inputs+self.outputs):
            socket.changeSocketPositionToStartPosition()
        if self.content:
            self.content.hideNode()

    def closeNode(self):
        self.socket_spacing = 0
        self.socket_y_offset = 0
        for socket in self.inputs:
            socket.changeSocketPosition(2)
        for socket in self.outputs:
            socket.changeSocketPosition(5)
        if self.content:
            self.content.closeNode()

    def lockNode(self):
        self.content.lockNode()

    def editNode(self):
        self.content.editNode()

    def changeSocketPositions(self, inputPos: int = 1, outputPos: int = 4):
        for socket in self.inputs:
            socket.changeSocketPosition(inputPos)
        for socket in self.outputs:
            socket.changeSocketPosition(outputPos)


    # traversing nodes functions

    def getChildrenNodes(self) -> 'List[Node]':
        """
        Retreive all first-level children connected to this `Node` `Outputs`

        :return: list of `Nodes` connected to this `Node` from all `Outputs`
        :rtype: List[:class:`~nodeeditor.node_node.Node`]
        """
        if self.outputs == []: return []
        other_nodes = []
        for ix in range(len(self.outputs)):
            for edge in self.outputs[ix].edges:
                other_node = edge.getOtherSocket(self.outputs[ix]).node
                other_nodes.append(other_node)
        return other_nodes


    def getInput(self, index: int=0) -> ['Node', None]:
        """
        Get the **first**  `Node` connected to the  Input specified by `index`

        :param index: Order number of the `Input Socket`
        :type index: ``int``
        :return: :class:`~nodeeditor.node_node.Node` which is connected to the specified `Input` or ``None`` if
            there is no connection or the index is out of range
        :rtype: :class:`~nodeeditor.node_node.Node` or ``None``
        """
        try:
            input_socket = self.inputs[index]
            if len(input_socket.edges) == 0: return None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node
        except Exception as e:
            dumpException(e)
            return None

    def getInputWithSocket(self, index: int=0) -> [('Node', 'Socket'), (None, None)]:
        """
        Get the **first**  `Node` connected to the Input specified by `index` and the connection `Socket`

        :param index: Order number of the `Input Socket`
        :type index: ``int``
        :return: Tuple containing :class:`~nodeeditor.node_node.Node` and :class:`~nodeeditor.node_socket.Socket` which
            is connected to the specified `Input` or ``None`` if there is no connection or the index is out of range
        :rtype: (:class:`~nodeeditor.node_node.Node`, :class:`~nodeeditor.node_socket.Socket`)
        """
        try:
            input_socket = self.inputs[index]
            if len(input_socket.edges) == 0: return None, None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node, other_socket
        except Exception as e:
            dumpException(e)
            return None, None

    def getInputWithSocketIndex(self, index: int=0) -> ('Node', int):
        """
        Get the **first**  `Node` connected to the Input specified by `index` and the connection `Socket`

        :param index: Order number of the `Input Socket`
        :type index: ``int``
        :return: Tuple containing :class:`~nodeeditor.node_node.Node` and :class:`~nodeeditor.node_socket.Socket` which
            is connected to the specified `Input` or ``None`` if there is no connection or the index is out of range
        :rtype: (:class:`~nodeeditor.node_node.Node`, int)
        """
        try:
            edge = self.inputs[index].edges[0]
            socket = edge.getOtherSocket(self.inputs[index])
            return socket.node, socket.index
        except IndexError:
            # print("EXC: Trying to get input with socket index %d, but none is attached to" % index, self)
            return None, None
        except Exception as e:
            dumpException(e)
            return None, None

    def getInputs(self, index: int=0) -> 'List[Node]':
        """
        Get **all** `Nodes` connected to the Input specified by `index`

        :param index: Order number of the `Input Socket`
        :type index: ``int``
        :return: all :class:`~nodeeditor.node_node.Node` instances which are connected to the
            specified `Input` or ``[]`` if there is no connection or the index is out of range
        :rtype: List[:class:`~nodeeditor.node_node.Node`]
        """
        ins = []
        for edge in self.inputs[index].edges:
            other_socket = edge.getOtherSocket(self.inputs[index])
            ins.append(other_socket.node)
        return ins

    def getOutputs(self, index: int=0) -> 'List[Node]':
        """
        Get **all** `Nodes` connected to the Output specified by `index`

        :param index: Order number of the `Output Socket`
        :type index: ``int``
        :return: all :class:`~nodeeditor.node_node.Node` instances which are connected to the
            specified `Output` or ``[]`` if there is no connection or the index is out of range
        :rtype: List[:class:`~nodeeditor.node_node.Node`]
        """
        outs = []
        for edge in self.outputs[index].edges:
            other_socket = edge.getOtherSocket(self.outputs[index])
            outs.append(other_socket.node)
        return outs

    def isChildrenAtSocket(self, index: int = -1) -> bool:
        if self.outputs == []: return False
        if index < 0:
            for ix in range(len(self.outputs)):
                for edge in self.outputs[ix].edges:
                    other_socket = edge.getOtherSocket(self.outputs[ix])
                    if other_socket:
                        return True
        else:
            if index < len(self.outputs):
                for edge in self.outputs[index].edges:
                    other_socket = edge.getOtherSocket(self.outputs[index])
                    if other_socket:
                        return True
        return False

    # functions for the newer version... with sendData and receiveData

    def getChildrenNodesAndSockets(self, index: int = -1) -> 'List[Node]':
        if self.outputs == []: return []
        other_nodes_and_sockets = []
        if index < 0:
            for ix in range(len(self.outputs)):
                for edge in self.outputs[ix].edges:
                    other_socket = edge.getOtherSocket(self.outputs[ix])
                    if other_socket:
                        other_node = other_socket.node
                        other_nodes_and_sockets.append([other_node, other_socket.index])
        else:
            if index < len(self.outputs):
                for edge in self.outputs[index].edges:
                    other_socket = edge.getOtherSocket(self.outputs[index])
                    if other_socket:
                        other_node = other_socket.node
                        other_nodes_and_sockets.append([other_node, other_socket.index])
        return other_nodes_and_sockets

    def sendDataFromSocket(self, data, outputSocketIndex: int = -1):
        for nodes_and_sockets in self.getChildrenNodesAndSockets(outputSocketIndex):
            nodes_and_sockets[0].receiveData(data, nodes_and_sockets[1])

    def receiveData(self, data, inputSocketIndex):
        self.inputValues[inputSocketIndex] = data
        if self.grNode.showEvaluatedAnimation:
            self.grNode.animation.startAnimation()


    # serialization functions

    def serialize(self) -> OrderedDict:
        inputs, outputs = [], []
        for socket in self.inputs: inputs.append(socket.serialize())
        for socket in self.outputs: outputs.append(socket.serialize())
        ser_content = self.content.serialize() if isinstance(self.content, Serializable) else {}

        return OrderedDict([
            ('id', self.id),
            ('_path', self._path),
            ('_filename', self._filename),
            ('title', self.title),
            ('locked_status', self.locked),
            ('pos_x', self.grNode.scenePos().x()),
            ('pos_y', self.grNode.scenePos().y()),
            ('scale', self.grNode.scale()),
            ('hidden_status', self.grNode.hidden_status),
            ('evaluation_icon_visibility', self.grNode.evaluationIconVisibility),
            ('grnode_rotation', self.grNode.rotation()),
            ('grnode_width', self.grNode.width),
            ('grnode_height', self.grNode.height),
            ('grnode_shown_width', self.grNode.shown_width),
            ('grnode_shown_height', self.grNode.shown_height),
            ('grnode_hidden_width', self.grNode.hidden_width),
            ('grnode_hidden_height', self.grNode.hidden_height),
            ('grnode_closed_width', self.grNode.closed_width),
            ('grnode_closed_height', self.grNode.closed_height),
            ('grnode_show_scale_icon', self.grNode.scale_item.isVisible()),
            ('grnode_show_rotation_icon', self.grNode.rotate_item.isVisible()),
            ('grnode_show_resize_icon', self.grNode.resize_item.isVisible()),
            ('hide_item_visibility', self.grNode.hide_item.isVisible()),
            ('inputs', inputs),
            ('outputs', outputs),
            ('content', ser_content),
            ('showaEvalAnimation', self.grNode.animation.isEnable())
        ])

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, *args, **kwargs) -> bool:
        try:
            if restore_id: self.id = data['id']
            hashmap[data['id']] = self

            self.setPos(data['pos_x'], data['pos_y'])
            self.grNode.setScale(data['scale'])
            self.grNode.changeHiddenStatus(data['hidden_status'])
            self.grNode.evaluationIconVisibility = data['evaluation_icon_visibility']
            self.title = data['title']
            self._path = data['_path']
            self._filename = data['_filename']
            self.grNode.setLockedStatus(data['locked_status'])
            self.grNode.setRotation(data['grnode_rotation'])
            self.grNode.changeContendSize(data['grnode_width'], data['grnode_height'])
            self.grNode.shown_width = data['grnode_shown_width']
            self.grNode.shown_height = data['grnode_shown_height']
            self.grNode.hidden_width = data['grnode_hidden_width']
            self.grNode.hidden_height = data['grnode_hidden_height']
            self.grNode.closed_width = data['grnode_closed_width']
            self.grNode.closed_height = data['grnode_closed_height']
            self.grNode.showScaleRotResize(data['grnode_show_scale_icon'], "SCALE")
            self.grNode.showScaleRotResize(data['grnode_show_rotation_icon'], "ROTATION")
            self.grNode.showScaleRotResize(data['grnode_show_resize_icon'], "RESIZE")
            self.grNode.showHideIcon(data['hide_item_visibility'])
            self.grNode.animation.setEnable(data['showaEvalAnimation'])

            data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000 )
            data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000 )
            num_inputs = len( data['inputs'] )
            num_outputs = len( data['outputs'] )

            # print("> deserialize node,   num inputs:", num_inputs, "num outputs:", num_outputs)
            # pp(data)

            # possible way to do it is reuse existing sockets...
            # dont create new ones if not necessary

            for socket_data in data['inputs']:
                found = None
                for socket in self.inputs:
                    # print("\t", socket, socket.index, "=?", socket_data['index'])
                    if socket.index == socket_data['index']:
                        found = socket
                        break
                if found is None:
                    # print("deserialization of socket data has not found input socket with index:", socket_data['index'])
                    # print("actual socket data:", socket_data)
                    # we can create new socket for this
                    found = self.__class__.Socket_class(
                        node=self, index=socket_data['index'], position=socket_data['position'],
                        socket_type=socket_data['socket_type'], count_on_this_node_side=num_inputs,
                        is_input=True, supportedTypes=socket_data['supported_types']
                    )
                    self.inputs.append(found)  # append newly created input to the list
                    self.inputValues.append(None)
                found.deserialize(socket_data, hashmap, restore_id)


            for socket_data in data['outputs']:
                found = None
                for socket in self.outputs:
                    # print("\t", socket, socket.index, "=?", socket_data['index'])
                    if socket.index == socket_data['index']:
                        found = socket
                        break
                if found is None:
                    # print("deserialization of socket data has not found output socket with index:", socket_data['index'])
                    # print("actual socket data:", socket_data)
                    # we can create new socket for this
                    found = self.__class__.Socket_class(
                        node=self, index=socket_data['index'], position=socket_data['position'],
                        socket_type=socket_data['socket_type'], count_on_this_node_side=num_outputs,
                        is_input=False, supportedTypes=socket_data['supported_types']
                    )
                    self.outputs.append(found)  # append newly created output to the list
                found.deserialize(socket_data, hashmap, restore_id)
            self.grNode.updateSocketsAndEdgesPositions()

        except Exception as e: dumpException(e)

        # also deserialize the content of the node
        # so far the rest was ok, now as last step the content...
        if isinstance(self.content, Serializable):
            res = self.content.deserialize(data['content'], hashmap)
            return res


        return True
