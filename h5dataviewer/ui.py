# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'H5DataViewer.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(904, 679)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setAnimated(True)
        MainWindow.setDockOptions(QMainWindow.AnimatedDocks)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.dataWidget = QWidget()
        self.dataWidget.setObjectName(u"dataWidget")
        self.horizontalLayout_2 = QHBoxLayout(self.dataWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.splitter = QSplitter(self.dataWidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.groupBox = QGroupBox(self.splitter)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.dataTree = QTreeWidget(self.groupBox)
        self.dataTree.setObjectName(u"dataTree")

        self.verticalLayout.addWidget(self.dataTree)

        self.viewButton = QPushButton(self.groupBox)
        self.viewButton.setObjectName(u"viewButton")
        self.viewButton.setEnabled(False)

        self.verticalLayout.addWidget(self.viewButton)

        self.attrTree = QTreeWidget(self.groupBox)
        self.attrTree.setObjectName(u"attrTree")

        self.verticalLayout.addWidget(self.attrTree)

        self.splitter.addWidget(self.groupBox)
        self.groupBox_2 = QGroupBox(self.splitter)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.previewIndexLabel = QLabel(self.groupBox_2)
        self.previewIndexLabel.setObjectName(u"previewIndexLabel")

        self.verticalLayout_2.addWidget(self.previewIndexLabel)

        self.scrollArea = QScrollArea(self.groupBox_2)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 190, 493))
        self.previewLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.previewLayout.setObjectName(u"previewLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.splitter.addWidget(self.groupBox_2)

        self.horizontalLayout_2.addWidget(self.splitter)

        self.tabWidget.addTab(self.dataWidget, "")
        self.labelWidget = QWidget()
        self.labelWidget.setObjectName(u"labelWidget")
        self.horizontalLayout_3 = QHBoxLayout(self.labelWidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.labelTab = QTabWidget(self.labelWidget)
        self.labelTab.setObjectName(u"labelTab")

        self.horizontalLayout_3.addWidget(self.labelTab)

        self.tabWidget.addTab(self.labelWidget, "")
        self.tfWidget = QWidget()
        self.tfWidget.setObjectName(u"tfWidget")
        self.horizontalLayout_4 = QHBoxLayout(self.tfWidget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.tfTree = QTreeWidget(self.tfWidget)
        self.tfTree.setObjectName(u"tfTree")

        self.horizontalLayout_4.addWidget(self.tfTree)

        self.tabWidget.addTab(self.tfWidget, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 904, 28))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionExit)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.labelTab.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"H5DataViewer", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"&Open", None))
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
#if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(QCoreApplication.translate("MainWindow", u"Esc", None))
#endif // QT_CONFIG(shortcut)
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Data", None))
        ___qtreewidgetitem = self.dataTree.headerItem()
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("MainWindow", u"Value", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("MainWindow", u"dtype", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"Type", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"/", None));
        self.viewButton.setText(QCoreApplication.translate("MainWindow", u"View", None))
        ___qtreewidgetitem1 = self.attrTree.headerItem()
        ___qtreewidgetitem1.setText(1, QCoreApplication.translate("MainWindow", u"Value", None));
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("MainWindow", u"Attribute", None));
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Preview", None))
        self.previewIndexLabel.setText(QCoreApplication.translate("MainWindow", u"Index", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.dataWidget), QCoreApplication.translate("MainWindow", u"Data", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.labelWidget), QCoreApplication.translate("MainWindow", u"Label", None))
        ___qtreewidgetitem2 = self.tfTree.headerItem()
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("MainWindow", u"Frame ID", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tfWidget), QCoreApplication.translate("MainWindow", u"Transforms", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi

