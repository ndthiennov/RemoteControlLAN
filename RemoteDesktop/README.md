# REMOTE CONTROL OVER A COMPUTER WITH SOCKET
## Điều khiển máy tính từ xa sử dụng Socket.

## Features
 - Xem, start, kill các process đang chạy
 - Xem, start, kill các app đang chạy
 - Keystroke
 - Chụp màn hình
 - Xem, copy, xoá files
 - Tắt máy
 ## Prerequisites
 - Cài đặt Python3, pip
 - Cài đặt các thư viện PyQT, PynNut, WinReg... có trong `Requirement.txt`
 - Máy bị điều khiển chỉ hỗ trợ hệ điều hành Windows. Máy điều khiển và máy bị điều khiển trong cùng một mạng LAN
- Gọi máy bị điều khiển là Server. Máy điều khiển là Client.

## Guideline
Cài đặt các requirements

    pip install -r requirements.txt
Đặt folder Server trên máy bị điều khiển. Chạy file `main.py`

    cd path/to/Server
    python3 main.py

Đặt folder Client trên máy điều khiển. Chạy file `main.py`

    cd path/to/Client
    python3 main.py

Nhập địa chỉ IP của máy bị điều khiển để kết nối. Port mặc định Server mở là `8080`. 
