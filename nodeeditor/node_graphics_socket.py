# -*- coding: utf-8 -*-
"""
A module containing Graphics representation of a :class:`~nodeeditor.node_socket.Socket`
"""
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QRectF

from nodeeditor.utils_no_qt import dumpException
from nodeeditor.var_type_conf import TYPE_NAMES

class QDMGraphicsSocket(QGraphicsItem):
    """Class representing Graphic `Socket` in ``QGraphicsScene``"""
    def __init__(self, socket:'Socket'):
        """
        :param socket: reference to :class:`~nodeeditor.node_socket.Socket`
        :type socket: :class:`~nodeeditor.node_socket.Socket`
        """
        super().__init__(socket.node.grNode)

        self.socket = socket
        self.setAcceptHoverEvents(True)

        self.isHighlighted = False

        self.radius = 10.0
        self.outline_width = 1.0
        self.initAssets()

        self.hiddenStatus = False
        self.hiddenRadius = 3.0

        self.setToolTipText()

    @property
    def socket_type(self):
        return self.socket.socket_type

    def setToolTipText(self):
        toolTipText = ""
        for supportedType in self.socket.supportedTypes:
            if toolTipText != "":
                toolTipText += " / "
            toolTipText += TYPE_NAMES[supportedType]
        self.setToolTip(toolTipText)

    def getSocketColor(self, key):
        """Returns the ``QColor`` for this ``key``"""
        try:
            if self._socket_color: return self._socket_color
            if type(key) == int: return self.socket.node.scene.socketColors[key]
            elif type(key) == str: return QColor(key)
        except Exception as e: dumpException(e)
        return Qt.transparent

    def changeSocketType(self):
        """Change the Socket Type"""
        self._color_background = self.getSocketColor(self.socket_type)
        self._brush = QBrush(self._color_background)
        # print("Socket changed to:", self._color_background.getRgbF())
        self.update()

    def updateColor(self):
        self.changeSocketType()

    def setLocalColor(self, color: QColor = None):
        self._socket_color = color

    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""

        # determine socket color
        self._socket_color = None

        self._color_background = self.getSocketColor(self.socket_type)
        self._color_outline = QColor("#FF000000")
        self._color_highlight = QColor("#FF37A6FF")
        self._color_not_connected = QColor("#99000000")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._pen_highlight = QPen(self._color_highlight)
        self._pen_highlight.setWidthF(2.0)
        self._brush = QBrush(self._color_background)
        self._not_connected_brush = QBrush(self._color_not_connected)

        self._hidden_color_background = QColor("#33000000")
        self._hidden_color_outline = QColor("#00000000")
        self._hidden_pen = QPen(self._hidden_color_outline)
        self._hidden_brush = QBrush(self._hidden_color_background)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent'):
        self.isHighlighted = True

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent'):
        self.isHighlighted = False

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent'):
        self.isHighlighted = True

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """Painting a circle"""
        if self.hiddenStatus:
            painter.setBrush(self._hidden_brush)
            painter.setPen(self._hidden_pen if not self.isHighlighted or self.socket.locked else self._pen_highlight)
            painter.drawEllipse(int(-self.hiddenRadius), int(-self.hiddenRadius), int(2 * self.hiddenRadius), int(2 * self.hiddenRadius))
        else:
            painter.setBrush(self._brush)
            painter.setPen(self._pen if not self.isHighlighted or self.socket.locked else self._pen_highlight)
            painter.drawEllipse(int(-self.radius / 2), int(-self.radius / 2), int(self.radius), int(self.radius))

            if not self.socket.hasAnyEdge():
                painter.setBrush(self._not_connected_brush)
                painter.setPen(self._pen if not self.isHighlighted or self.socket.locked else self._pen_highlight)
                painter.drawEllipse(int(-self.radius / 2), int(-self.radius / 2), int(self.radius), int(self.radius))

    def boundingRect(self) -> QRectF:
        """Defining Qt' bounding rectangle"""
        return QRectF(
            - self.radius - self.outline_width,
            - self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )
