# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dialog_app(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(499, 464)
        self.layoutWidget_2 = QtWidgets.QWidget(Dialog)
        self.layoutWidget_2.setGeometry(QtCore.QRect(10, 10, 481, 441))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.layoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btn_show = QtWidgets.QPushButton(self.layoutWidget_2)
        self.btn_show.setObjectName("btn_show")
        self.horizontalLayout_2.addWidget(self.btn_show)
        self.btn_delete = QtWidgets.QPushButton(self.layoutWidget_2)
        self.btn_delete.setObjectName("btn_delete")
        self.horizontalLayout_2.addWidget(self.btn_delete)
        self.btn_kill = QtWidgets.QPushButton(self.layoutWidget_2)
        self.btn_kill.setObjectName("btn_kill")
        self.horizontalLayout_2.addWidget(self.btn_kill)
        self.btn_start = QtWidgets.QPushButton(self.layoutWidget_2)
        self.btn_start.setObjectName("btn_start")
        self.horizontalLayout_2.addWidget(self.btn_start)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(self.layoutWidget_2)
        self.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout_2.addWidget(self.tableWidget, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Applications"))
        self.btn_kill.setText(_translate("Dialog", "Kill"))
        self.btn_show.setText(_translate("Dialog", "Show"))
        self.btn_delete.setText(_translate("Dialog", "Clear"))
        self.btn_start.setText(_translate("Dialog", "Start"))


class Ui_dialog_capture(object):
    def setupUi(self, Dialog_capture):
        Dialog_capture.setObjectName("Dialog_capture")
        Dialog_capture.resize(510, 382)
        self.layoutWidget = QtWidgets.QWidget(Dialog_capture)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 491, 361))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.graphicsView = QtWidgets.QGraphicsView(self.layoutWidget)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_2 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_2.setObjectName("btn_cap")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_3.setObjectName("btn_save")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog_capture)
        QtCore.QMetaObject.connectSlotsByName(Dialog_capture)

    def retranslateUi(self, Dialog_capture):
        _translate = QtCore.QCoreApplication.translate
        Dialog_capture.setWindowTitle(_translate("Dialog_capture", "Screen Capture"))
        self.pushButton_2.setText(_translate("Dialog_capture", "Capture"))
        self.pushButton_3.setText(_translate("Dialog_capture", "Save"))

class Ui_dialog_keystroke(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(506, 359)
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 481, 341))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btn_hook = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_hook.setObjectName("btn_hook")
        self.horizontalLayout_2.addWidget(self.btn_hook)
        self.btn_unhook = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_unhook.setObjectName("btn_unhook")
        self.horizontalLayout_2.addWidget(self.btn_unhook)
        self.btn_key = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_key.setObjectName("btn_key")
        self.horizontalLayout_2.addWidget(self.btn_key)
        self.btn_delete = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_delete.setObjectName("btn_delete")
        self.horizontalLayout_2.addWidget(self.btn_delete)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.layoutWidget)
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.gridLayout.addWidget(self.textBrowser_2, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Key Stroke"))
        self.btn_hook.setText(_translate("Dialog", "Hook"))
        self.btn_unhook.setText(_translate("Dialog", "Unhook"))
        self.btn_key.setText(_translate("Dialog", "Print"))
        self.btn_delete.setText(_translate("Dialog", "Clear"))
        
class Ui_dialog_kill(object):
    def setupUi(self, Dialog_Kill):
        Dialog_Kill.setObjectName("Dialog_Kill")
        Dialog_Kill.resize(389, 50)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog_Kill.sizePolicy().hasHeightForWidth())
        Dialog_Kill.setSizePolicy(sizePolicy)

        self.layoutWidget = QtWidgets.QWidget(Dialog_Kill)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 371, 27))
        self.layoutWidget.setObjectName("layoutWidget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.label.setText("Enter ID:")  
        self.horizontalLayout.addWidget(self.label) 

        self.lineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)

        self.btn_kill = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_kill.setObjectName("btn_kill")
        self.horizontalLayout.addWidget(self.btn_kill)

        self.retranslateUi(Dialog_Kill)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Kill)

    def retranslateUi(self, Dialog_Kill):
        _translate = QtCore.QCoreApplication.translate
        Dialog_Kill.setWindowTitle(_translate("Dialog_Kill", "Kill"))
        self.btn_kill.setText(_translate("Dialog_Kill", "Kill"))

class Ui_dialog_main(object):
    def setupUi(self, dialog_main):
        dialog_main.setObjectName("dialog_main")
        dialog_main.resize(337, 315)
        dialog_main.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(dialog_main)
        self.gridLayout.setObjectName("gridLayout")
        self.btn_key = QtWidgets.QPushButton(dialog_main)
        self.btn_key.setObjectName("btn_key")
        self.gridLayout.addWidget(self.btn_key, 3, 0, 1, 1)
        self.btn_cap = QtWidgets.QPushButton(dialog_main)
        self.btn_cap.setObjectName("btn_cap")
        self.gridLayout.addWidget(self.btn_cap, 5, 0, 1, 1)
        self.btn_exit = QtWidgets.QPushButton(dialog_main)
        self.btn_exit.setObjectName("btn_exit")
        self.gridLayout.addWidget(self.btn_exit, 8, 0, 1, 1) 
        self.btn_shutdown = QtWidgets.QPushButton(dialog_main)
        self.btn_shutdown.setObjectName("btn_shutdown")
        self.gridLayout.addWidget(self.btn_shutdown, 6, 0, 1, 1) 
        self.btn_reset = QtWidgets.QPushButton(dialog_main)
        self.btn_reset.setObjectName("btn_reset")
        self.gridLayout.addWidget(self.btn_reset, 7, 0, 1, 1)
        self.btn_process = QtWidgets.QPushButton(dialog_main)
        self.btn_process.setObjectName("btn_process")
        self.gridLayout.addWidget(self.btn_process, 1, 0, 1, 1)
        self.btn_app = QtWidgets.QPushButton(dialog_main)
        self.btn_app.setObjectName("btn_app")
        self.gridLayout.addWidget(self.btn_app, 2, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit = QtWidgets.QLineEdit(dialog_main)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.btn_connect = QtWidgets.QPushButton(dialog_main)
        self.btn_connect.setObjectName("btn_connect")
        self.horizontalLayout.addWidget(self.btn_connect)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtWidgets.QLabel(dialog_main)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.btn_files = QtWidgets.QPushButton(dialog_main)
        self.gridLayout.addWidget(self.btn_files, 4, 0, 1, 1)

        self.retranslateUi(dialog_main)
        QtCore.QMetaObject.connectSlotsByName(dialog_main)

    def retranslateUi(self, dialog_main):
        _translate = QtCore.QCoreApplication.translate
        dialog_main.setWindowTitle(_translate("dialog_main", "Main"))
        self.btn_key.setText(_translate("dialog_main", "Keystroke"))
        self.btn_cap.setText(_translate("dialog_main", "Screenshot"))
        self.btn_exit.setText(_translate("dialog_main", "Exit"))
        self.btn_shutdown.setText(_translate("dialog_main", "Shutdown"))
        self.btn_reset.setText(_translate("dialog_main", "Reset"))
        self.btn_process.setText(_translate("dialog_main", "Processes"))
        self.btn_app.setText(_translate("dialog_main", "Applications"))
        self.btn_files.setText(_translate("dialog_main", "Files"))
        self.btn_connect.setText(_translate("dialog_main", "Connect"))
        self.label.setText(_translate("dialog_main", "No Connection"))

class Ui_dialog_process(object):
    def setupUi(self, Dialog_process):
        Dialog_process.setObjectName("Dialog_process")
        Dialog_process.resize(504, 460)
        self.layoutWidget = QtWidgets.QWidget(Dialog_process)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 481, 441))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_show = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_show.setObjectName("btn_show")
        self.horizontalLayout.addWidget(self.btn_show)
        self.btn_delete = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_delete.setObjectName("btn_delete")
        self.horizontalLayout.addWidget(self.btn_delete)
        self.btn_kill = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_kill.setObjectName("btn_kill")
        self.horizontalLayout.addWidget(self.btn_kill)
        self.btn_start = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_start.setObjectName("btn_start")
        self.horizontalLayout.addWidget(self.btn_start)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(self.layoutWidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 1)

        self.retranslateUi(Dialog_process)
        QtCore.QMetaObject.connectSlotsByName(Dialog_process)

    def retranslateUi(self, Dialog_process):
        _translate = QtCore.QCoreApplication.translate
        Dialog_process.setWindowTitle(_translate("Dialog_process", "Running Processes"))
        self.btn_kill.setText(_translate("Dialog_process", "Kill"))
        self.btn_show.setText(_translate("Dialog_process", "Show"))
        self.btn_delete.setText(_translate("Dialog_process", "Clear"))
        self.btn_start.setText(_translate("Dialog_process", "Start"))

class Ui_dialog_start(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(374, 50)
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 353, 31))
        self.layoutWidget.setObjectName("layoutWidget")

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.label.setText("Enter Name:") 
        self.horizontalLayout_2.addWidget(self.label)

        self.lineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)

        self.btn_start = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_start.setObjectName("btn_start")
        self.horizontalLayout_2.addWidget(self.btn_start)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Start"))
        self.btn_start.setText(_translate("Dialog", "Start"))
        
class Ui_dialog_files(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(800, 500)
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 780, 480))
        self.layoutWidget.setObjectName("layoutWidget")
        
        self.mainLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setObjectName("mainLayout")

        self.topLayout = QtWidgets.QHBoxLayout()
        
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.topLayout.addWidget(self.label)
        
        self.pathEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.pathEdit.setObjectName("pathEdit")
        self.topLayout.addWidget(self.pathEdit)
        
        self.btn_browse = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_browse.setObjectName("btn_browse")
        self.topLayout.addWidget(self.btn_browse)
        
        self.mainLayout.addLayout(self.topLayout)

        # To displat folder structure
        self.treeWidget = QtWidgets.QTreeWidget(self.layoutWidget)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.setHeaderLabels(["Name", "Size", "Type", "Modified"])
        self.treeWidget.setAlternatingRowColors(True)
        self.mainLayout.addWidget(self.treeWidget)

        # Buttons
        self.buttonLayout = QtWidgets.QHBoxLayout()
        
        self.btn_refresh = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_refresh.setObjectName("btn_refresh")
        self.buttonLayout.addWidget(self.btn_refresh)
        
        self.btn_download = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_download.setObjectName("btn_download")
        self.buttonLayout.addWidget(self.btn_download)
        
        self.btn_delete = QtWidgets.QPushButton(self.layoutWidget)
        self.btn_delete.setObjectName("btn_delete")
        self.buttonLayout.addWidget(self.btn_delete)
        
        self.mainLayout.addLayout(self.buttonLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "File Manager"))
        self.label.setText(_translate("Dialog", "Path:"))
        self.btn_browse.setText(_translate("Dialog", "Browse"))
        self.btn_refresh.setText(_translate("Dialog", "Refresh"))
        self.btn_download.setText(_translate("Dialog", "Copy"))
        self.btn_delete.setText(_translate("Dialog", "Delete"))