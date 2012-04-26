# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\uiwebviewtab.ui'
#
# Created: Sat Jul 23 20:03:42 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_webViewTab(object):
    def setupUi(self, webViewTab):
        webViewTab.setObjectName(_fromUtf8("webViewTab"))
        webViewTab.resize(528, 362)
        self.gridLayout = QtGui.QGridLayout(webViewTab)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.webView = QtWebKit.QWebView(webViewTab)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.gridLayout.addWidget(self.webView, 0, 0, 2, 2)
        self.__gridLayout = QtGui.QGridLayout()
        self.__gridLayout.setObjectName(_fromUtf8("__gridLayout"))
        self.__horizontalLayout = QtGui.QHBoxLayout()
        self.__horizontalLayout.setObjectName(_fromUtf8("__horizontalLayout"))
        self.cargandoProgressBar = QtGui.QProgressBar(webViewTab)
        self.cargandoProgressBar.setEnabled(True)
        self.cargandoProgressBar.setMaximumSize(QtCore.QSize(16777215, 16))
        self.cargandoProgressBar.setProperty(_fromUtf8("value"), 66)
        self.cargandoProgressBar.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.cargandoProgressBar.setTextVisible(True)
        self.cargandoProgressBar.setInvertedAppearance(False)
        self.cargandoProgressBar.setTextDirection(QtGui.QProgressBar.BottomToTop)
        self.cargandoProgressBar.setObjectName(_fromUtf8("cargandoProgressBar"))
        self.__horizontalLayout.addWidget(self.cargandoProgressBar)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.__horizontalLayout.addItem(spacerItem)
        self.__gridLayout.addLayout(self.__horizontalLayout, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.__gridLayout.addItem(spacerItem1, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.__gridLayout, 1, 1, 1, 1)

        self.retranslateUi(webViewTab)
        QtCore.QMetaObject.connectSlotsByName(webViewTab)

    def retranslateUi(self, webViewTab):
        webViewTab.setWindowTitle(QtGui.QApplication.translate("webViewTab", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.cargandoProgressBar.setFormat(QtGui.QApplication.translate("webViewTab", "Cargando:%p%", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
