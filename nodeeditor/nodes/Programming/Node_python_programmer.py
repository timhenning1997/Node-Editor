from io import StringIO
from contextlib import redirect_stdout

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QTextDocument, QSyntaxHighlighter, QFont, QTextCharFormat

from PyQt5.QtWidgets import QLabel, QTextEdit, QVBoxLayout
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *



class Content(QDMNodeContentWidget):
    def initUI(self):
        self.editorTextEdit = QTextEdit()
        self.editorTextEdit.setObjectName("editorTextEditObj")
        self.editorTextEdit.setStyleSheet("#editorTextEditObj {background-color: #111111; color: #eeeeee}")
        self.editorTextEdit.setTabStopDistance(20)
        self.editorTextEdit.setTextColor(QColor(200, 200, 200))
        self.editorTextEdit.setPlainText("# comment")
        self.highlight = PythonHighlighter(self.editorTextEdit.document())

        self.consoleLabel = QLabel("")
        self.consoleLabel.setStyleSheet("color: gray")
        self.consoleLabel.hide()

        self.errorLabel = QLabel("")
        self.errorLabel.setStyleSheet("color: red")
        self.errorLabel.hide()

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.editorTextEdit)
        layout.addWidget(self.consoleLabel)
        layout.addWidget(self.errorLabel)

        self.setLayout(layout)

    def sendData(self, data):
        self.node.sendDataFromSocket(data)

    def excecuteScript(self, obj):
        localDict = {"input": obj}
        text = self.editorTextEdit.toPlainText()
        self.resultName = ""
        localDict.update(globals())
        localDict.update(locals())
        try:
            with redirect_stdout(StringIO()) as f:
                exec(text, localDict)
            s = str(f.getvalue()).replace("<", "&lt;").replace(">", "&gt;")
            self.consoleLabel.setText(s.strip())
            if s:
                self.consoleLabel.show()
            else:
                self.consoleLabel.hide()
            self.errorLabel.hide()
        except Exception as inst:
            self.errorLabel.show()
            self.errorLabel.setText(str(inst))


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(350, 264)
        self.setHiddenSize(350, 230)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_ProgrammingPythonProgrammerNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Python Programmer", inputs: list = [VAR_TYPE_NOT_DEFINED], outputs: list = [VAR_TYPE_NOT_DEFINED]):
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

        self.content.excecuteScript(data)
        #self.sendDataFromSocket(None)


def format(color, style=''):
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)
    return _format


class PythonHighlighter (QSyntaxHighlighter):
    STYLES = {
        'keyword': format('#7986CB'),
        'operator': format('#9575CD'),
        'brace': format('#A1887F'),
        'defclass': format('#00897B', 'bold'),
        'string': format('#90A4AE', 'italic'),
        'string2': format('#26A69A'),
        'comment': format('#546E7A', 'italic'),
        'self': format('#7E57C2', 'italic'),
        'numbers': format('#6897bb'),
    }

    keywords = ['and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False']

    operators = ['=', '==', '!=', '<', '<=', '>', '>=', '\+', '-', '\*', '/', '//', '\%', '\*\*', '\+=', '-=', '\*=', '/=', '\%=', '\^', '\|', '\&', '\~', '>>', '<<']
    braces = ['\{', '\}', '\(', '\)', '\[', '\]']

    def __init__(self, parent: QTextDocument) -> None:
        super().__init__(parent)
        self.tri_single = (QRegExp("'''"), 1, self.STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, self.STYLES['string2'])

        rules = []
        rules += [(r'\b%s\b' % w, 0, self.STYLES['keyword'])
            for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, self.STYLES['operator'])
            for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, self.STYLES['brace'])
            for b in PythonHighlighter.braces]
        rules += [
            (r'\bself\b', 0, self.STYLES['self']),
            (r'\bdef\b\s*(\w+)', 1, self.STYLES['defclass']),
            (r'\bclass\b\s*(\w+)', 1, self.STYLES['defclass']),
            (r'\b[+-]?[0-9]+[lL]?\b', 0, self.STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, self.STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, self.STYLES['numbers']),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.STYLES['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.STYLES['string']),
            (r'#[^\n]*', 0, self.STYLES['comment'])]

        self.rules = [(QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        self.tripleQuoutesWithinStrings = []
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)
            if index >= 0:
                if expression.pattern() in [r'"[^"\\]*(\\.[^"\\]*)*"', r"'[^'\\]*(\\.[^'\\]*)*'"]:
                    innerIndex = self.tri_single[0].indexIn(text, index + 1)
                    if innerIndex == -1:
                        innerIndex = self.tri_double[0].indexIn(text, index + 1)

                    if innerIndex != -1:
                        tripleQuoteIndexes = range(innerIndex, innerIndex + 3)
                        self.tripleQuoutesWithinStrings.extend(tripleQuoteIndexes)

            while index >= 0:
                if index in self.tripleQuoutesWithinStrings:
                    index += 1
                    expression.indexIn(text, index)
                    continue

                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        else:
            start = delimiter.indexIn(text)
            if start in self.tripleQuoutesWithinStrings:
                return False
            add = delimiter.matchedLength()

        while start >= 0:
            end = delimiter.indexIn(text, start + add)
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            self.setFormat(start, length, style)
            start = delimiter.indexIn(text, start + length)

        if self.currentBlockState() == in_state:
            return True
        else:
            return False
