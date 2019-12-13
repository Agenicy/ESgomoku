"""UNITY和python溝通的管道"""
"""
import socket

HOST = '127.0.0.1'#設定要綁定的地址
PORT = 4567# SocketIO plugin in Unity

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#創建socket
s.bind((HOST, PORT))#綁定
s.listen(5)#監聽

#進入無窮迴圈等代客戶端連線
while True:
    conn, addr = s.accept()
    print('Connected by {}'.format(addr))
    #連線成功後，不斷接收並印出資料，並回傳收到
    while True:
        data = conn.recv(1024)
        print(data)

        conn.send("server received you message.")

# conn.close()
"""
import socketio
import eventlet
import eventlet.wsgi
from flask import Flask
app = Flask(__name__)
sio = socketio.Server()

# "连接建立的回调函数"
@sio.on('connect')
def on_connect(sid, environ):    
    print("connect ", sid)
    send_to_client(101)

# "接收 Client 事件 (client_sent) 的回调函数"
@sio.on('client_sent')
def on_revieve(sid, data):    
    if data:
        print ('From Client : %s' % data['nbr'])
        send_to_client(int(data['nbr']) + 1)
    else:
        print ('Recieved Empty Data!')

# "向 Client 发送数字"
def send_to_client(_nbr):    
    sio.emit(
        'server_sent', 
        data = {'nbr':_nbr.__str__()}, 
        skip_sid=True)        

if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)