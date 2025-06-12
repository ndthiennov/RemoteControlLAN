import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from main_ui import Ui_Server
from ps import RemoteControlServer

class Window(QMainWindow, Ui_Server):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.server = None
        self.server_thread = None
        self.pushButton.clicked.connect(self.toggle_server)

    def toggle_server(self):
        if not self.server:
            try:
                self.server = RemoteControlServer()
                self.server_thread = threading.Thread(target=self.server.main)
                self.server_thread.daemon = True
                self.server_thread.start()
                self.updateStatus(True)
                self.statusbar.showMessage("Server started successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start server: {str(e)}")
                self.updateStatus(False)
        else:
            try:
                self.server.cleanup()
                self.server = None
                self.updateStatus(False)
                self.statusbar.showMessage("Server stopped successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to stop server: {str(e)}")

    def closeEvent(self, event):
        """Handle application closing"""
        if self.server:
            try:
                self.server.cleanup()
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Error during cleanup: {str(e)}")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    win = Window()
    win.show()
    
    sys.exit(app.exec())