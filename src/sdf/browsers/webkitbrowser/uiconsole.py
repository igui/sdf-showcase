# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\uiconsole.ui'
#
# Created: Sat Jul 23 20:02:45 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ConsoleWidget(object):
    def setupUi(self, ConsoleWidget):
        ConsoleWidget.setObjectName(_fromUtf8("ConsoleWidget"))
        ConsoleWidget.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(ConsoleWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.consoleOutputBox = QtGui.QTextEdit(ConsoleWidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans Mono"))
        font.setPointSize(10)
        self.consoleOutputBox.setFont(font)
        self.consoleOutputBox.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.consoleOutputBox.setReadOnly(True)
        self.consoleOutputBox.setHtml(_fromUtf8("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans Mono\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>"))
        self.consoleOutputBox.setAcceptRichText(False)
        self.consoleOutputBox.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.consoleOutputBox.setObjectName(_fromUtf8("consoleOutputBox"))
        self.verticalLayout.addWidget(self.consoleOutputBox)
        self.consoleCommandLine = HistoryLineEdit(ConsoleWidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans Mono"))
        font.setPointSize(10)
        self.consoleCommandLine.setFont(font)
        self.consoleCommandLine.setFrame(False)
        self.consoleCommandLine.setCursorPosition(0)
        self.consoleCommandLine.setObjectName(_fromUtf8("consoleCommandLine"))
        self.verticalLayout.addWidget(self.consoleCommandLine)

        self.retranslateUi(ConsoleWidget)
        QtCore.QMetaObject.connectSlotsByName(ConsoleWidget)

    def retranslateUi(self, ConsoleWidget):
        ConsoleWidget.setWindowTitle(QtGui.QApplication.translate("ConsoleWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

from .historylineedit import HistoryLineEdit
