from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

class Ui_Server(object):
    def setupUi(self, Server):
        # Set fixed window size and properties
        Server.setObjectName("Server")
        Server.resize(300, 150)
        Server.setMinimumSize(300, 150)
        Server.setMaximumSize(300, 150)
        Server.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        # Create and setup central widget
        self.centralwidget = QtWidgets.QWidget(Server)
        self.centralwidget.setObjectName("centralwidget")

        # Create main layout
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(10)

        # Create and setup status label
        self.statusLabel = QtWidgets.QLabel(self.centralwidget)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setObjectName("statusLabel")
        self.mainLayout.addWidget(self.statusLabel)

        # Create and setup start/stop button
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setMinimumHeight(40)
        self.pushButton.setObjectName("pushButton")
        self.mainLayout.addWidget(self.pushButton)

        # Set central widget
        Server.setCentralWidget(self.centralwidget)

        # Create and setup menubar
        self.menubar = QtWidgets.QMenuBar(Server)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 300, 22))
        self.menubar.setObjectName("menubar")
        Server.setMenuBar(self.menubar)

        # Create and setup statusbar
        self.statusbar = QtWidgets.QStatusBar(Server)
        self.statusbar.setObjectName("statusbar")
        Server.setStatusBar(self.statusbar)

        # Setup stylesheet
        self.setupStyle()
        
        # Initialize UI text
        self.retranslateUi(Server)
        QtCore.QMetaObject.connectSlotsByName(Server)

    def setupStyle(self):
        """Setup the stylesheet for the UI components"""
        style = """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1984D8;
            }
            QPushButton:pressed {
                background-color: #006CC1;
            }
            QLabel {
                color: #333333;
                font-size: 12px;
            }
            QStatusBar {
                background-color: #f0f0f0;
                color: #666666;
            }
        """
        self.centralwidget.setStyleSheet(style)

    def retranslateUi(self, Server):
        """Set up all the text for the UI"""
        _translate = QtCore.QCoreApplication.translate
        Server.setWindowTitle(_translate("Server", "Remote Control Server"))
        self.pushButton.setText(_translate("Server", "Start Server"))
        self.statusLabel.setText(_translate("Server", "Server Status: Stopped"))

    def updateStatus(self, running: bool):
        """Update the UI to reflect the server status"""
        if running:
            self.statusLabel.setText("Server Status: Running")
            self.pushButton.setText("Stop Server")
            self.pushButton.setStyleSheet("""
                background-color: #C42B1C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            """)
        else:
            self.statusLabel.setText("Server Status: Stopped")
            self.pushButton.setText("Start Server")
            self.pushButton.setStyleSheet("""
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            """)