# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\uiwebkitbrowser.ui'
#
# Created: Sat Jul 23 20:03:12 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_WebKitBrowser(object):
    def setupUi(self, WebKitBrowser):
        WebKitBrowser.setObjectName(_fromUtf8("WebKitBrowser"))
        WebKitBrowser.resize(800, 666)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/SDF.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        WebKitBrowser.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(WebKitBrowser)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_3 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setContentsMargins(0, -1, -1, -1)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.atrasButton = QtGui.QPushButton(self.centralwidget)
        self.atrasButton.setMaximumSize(QtCore.QSize(36, 16777215))
        self.atrasButton.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/go-previous.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.atrasButton.setIcon(icon1)
        self.atrasButton.setIconSize(QtCore.QSize(24, 24))
        self.atrasButton.setFlat(True)
        self.atrasButton.setObjectName(_fromUtf8("atrasButton"))
        self.horizontalLayout_2.addWidget(self.atrasButton)
        self.adelanteButton = QtGui.QPushButton(self.centralwidget)
        self.adelanteButton.setMaximumSize(QtCore.QSize(36, 16777215))
        self.adelanteButton.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/go-next.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.adelanteButton.setIcon(icon2)
        self.adelanteButton.setIconSize(QtCore.QSize(24, 24))
        self.adelanteButton.setFlat(True)
        self.adelanteButton.setObjectName(_fromUtf8("adelanteButton"))
        self.horizontalLayout_2.addWidget(self.adelanteButton)
        self.refrescarButton = QtGui.QPushButton(self.centralwidget)
        self.refrescarButton.setMaximumSize(QtCore.QSize(36, 16777215))
        self.refrescarButton.setText(_fromUtf8(""))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/view-refresh.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.refrescarButton.setIcon(icon3)
        self.refrescarButton.setIconSize(QtCore.QSize(24, 24))
        self.refrescarButton.setFlat(True)
        self.refrescarButton.setObjectName(_fromUtf8("refrescarButton"))
        self.horizontalLayout_2.addWidget(self.refrescarButton)
        self.homeButton = QtGui.QPushButton(self.centralwidget)
        self.homeButton.setMaximumSize(QtCore.QSize(36, 16777215))
        self.homeButton.setText(_fromUtf8(""))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/go-home.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.homeButton.setIcon(icon4)
        self.homeButton.setIconSize(QtCore.QSize(24, 24))
        self.homeButton.setFlat(True)
        self.homeButton.setObjectName(_fromUtf8("homeButton"))
        self.horizontalLayout_2.addWidget(self.homeButton)
        self.pararButton = QtGui.QPushButton(self.centralwidget)
        self.pararButton.setMaximumSize(QtCore.QSize(36, 16777215))
        self.pararButton.setText(_fromUtf8(""))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/process-stop.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pararButton.setIcon(icon5)
        self.pararButton.setIconSize(QtCore.QSize(24, 24))
        self.pararButton.setFlat(True)
        self.pararButton.setObjectName(_fromUtf8("pararButton"))
        self.horizontalLayout_2.addWidget(self.pararButton)
        self.direccionlineEdit = QtGui.QLineEdit(self.centralwidget)
        self.direccionlineEdit.setObjectName(_fromUtf8("direccionlineEdit"))
        self.horizontalLayout_2.addWidget(self.direccionlineEdit)
        self.imagenesPushButton = QtGui.QPushButton(self.centralwidget)
        self.imagenesPushButton.setMaximumSize(QtCore.QSize(16777215, 28))
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/image-bmp.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.imagenesPushButton.setIcon(icon6)
        self.imagenesPushButton.setIconSize(QtCore.QSize(20, 20))
        self.imagenesPushButton.setCheckable(True)
        self.imagenesPushButton.setObjectName(_fromUtf8("imagenesPushButton"))
        self.horizontalLayout_2.addWidget(self.imagenesPushButton)
        self.consolaButton = QtGui.QPushButton(self.centralwidget)
        self.consolaButton.setMaximumSize(QtCore.QSize(16777215, 28))
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/utilities-terminal.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.consolaButton.setIcon(icon7)
        self.consolaButton.setCheckable(True)
        self.consolaButton.setObjectName(_fromUtf8("consolaButton"))
        self.horizontalLayout_2.addWidget(self.consolaButton)
        self.gridLayout_3.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.tabWebViews = QtGui.QTabWidget(self.centralwidget)
        self.tabWebViews.setMovable(True)
        self.tabWebViews.setObjectName(_fromUtf8("tabWebViews"))
        self.gridLayout_3.addWidget(self.tabWebViews, 1, 0, 1, 1)
        WebKitBrowser.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(WebKitBrowser)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        WebKitBrowser.setStatusBar(self.statusbar)
        self.consoleDock = QtGui.QDockWidget(WebKitBrowser)
        self.consoleDock.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        self.consoleDock.setObjectName(_fromUtf8("consoleDock"))
        self.consoleDockContents = QtGui.QWidget()
        self.consoleDockContents.setObjectName(_fromUtf8("consoleDockContents"))
        self.consoleDock.setWidget(self.consoleDockContents)
        WebKitBrowser.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.consoleDock)
        self.actionNuevaPestana = QtGui.QAction(WebKitBrowser)
        self.actionNuevaPestana.setObjectName(_fromUtf8("actionNuevaPestana"))

        self.retranslateUi(WebKitBrowser)
        self.tabWebViews.setCurrentIndex(-1)
        QtCore.QObject.connect(self.consolaButton, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.consoleDock.setVisible)
        QtCore.QObject.connect(self.consoleDock, QtCore.SIGNAL(_fromUtf8("visibilityChanged(bool)")), self.consolaButton.setChecked)
        QtCore.QMetaObject.connectSlotsByName(WebKitBrowser)
        WebKitBrowser.setTabOrder(self.direccionlineEdit, self.atrasButton)
        WebKitBrowser.setTabOrder(self.atrasButton, self.adelanteButton)
        WebKitBrowser.setTabOrder(self.adelanteButton, self.refrescarButton)
        WebKitBrowser.setTabOrder(self.refrescarButton, self.homeButton)
        WebKitBrowser.setTabOrder(self.homeButton, self.pararButton)
        WebKitBrowser.setTabOrder(self.pararButton, self.consolaButton)
        WebKitBrowser.setTabOrder(self.consolaButton, self.imagenesPushButton)
        WebKitBrowser.setTabOrder(self.imagenesPushButton, self.tabWebViews)

    def retranslateUi(self, WebKitBrowser):
        WebKitBrowser.setWindowTitle(QtGui.QApplication.translate("WebKitBrowser", "Navegador WebKit", None, QtGui.QApplication.UnicodeUTF8))
        self.atrasButton.setToolTip(QtGui.QApplication.translate("WebKitBrowser", "Ir atrás", None, QtGui.QApplication.UnicodeUTF8))
        self.adelanteButton.setToolTip(QtGui.QApplication.translate("WebKitBrowser", "Ir adelante", None, QtGui.QApplication.UnicodeUTF8))
        self.refrescarButton.setToolTip(QtGui.QApplication.translate("WebKitBrowser", "Recargar", None, QtGui.QApplication.UnicodeUTF8))
        self.homeButton.setToolTip(QtGui.QApplication.translate("WebKitBrowser", "Página de inicio", None, QtGui.QApplication.UnicodeUTF8))
        self.homeButton.setShortcut(QtGui.QApplication.translate("WebKitBrowser", "Ctrl+H", None, QtGui.QApplication.UnicodeUTF8))
        self.pararButton.setToolTip(QtGui.QApplication.translate("WebKitBrowser", "Detener la descarga de la página", None, QtGui.QApplication.UnicodeUTF8))
        self.imagenesPushButton.setText(QtGui.QApplication.translate("WebKitBrowser", "Ver Imágenes", None, QtGui.QApplication.UnicodeUTF8))
        self.consolaButton.setText(QtGui.QApplication.translate("WebKitBrowser", "Consola", None, QtGui.QApplication.UnicodeUTF8))
        self.consoleDock.setWindowTitle(QtGui.QApplication.translate("WebKitBrowser", "Consola", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNuevaPestana.setText(QtGui.QApplication.translate("WebKitBrowser", "nuevaPestana", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNuevaPestana.setShortcut(QtGui.QApplication.translate("WebKitBrowser", "Ctrl+T", None, QtGui.QApplication.UnicodeUTF8))

#from .resources import resources
