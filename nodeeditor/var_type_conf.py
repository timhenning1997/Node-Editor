from PyQt5.QtGui import QColor

VAR_TYPE_NOT_DEFINED = 1
VAR_TYPE_INT = 2
VAR_TYPE_FLOAT = 3
VAR_TYPE_STR = 4
VAR_TYPE_LIST = 5
VAR_TYPE_DICT = 6
VAR_TYPE_PIXMAP = 7
VAR_TYPE_BOOL = 7

LEFT_TOP = 1
LEFT_CENTER = 2
LEFT_BOTTOM = 3
RIGHT_TOP = 4
RIGHT_CENTER = 5
RIGHT_BOTTOM = 6

TYPE_COLORS = [
                QColor("#FF000000"),    # black color not used
                QColor("#FFFFFFFF"),    # white color used for "not defined variable type"
                QColor("#FFFF7700"),
                QColor("#FF52e220"),
                QColor("#FF0056a6"),
                QColor("#FFa86db1"),
                QColor("#FFb54747"),
                QColor("#FFdbe220"),
                QColor("#FFFF5733"),
                ]

TYPE_NAMES = [
                "NOT_USED",
                "NOT_DEFINED",
                "INT",
                "FLOAT",
                "STR",
                "LIST",
                "DICT",
                "PIXMAP",
                "BOOL",
                ]

EDGE_COLOR = QColor("#101010")

EVAL_HIGHLIGHT_COLOR = QColor("#FFFFFF00")
