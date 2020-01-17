# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'openDialog.ui'
##
## Created by: Qt User Interface Compiler version 5.14.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

class Ui_Form(object):
    def setupUi(self, Form):
        if Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1305, 965)
        self.horizontalLayout_3 = QHBoxLayout(Form)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")

        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QSize(0, 70))
        self.groupBox.setMaximumSize(QSize(16777215, 70))
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.splitter = QSplitter(Form)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setHandleWidth(10)
        self.splitter.setChildrenCollapsible(True)
        self.tabWidget = QTabWidget(self.splitter)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setMinimumSize(QSize(300, 0))
        self.tabWidget.setMaximumSize(QSize(16777, 16777215))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.horizontalLayout_4 = QHBoxLayout(self.tab)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.treeView = QTreeView(self.tab)
        self.treeView.setObjectName(u"treeView")

        self.horizontalLayout_4.addWidget(self.treeView)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.horizontalLayout_5 = QHBoxLayout(self.tab_2)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.treeView_2 = QTreeView(self.tab_2)
        self.treeView_2.setObjectName(u"treeView_2")

        self.horizontalLayout_5.addWidget(self.treeView_2)

        self.tabWidget.addTab(self.tab_2, "")
        self.splitter.addWidget(self.tabWidget)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_2 = QLineEdit(self.layoutWidget)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.horizontalLayout.addWidget(self.lineEdit_2)

        self.pushButton_2 = QPushButton(self.layoutWidget)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton_3 = QPushButton(self.layoutWidget)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout.addWidget(self.pushButton_3)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.listView = QListView(self.layoutWidget)
        self.listView.setObjectName(u"listView")

        self.verticalLayout.addWidget(self.listView)

        self.splitter.addWidget(self.layoutWidget)

        self.verticalLayout_2.addWidget(self.splitter)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout_2.addWidget(self.lineEdit)

        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_2.addWidget(self.pushButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)


        self.retranslateUi(Form)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"File Open", None))
        self.groupBox.setTitle("")
        self.label.setText(QCoreApplication.translate("Form", u"> File Path Location > File Path Location > File Path Location > File Path Location > File Path Location", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Form", u"Assets", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Form", u"Shots", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"Search", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"list/Icon", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"Open", None))
    # retranslateUi

