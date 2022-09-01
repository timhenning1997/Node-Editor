# -*- coding: utf-8 -*-
"""
A module containing Graphics representation of :class:`~nodeeditor.node_node.Node`
"""
import math
from turtle import isvisible

from PyQt5.QtWidgets import QGraphicsItem, QWidget, QGraphicsTextItem, QMenu
from PyQt5.QtGui import QFont, QColor, QPen, QBrush, QPainterPath, QImage, QFocusEvent, QPixmap, QIcon, \
    QContextMenuEvent
from PyQt5.QtCore import Qt, QRectF, QPoint, QRect, QPointF, QEvent

from nodeeditor.node_graphics_edge import QDMGraphicsEdge
from nodeeditor.propertyAnimator import PropertyAnimator
from nodeeditor.utils_no_qt import getNodeEditorDirectory
from nodeeditor.var_type_conf import EVAL_HIGHLIGHT_COLOR


class QDMGraphicsNode(QGraphicsItem):
    """Class describing Graphics representation of :class:`~nodeeditor.node_node.Node`"""

    def __init__(self, node: 'Node', parent: QWidget = None):
        """
        :param node: reference to :class:`~nodeeditor.node_node.Node`
        :type node: :class:`~nodeeditor.node_node.Node`
        :param parent: parent widget
        :type parent: QWidget

        :Instance Attributes:

            - **node** - reference to :class:`~nodeeditor.node_node.Node`
        """
        super().__init__(parent)
        self.node = node

        # init our flags
        self.hovered = False
        self._was_moved = False
        self._last_selected_state = False

        self.setScale(1)
        self.hidden_status = "show"  # or hidden or closed
        self.evaluationIconVisibility = True

        self.showEvaluatedAnimation = True
        self._draw_evaluated_outline = False
        self._draw_error_evaluated_outline = False
        self.drawHovered = True

        self.drawBackground = True
        self.drawOutline = True
        self.drawEvaluationIcon = True
        self.setShowAndHiddenSameSize = False

        self.contextMenuInteractable = False
        self.scaleEvenlyByScaleIcon = False

        self.animation = PropertyAnimator(startValue=0, endValue=1, duration=200, interval=50)
        self.animation.update.connect(self.updateEvaluatedAnimation)
        self.animation.stop.connect(self.stopEvaluatedAnimation)

        self.errorAnimation = PropertyAnimator(startValue=0, endValue=1, duration=500, interval=50)
        self.errorAnimation.update.connect(self.updateErrorEvaluatedAnimation)
        self.errorAnimation.stop.connect(self.stopErrorEvaluatedAnimation)

        self.initSizes()
        self.initAssets()
        self.initUI()

    def setEvaluatedAnimationColor(self, color: QColor = None):
        if color:
            self._color_evaluated = color
            self._pen_evaluated.setColor(color)

    def updateEvaluatedAnimation(self, value):
        self._pen_evaluated.setWidthF((1-value) * 2)
        self._color_evaluated.setAlphaF((1-value) / 3)
        self._pen_evaluated.setColor(self._color_evaluated)
        self._draw_evaluated_outline = True
        self.update()

    def stopEvaluatedAnimation(self):
        self._draw_evaluated_outline = False
        self._color_evaluated.setAlphaF(1)

    def updateErrorEvaluatedAnimation(self, value):
        self._pen_error_evaluated.setWidthF((1-value) * 2)
        self._color_error_evaluated.setAlphaF((1-value))
        self._pen_error_evaluated.setColor(self._color_error_evaluated)
        self._draw_error_evaluated_outline = True
        self.update()

    def stopErrorEvaluatedAnimation(self):
        self._draw_error_evaluated_outline = False
        self._color_error_evaluated.setAlphaF(1)

    @property
    def content(self):
        """Reference to `Node Content`"""
        return self.node.content if self.node else None

    @property
    def title(self):
        """title of this `Node`

        :getter: current Graphics Node title
        :setter: stores and make visible the new title
        :type: str
        """
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    def initUI(self):
        """Set up this ``QGraphicsItem``"""
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)

        # init title
        self.initTitle()
        self.title = self.node.title

        self.initContent()

        self.initIcons()

    def initSizes(self):
        """Set up internal attributes like `width`, `height`, etc."""
        self.width = 180
        self.height = 240
        self.edge_roundness = 10.0
        self.edge_padding = 10.0
        self.title_height = 24.0
        self.title_horizontal_padding = 4.0
        self.title_vertical_padding = 4.0

        self.shown_width = 180
        self.shown_height = 240
        self.shown_edge_roundness = 10.0
        self.shown_edge_padding = 10.0
        self.shown_title_height = 24.0
        self.shown_title_horizontal_padding = 4.0
        self.shown_title_vertical_padding = 4.0

        self.hidden_width = 180
        self.hidden_height = 240
        self.hidden_edge_roundness = 10.0
        self.hidden_edge_padding = 10.0
        self.hidden_title_height = 24.0
        self.hidden_title_horizontal_padding = 4.0
        self.hidden_title_vertical_padding = 4.0

        self.closed_width = 30
        self.closed_height = 30
        self.closed_edge_roundness = 10.0
        self.closed_edge_padding = 5
        self.closed_title_height = 0
        self.closed_title_horizontal_padding = 0
        self.closed_title_vertical_padding = 0


    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._title_color = Qt.white
        self._title_font = QFont("Ubuntu", 10)

        self._color = QColor("#7F000000")
        self._color_selected = QColor("#FFFFA637")
        self._color_hovered = QColor("#FF37A6FF")
        self._color_evaluated = EVAL_HIGHLIGHT_COLOR
        self._color_error_evaluated = QColor("#FFFF0000")

        self._pen_default = QPen(self._color)
        self._pen_default.setWidthF(2.0)
        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(2.0)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_hovered.setWidthF(3.0)
        self._pen_evaluated = QPen(self._color_evaluated)
        self._pen_evaluated.setWidthF(5.0)
        self._pen_error_evaluated = QPen(self._color_error_evaluated)
        self._pen_error_evaluated.setWidthF(5.0)

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        # Initialize icons
        self.statusIcons = QImage(getNodeEditorDirectory() + "/res/icons/status_icons/status_icons_Alpha80.png")
        self.hiddenIcons = QImage(getNodeEditorDirectory() + "/res/icons/hidden_icons.png")
        self.scaleIcon = QImage(getNodeEditorDirectory() + "/res/icons/scale_icon.png")
        self.resizeIcon = QImage(getNodeEditorDirectory() + "/res/icons/resize_icon.png")
        self.rotateIcon = QImage(getNodeEditorDirectory() + "/res/icons/rotate_icon.png")

    def setShownSize(self, width, height):
        self.shown_width = width
        self.shown_height = height
        self.width = self.shown_width
        self.height = self.shown_height

    def setHiddenSize(self, width, height):
        self.hidden_width = width
        self.hidden_height = height

    def setClosedSize(self, width, height):
        self.closed_width = width
        self.closed_height = height

    def onSelected(self):
        """Our event handling when the node was selected"""
        self.node.scene.grScene.itemSelected.emit()

    def doSelect(self, new_state=True):
        """Safe version of selecting the `Graphics Node`. Takes care about the selection state flag used internally

        :param new_state: ``True`` to select, ``False`` to deselect
        :type new_state: ``bool``
        """
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state: self.onSelected()

    def sceneEvent(self, event):
        if event.type() == QEvent.GraphicsSceneContextMenu and self.checkEventModifiersToSetIconVisibility(event):
            return False
                
        if event.type() == QEvent.GraphicsSceneContextMenu and self.contextMenuInteractable:
            super().sceneEvent(event)
            return False
        return super().sceneEvent(event)

    def checkEventModifiersToSetIconVisibility(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if self.hide_item.isVisible():
                self.showHideIcon(False, True)
            else:
                self.showHideIcon(True, True)
            return True
        elif event.modifiers() == Qt.ShiftModifier:
            if self.rotate_item.isVisible() or self.scale_item.isVisible() or self.resize_item.isVisible():
                self.showScaleRotResize(False, toAllSelected=True)
            else:
                self.showScaleRotResize(True, toAllSelected=True)
            return True
        elif event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            if self.rotate_item.isVisible() or self.scale_item.isVisible() or \
                    self.resize_item.isVisible() or self.hide_item.isVisible():
                self.showScaleRotResize(False, toAllSelected=True)
                self.showHideIcon(False, True)
            else:
                self.showScaleRotResize(True, toAllSelected=True)
                self.showHideIcon(True, True)
            return True
        return False

    def mouseMoveEvent(self, event):
        """Overridden event to detect that we moved with this `Node`"""

        super().mouseMoveEvent(event)

        if event.modifiers() == Qt.ControlModifier | Qt.ShiftModifier or self.node.scene.grScene.isSnappingToGridSquares:
            gridSize = self.node.scene.grScene.gridSize * self.node.scene.grScene.gridSquares
            self.setPos(round(self.pos().x() / gridSize) * gridSize, round(self.pos().y() / gridSize) * gridSize)
        elif event.modifiers() == Qt.ControlModifier or self.node.scene.grScene.isSnappingToGrid:
            gridSize = self.node.scene.grScene.gridSize
            self.setPos(round(self.pos().x() / gridSize) * gridSize, round(self.pos().y() / gridSize) * gridSize)

        # optimize me! just update the selected nodes
        for node in self.scene().scene.nodes:
            if node.grNode.isSelected():
                node.updateConnectedEdges()
        self._was_moved = True

    def mouseReleaseEvent(self, event):
        """Overriden event to handle when we moved, selected or deselected this `Node`"""
        super().mouseReleaseEvent(event)

        # handle when grNode moved
        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.storeHistory("Node moved", setModified=True)

            self.node.scene.resetLastSelectedStates()
            self.doSelect()  # also trigger itemSelected when node was moved

            # we need to store the last selected state, because moving does also select the nodes
            self.node.scene._last_selected_items = self.node.scene.getSelectedItems()

            # now we want to skip storing selection
            return

        # handle when grNode was clicked on
        if self._last_selected_state != self.isSelected() or self.node.scene._last_selected_items != self.node.scene.getSelectedItems():
            self.node.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def mouseDoubleClickEvent(self, event):
        """Overriden event for doubleclick. Resend to `Node::onDoubleClicked`"""
        self.node.onDoubleClicked(event)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = False
        self.update()

    def boundingRect(self) -> QRectF:
        """Defining Qt' bounding rectangle"""
        return QRectF(
            0,
            0,
            self.width,
            self.height
        ).normalized()

    def initTitle(self):
        """Set up the title Graphics representation: font, color, position, etc."""
        self.title_item = TextItem(self)
        self.title_item.node = self.node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.title_horizontal_padding, 0)
        self.title_item.setTextWidth(
            self.width
            - 2 * self.title_horizontal_padding
        )

    def initIcons(self):
        self.hide_item = HideIconItem(self, self.hiddenIcons)
        self.hide_item.setPos(self.width - 26, 0)

        self.scale_item = ScaleIconItem(self, self.scaleIcon)
        self.scale_item.setPos(self.width - 18, self.height + 2)
        self.scale_item.setEnabled(False)
        self.scale_item.hide()

        self.resize_item = ResizeIconItem(self, self.resizeIcon)
        self.resize_item.setPos(self.width - 38, self.height + 2)
        self.resize_item.setEnabled(False)
        self.resize_item.hide()

        self.rotate_item = RotateIconItem(self, self.rotateIcon)
        self.rotate_item.setPos(self.width + 2, self.height + 2)
        self.rotate_item.setEnabled(False)
        self.rotate_item.hide()

    def initContent(self):
        """Set up the `grContent` - ``QGraphicsProxyWidget`` to have a container for `Graphics Content`"""
        if self.content is not None:
            self.content.setGeometry(int(self.edge_padding),
                                     int(self.title_height + self.edge_padding),
                                     int(self.width - 2 * self.edge_padding),
                                     int(self.height - 2 * self.edge_padding - self.title_height))

        # get the QGraphicsProxyWidget when inserted into the grScene
        self.grContent = self.node.scene.grScene.addWidget(self.content)
        self.grContent.node = self.node
        self.grContent.setParentItem(self)

    def changeContendSize(self, width=-1, height=-1):
        if self.content is None:
            return
        if width > 0 and height > 0:
            self.width = width
            self.height = height
        elif self.hidden_status == "show":
            self.width = self.shown_width
            self.height = self.shown_height
            self.edge_roundness = self.shown_edge_roundness
            self.edge_padding = self.shown_edge_padding
            self.title_height = self.shown_title_height
            self.title_horizontal_padding = self.shown_title_horizontal_padding
            self.title_vertical_padding = self.shown_title_vertical_padding
        elif self.hidden_status == "hidden":
            self.width = self.hidden_width
            self.height = self.hidden_height
            self.edge_roundness = self.hidden_edge_roundness
            self.edge_padding = self.hidden_edge_padding
            self.title_height = self.hidden_title_height
            self.title_horizontal_padding = self.hidden_title_horizontal_padding
            self.title_vertical_padding = self.hidden_title_vertical_padding
        elif self.hidden_status == "closed":
            self.width = self.closed_width
            self.height = self.closed_height
            self.edge_roundness = self.closed_edge_roundness
            self.edge_padding = self.closed_edge_padding
            self.title_height = self.closed_title_height
            self.title_horizontal_padding = self.closed_title_horizontal_padding
            self.title_vertical_padding = self.closed_title_vertical_padding

        self.content.setGeometry(int(self.edge_padding),
                                 int(self.title_height + self.edge_padding),
                                 int(width - 2 * self.edge_padding),
                                 int(height - 2 * self.edge_padding - self.title_height))

        self.hide_item.setPos(self.width - 26, 0)
        self.scale_item.setPos(self.width - 18, self.height + 2)
        self.resize_item.setPos(self.width - 38, self.height + 2)
        self.rotate_item.setPos(self.width + 2, self.height + 2)

    def changeSizeFromResize(self, width=-1, height=-1):
        if self.content is None:
            return
        elif self.setShowAndHiddenSameSize and self.hidden_status in ["show", "hidden"]:
            self.shown_width = self.hidden_width = width
            self.shown_height = self.hidden_height = height
        elif self.hidden_status == "show":
            self.shown_width = width
            self.shown_height = height
        elif self.hidden_status == "hidden":
            self.hidden_width = width
            self.hidden_height = height
        elif self.hidden_status == "closed":
            self.closed_width = width
            self.closed_height = height

    def changeHiddenStatus(self, status="show", toAllSelected: bool = False):
        if toAllSelected:
            if self.node.scene.grScene.selectedItems() != []:
                for item in self.node.scene.grScene.selectedItems():
                    if isinstance(item, QDMGraphicsNode):
                        item.changeHiddenStatus(status)
        if status not in ["show", "hidden", "closed"]:
            return None

        self.hidden_status = status
        self.changeContendSize()

        if status == "show": self.showNode()
        elif status == "hidden": self.hideNode()
        elif status == "closed": self.closeNode()

        self.updateSocketsAndEdgesPositions()

        return status

    def setScale(self, scale: float, toAllSelected: bool = False) -> None:
        if toAllSelected:
            if self.node.scene.grScene.selectedItems() != []:
                for item in self.node.scene.grScene.selectedItems():
                    if isinstance(item, QDMGraphicsNode):
                        item.setScale(scale)
        super().setScale(scale)
        self.updateSocketsAndEdgesPositions()

    def setRotation(self, angle: float, toAllSelected: bool = False) -> None:
        if toAllSelected:
            if self.node.scene.grScene.selectedItems() != []:
                for item in self.node.scene.grScene.selectedItems():
                    if isinstance(item, QDMGraphicsNode):
                        item.setRotation(angle)
        super().setRotation(angle)
        self.updateSocketsAndEdgesPositions()

    def showHideIcon(self, value: bool = True, toAllSelected: bool = False):
        if toAllSelected:
            if self.node.scene.grScene.selectedItems() != []:
                for item in self.node.scene.grScene.selectedItems():
                    if isinstance(item, QDMGraphicsNode):
                        item.showHideIcon(value)
        if value:
            self.hide_item.show()
        else:
            self.hide_item.hide()
    def showScaleRotResize(self, value: bool = True, type: str = "ALL", toAllSelected: bool = False):
        if toAllSelected:
            if self.node.scene.grScene.selectedItems() != []:
                for item in self.node.scene.grScene.selectedItems():
                    if isinstance(item, QDMGraphicsNode):
                        item.showScaleRotResize(value, type)
        if type in ["ALL", "ROTATION"]: self.rotate_item.setEnabled(value)
        if type in ["ALL", "SCALE"]: self.scale_item.setEnabled(value)
        if type in ["ALL", "RESIZE"]: self.resize_item.setEnabled(value)
        if value:
            if type in ["ALL", "ROTATION"]: self.rotate_item.show()
            if type in ["ALL", "SCALE"]: self.scale_item.show()
            if type in ["ALL", "RESIZE"]: self.resize_item.show()
        else:
            if type in ["ALL", "ROTATION"]:self.rotate_item.hide()
            if type in ["ALL", "SCALE"]: self.scale_item.hide()
            if type in ["ALL", "RESIZE"]: self.resize_item.hide()


    def updateSocketsAndEdgesPositions(self):
        if hasattr(self.node, "inputs") and hasattr(self.node, "outputs"):
            self.node.recalculateSocketPosition()
            self.node.updateConnectedEdges()

    def showNode(self):
        self.drawBackground = True
        self.drawOutline = True
        self.node.showNode()
        self.title_item.show()

    def hideNode(self):
        self.drawBackground = True
        self.drawOutline = True
        self.node.hideNode()
        self.title_item.hide()

    def closeNode(self):
        self.drawBackground = True
        self.drawOutline = True
        self.node.closeNode()
        self.title_item.hide()
        self.showScaleRotResize(False)

    def removeGrNode(self):
        pass

    def setLockedStatus(self, value: bool = True):
        if value:
            self.lockNode()
        else:
            self.editNode()

    def lockNode(self, toAllSelected: bool = False):
        if toAllSelected:
            if self.node.scene.grScene.selectedItems() != []:
                for item in self.node.scene.grScene.selectedItems():
                    if isinstance(item, QDMGraphicsNode):
                        item.lockNode()
                    if isinstance(item, QDMGraphicsEdge):
                        item.lockEdge()
        self.node.locked = True
        for socket in (self.node.inputs + self.node.outputs):
            socket.locked = True
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.node.lockNode()

    def editNode(self, toAllSelected: bool = False):
        if toAllSelected:
            if self.node.scene.grScene.selectedItems() != []:
                for item in self.node.scene.grScene.selectedItems():
                    if isinstance(item, QDMGraphicsNode):
                        item.editNode()
                    if isinstance(item, QDMGraphicsEdge):
                        item.lockEdge()
        self.node.locked = False
        for socket in (self.node.inputs + self.node.outputs):
            socket.locked = False
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.node.editNode()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """Painting the rounded rectanglar `Node`"""
        if self.title_item.isVisible():
            # title
            path_title = QPainterPath()
            path_title.setFillRule(Qt.WindingFill)
            path_title.addRoundedRect(0, 0, self.width, self.title_height, self.edge_roundness, self.edge_roundness)
            path_title.addRect(0, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
            path_title.addRect(self.width - self.edge_roundness, self.title_height - self.edge_roundness,
                               self.edge_roundness, self.edge_roundness)
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._brush_title)
            painter.drawPath(path_title.simplified())

        # content
        if self.drawBackground:
            path_content = QPainterPath()
            path_content.setFillRule(Qt.WindingFill)
            path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height,
                                        self.edge_roundness, self.edge_roundness)
            if self.grContent.isVisible() and self.title_item.isVisible():
                path_content.addRect(0, self.title_height, self.edge_roundness, self.edge_roundness)
                path_content.addRect(self.width - self.edge_roundness, self.title_height, self.edge_roundness,
                                     self.edge_roundness)
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._brush_background)
            painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(-1, -1, self.width + 2, self.height + 2, self.edge_roundness, self.edge_roundness)
        painter.setBrush(Qt.NoBrush)
        if self.hovered and not self.node.locked and self.drawHovered:
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        elif self.drawOutline or self.isSelected():
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
            painter.drawPath(path_outline.simplified())
        if self.showEvaluatedAnimation and self._draw_evaluated_outline:
            painter.setPen(self._pen_evaluated)
            painter.drawPath(path_outline.simplified())
        if self._draw_error_evaluated_outline:
            painter.setPen(self._pen_error_evaluated)
            painter.drawPath(path_outline.simplified())

        if self.evaluationIconVisibility and self.drawEvaluationIcon:
            # status icon
            offset = 24.0
            if self.node.isDirty():
                offset = 0.0
            elif self.node.isInvalid():
                offset = 48.0
            painter.drawImage(QRectF(-4, -4, 12.0, 12.0), self.statusIcons, QRectF(offset, 0, 24.0, 24.0))

        self.content.setGeometry(int(self.edge_padding),
                                 int(self.title_height + self.edge_padding),
                                 int(self.width - 2 * self.edge_padding),
                                 int(self.height - 2 * self.edge_padding - self.title_height))


class HideIconItem(QGraphicsItem):
    def __init__(self, parent, imageObj):
        super().__init__(parent)
        self.grNode = parent
        self.imageObj = imageObj
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemStacksBehindParent, False)

    def initTitleContextMenu(self):
        context_menu = QMenu()

        changeAct = context_menu.addAction("Show")
        changeAct.setProperty("actionType", "show")
        changeAct.setIcon(QIcon(QPixmap(self.imageObj).copy(QRect(0, 0, 48, 30))))
        changeAct = context_menu.addAction("Hide")
        changeAct.setProperty("actionType", "hide")
        changeAct.setIcon(QIcon(QPixmap(self.imageObj).copy(QRect(48, 0, 48, 30))))
        changeAct = context_menu.addAction("Close")
        changeAct.setProperty("actionType", "close")
        changeAct.setIcon(QIcon(QPixmap(self.imageObj).copy(QRect(96, 0, 48, 30))))

        context_menu.addSeparator()
        scale_menu = context_menu.addMenu("Scale node")
        for i in range(1, 10):
            scaleAct = scale_menu.addAction(str(i * 10) + "%")
            scaleAct.setProperty("actionType", "scale")
            scaleAct.setProperty("scaleFaktor", i / 10)
        for i in range(1, 11):
            scaleAct = scale_menu.addAction(str(i * 100) + "%")
            scaleAct.setProperty("actionType", "scale")
            scaleAct.setProperty("scaleFaktor", i)

        rotate_menu = context_menu.addMenu("Rotate node")
        for i in range(0, 12):
            rotateAct = rotate_menu.addAction(str(i * 30) + "°")
            rotateAct.setProperty("actionType", "rotate")
            rotateAct.setProperty("angle", i * 30)

        context_menu.addSeparator()
        changeAct = context_menu.addAction("Lock")
        changeAct.setProperty("actionType", "lock")
        changeAct.setIcon(QIcon(QPixmap(self.imageObj).copy(QRect(144, 0, 48, 30))))
        changeAct = context_menu.addAction("Edit")
        changeAct.setProperty("actionType", "edit")

        context_menu.addSeparator()
        showEvalIconAct = context_menu.addAction("Show eval icon")
        showEvalIconAct.setProperty("actionType", "show eval")
        hideEvalIconAct = context_menu.addAction("Hide eval icon")
        hideEvalIconAct.setProperty("actionType", "hide eval")

        context_menu.addSeparator()
        showSocketsAct = context_menu.addAction("Show sockets")
        showSocketsAct.setProperty("actionType", "show sockets")
        hideSocketsAct = context_menu.addAction("Hide sockets")
        hideSocketsAct.setProperty("actionType", "hide sockets")

        context_menu.addSeparator()
        showScaleRotResizeAct = context_menu.addAction("Show scale rot resize")
        showScaleRotResizeAct.setProperty("actionType", "show scale rot resize")
        hideScaleRotResizeAct = context_menu.addAction("Hide scale rot resize")
        hideScaleRotResizeAct.setProperty("actionType", "hide scale rot resize")

        return context_menu

    def contextMenuEvent(self, event):
        context_menu = self.initTitleContextMenu()
        view = self.grNode.node.scene.getView()

        zoom = int(self.grNode.node.scene.getView().zoom - 10)
        faktor = self.grNode.node.scene.getView().zoomInFactor
        zoomFaktor = float(faktor) ** zoom
        scaleFaktor = self.grNode.scale()

        viewPos = view.mapToGlobal(QPoint(0, 0))
        grNodePos = view.mapFromScene(self.grNode.pos().x(), self.grNode.pos().y())
        angle = self.grNode.rotation()
        newX = (event.pos().x() + self.pos().x()) * math.cos(math.radians(angle)) - \
               (event.pos().y() + self.pos().y()) * math.sin(math.radians(angle))
        newY = (event.pos().x() + self.pos().x()) * math.sin(math.radians(angle)) + \
               (event.pos().y() + self.pos().y()) * math.cos(math.radians(angle))
        eventPos = QPoint(int(newX * zoomFaktor * scaleFaktor),
                          int(newY * zoomFaktor * scaleFaktor))
        action = context_menu.exec_(viewPos + grNodePos + eventPos)

        if action and action.property("actionType"):
            if action.property("actionType") == "show":
                self.grNode.changeHiddenStatus("show", toAllSelected=True)
                self.grNode.node.scene.history.storeHistory("Changed hidden status to show node", setModified=True)
            elif action.property("actionType") == "hide":
                self.grNode.changeHiddenStatus("hidden", toAllSelected=True)
                self.grNode.node.scene.history.storeHistory("Changed hidden status to hidden node", setModified=True)
            elif action.property("actionType") == "close":
                self.grNode.changeHiddenStatus("closed", toAllSelected=True)
                self.grNode.node.scene.history.storeHistory("Changed hidden status to closed node", setModified=True)
            elif action.property("actionType") == "lock":
                self.grNode.lockNode(toAllSelected=True)
                self.grNode.node.scene.history.storeHistory("Changed locked status to locked node", setModified=True)
            elif action.property("actionType") == "edit":
                self.grNode.editNode(toAllSelected=True)
                self.grNode.node.scene.history.storeHistory("Changed locked status to edit node", setModified=True)
            elif action.property("actionType") == "hide eval":
                if self.grNode.node.scene.grScene.selectedItems() != []:
                    for item in self.grNode.node.scene.grScene.selectedItems():
                        if isinstance(item, QDMGraphicsNode):
                            item.evaluationIconVisibility = False
                self.grNode.evaluationIconVisibility = False
                self.grNode.node.scene.history.storeHistory("Hide evaluation icon", setModified=True)
            elif action.property("actionType") == "show eval":
                if self.grNode.node.scene.grScene.selectedItems() != []:
                    for item in self.grNode.node.scene.grScene.selectedItems():
                        if isinstance(item, QDMGraphicsNode):
                            item.evaluationIconVisibility = True
                self.grNode.evaluationIconVisibility = True
                self.grNode.node.scene.history.storeHistory("Show evaluation icon", setModified=True)
            elif action.property("actionType") == "hide sockets":
                if self.grNode.node.scene.grScene.selectedItems() != []:
                    for item in self.grNode.node.scene.grScene.selectedItems():
                        if isinstance(item, QDMGraphicsNode):
                            for socket in (item.node.inputs + item.node.outputs):
                                socket.grSocket.hiddenStatus = True
                for socket in (self.grNode.node.inputs+self.grNode.node.outputs):
                    socket.grSocket.hiddenStatus = True
                self.grNode.node.scene.history.storeHistory("Hide sockets", setModified=True)
            elif action.property("actionType") == "show sockets":
                for item in self.grNode.node.scene.grScene.selectedItems():
                    if isinstance(item, QDMGraphicsNode):
                        for socket in (item.node.inputs + item.node.outputs):
                            socket.grSocket.hiddenStatus = False
                for socket in (self.grNode.node.inputs + self.grNode.node.outputs):
                    socket.grSocket.hiddenStatus = False
                self.grNode.node.scene.history.storeHistory("Show sockets", setModified=True)
            elif action.property("actionType") == "scale" and action.property("scaleFaktor"):
                self.grNode.setScale(action.property("scaleFaktor"), toAllSelected=True)
                self.grNode.node.scene.history.storeHistory("Changed scale of node", setModified=True)
            elif action.property("actionType") == "rotate":
                self.grNode.setRotation(action.property("angle"), toAllSelected=True)
                self.grNode.node.scene.history.storeHistory("Changed rotation of node", setModified=True)
            elif action.property("actionType") == "show scale rot resize":
                self.grNode.showScaleRotResize(True, toAllSelected=True)
            elif action.property("actionType") == "hide scale rot resize":
                self.grNode.showScaleRotResize(False, toAllSelected=True)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        if self.grNode.node.locked:
            painter.drawImage(QRectF(0, 0, 24, 15), self.imageObj, QRectF(144, 0, 48.0, 30.0))
        elif self.grNode.hidden_status == "show":
            painter.drawImage(QRectF(0, 0, 24, 15), self.imageObj, QRectF(0, 0, 48.0, 30.0))
        elif self.grNode.hidden_status == "hidden":
            painter.drawImage(QRectF(0, 0, 24, 15), self.imageObj, QRectF(48, 0, 48.0, 30.0))
        elif self.grNode.hidden_status == "closed":
            painter.drawImage(QRectF(0, 0, 24, 15), self.imageObj, QRectF(96, 0, 48.0, 30.0))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.grNode.node.locked:
            if self.grNode.hidden_status == "show":
                self.grNode.changeHiddenStatus("hidden")
                self.grNode.node.scene.history.storeHistory("Changed hidden status to hidden node", setModified=True)
            elif self.grNode.hidden_status == "hidden":
                self.grNode.changeHiddenStatus("closed")
                self.grNode.node.scene.history.storeHistory("Changed hidden status to closed node", setModified=True)
            elif self.grNode.hidden_status == "closed":
                self.grNode.changeHiddenStatus("show")
                self.grNode.node.scene.history.storeHistory("Changed hidden status to show node", setModified=True)
            event.accept()
        else:
            super().mousePressEvent(event)

    def boundingRect(self) -> QRectF:
        """Defining Qt' bounding rectangle"""
        return QRectF(0, 0, 24, 15).normalized()


class TextItem(QGraphicsTextItem):
    def __init__(self, parent):
        super().__init__(parent)
        self.grNode = parent
        self.setTabChangesFocus(True)

    def initTitleContextMenu(self):
        context_menu = QMenu()

        changeAct = context_menu.addAction("Change title")
        changeAct.setProperty("actionType", "change")

        return context_menu

    def contextMenuEvent(self, event):
        if self.grNode.checkEventModifiersToSetIconVisibility(event):
            return

        if self.grNode.node.locked:
            return

        context_menu = self.initTitleContextMenu()
        view = self.grNode.node.scene.getView()

        zoom = int(self.grNode.node.scene.getView().zoom - 10)
        faktor = self.grNode.node.scene.getView().zoomInFactor
        zoomFaktor = float(faktor) ** zoom
        scaleFaktor = self.grNode.scale()

        viewPos = view.mapToGlobal(QPoint(0, 0))
        grNodePos = view.mapFromScene(self.grNode.pos().x(), self.grNode.pos().y())
        angle = self.grNode.rotation()
        newX = (event.pos().x() + self.pos().x()) * math.cos(math.radians(angle)) - \
               (event.pos().y() + self.pos().y()) * math.sin(math.radians(angle))
        newY = (event.pos().x() + self.pos().x()) * math.sin(math.radians(angle)) + \
               (event.pos().y() + self.pos().y()) * math.cos(math.radians(angle))
        eventPos = QPoint(int(newX * zoomFaktor * scaleFaktor),
                          int(newY * zoomFaktor * scaleFaktor))
        action = context_menu.exec_(viewPos + grNodePos + eventPos)

        if action and action.property("actionType"):
            if action.property("actionType") == "change":
                self.setTextInteractionFlags(Qt.TextEditorInteraction)
                self.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            event.accept()
            self.setTextInteractionFlags(Qt.NoTextInteraction)
            self.grNode.node.title = self.toPlainText()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.grNode.node.title = self.toPlainText()
        self.grNode.node.scene.history.storeHistory("Changed title of node", setModified=True)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().mousePressEvent(event)


class ScaleIconItem(QGraphicsItem):
    def __init__(self, parent, imageObj):
        super().__init__(parent)
        self.grNode = parent
        self.imageObj = imageObj
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemStacksBehindParent, False)
        self.startMousePos = QPointF(0.0, 0.0)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        self.startMousePos = event.pos()

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        if self.grNode.node.locked:
            return
        width = self.grNode.width
        mousePosX = event.pos().x() - self.startMousePos.x()
        grNodeScale = self.grNode.scale()
        newScale = grNodeScale * (1 + mousePosX / width)
        self.grNode.setScale(newScale)
        self.grNode.updateSocketsAndEdgesPositions()

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'):
        self.grNode.node.scene.history.storeHistory("Changed scale of node", setModified=True)
        super().mouseReleaseEvent(event)


    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        if self.grNode.node.locked:
            return
        painter.drawImage(QRectF(0, 0, 20, 15), self.imageObj, QRectF(0, 0, 40.0, 30.0))

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, 20, 15).normalized()


class ResizeIconItem(QGraphicsItem):
    def __init__(self, parent, imageObj):
        super().__init__(parent)
        self.grNode = parent
        self.imageObj = imageObj
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemStacksBehindParent, False)
        self.startMousePos = QPointF(0.0, 0.0)
        self.startGrNodeWidth = self.grNode.width
        self.startGrNodeHeight = self.grNode.height

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        self.startMousePos = self.mapToParent(event.pos())
        self.startGrNodeWidth = self.grNode.width
        self.startGrNodeHeight = self.grNode.height

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        if self.grNode.node.locked:
            return
        mousePos = self.mapToParent(event.pos()) - self.startMousePos
        if (event.modifiers() & Qt.ShiftModifier) or self.grNode.scaleEvenlyByScaleIcon:
            aspectRatio = self.startGrNodeHeight / self.startGrNodeWidth
            self.grNode.changeContendSize(int(self.startGrNodeWidth + mousePos.x()), int(self.startGrNodeHeight + mousePos.x() * aspectRatio))
            self.grNode.changeSizeFromResize(int(self.startGrNodeWidth + mousePos.x()), int(self.startGrNodeHeight + mousePos.x() * aspectRatio))
        else:
            self.grNode.changeContendSize(int(self.startGrNodeWidth + mousePos.x()), int(self.startGrNodeHeight + mousePos.y()))
            self.grNode.changeSizeFromResize(int(self.startGrNodeWidth + mousePos.x()), int(self.startGrNodeHeight + mousePos.y()))
        self.grNode.updateSocketsAndEdgesPositions()

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'):
        self.grNode.node.scene.history.storeHistory("Changed size of node", setModified=True)
        super().mouseReleaseEvent(event)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        if self.grNode.node.locked:
            return
        painter.drawImage(QRectF(0, 0, 20, 15), self.imageObj, QRectF(0, 0, 40.0, 30.0))

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, 20, 15).normalized()


class RotateIconItem(QGraphicsItem):
    def __init__(self, parent, imageObj):
        super().__init__(parent)
        self.grNode = parent
        self.imageObj = imageObj
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemStacksBehindParent, False)


    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        self.grNodeStartRot = self.grNode.rotation()
        self.grNodeStartPos = self.grNode.pos()
        self.globalRotationPoint = self.grNode.mapToParent(QPointF(self.grNode.width / 2, self.grNode.height / 2))
        self.startMousePos = self.grNode.mapToParent(self.mapToParent(event.pos()))

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        if self.grNode.node.locked:
            return
        mousePos = self.grNode.mapToParent(self.mapToParent(event.pos()))
        angle = self.getAngle(self.startMousePos, self.globalRotationPoint, mousePos)
        newPos = self.getPosFromRotation(self.grNodeStartPos.x(), self.grNodeStartPos.y(), angle,
                                         self.globalRotationPoint.x(), self.globalRotationPoint.y())
        self.grNode.setRotation(angle + + self.grNodeStartRot)
        self.grNode.setPos(newPos.x(), newPos.y())
        self.grNode.updateSocketsAndEdgesPositions()

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'):
        self.grNode.node.scene.history.storeHistory("Changed rotation of node", setModified=True)
        super().mouseReleaseEvent(event)

    def getPosFromRotation(self, x, y, angle, xOld=0, yOld=0):
        newX = (x-xOld) * math.cos(math.radians(angle)) - (y-yOld) * math.sin(math.radians(angle)) + xOld
        newY = (x-xOld) * math.sin(math.radians(angle)) + (y-yOld) * math.cos(math.radians(angle)) + yOld
        return QPointF(newX, newY)

    def getAngle(self, a, b, c):
        ang = math.degrees(math.atan2(c.y() - b.y(), c.x() - b.x()) - math.atan2(a.y() - b.y(), a.x() - b.x()))
        return ang

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        if self.grNode.node.locked:
            return
        painter.drawImage(QRectF(0, 0, 20, 15), self.imageObj, QRectF(0, 0, 40.0, 30.0))

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, 20, 15).normalized()