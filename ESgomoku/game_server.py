import socketio
import eventlet
eventlet.monkey_patch()
import eventlet.wsgi
from flask import Flask
import threading, time

from game_engine import *


sio = socketio.Server()
app = Flask(__name__)

# thread
t = []

# client input queue
loc = []

"""
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
        time.sleep(3)
        send_to_client(int(data['nbr']) + 1)
    else:
        print ('Recieved Empty Data!')
# "向 Client 发送数字"
def send_to_client(_nbr):    
    sio.emit(
        'server_sent', 
        data = {'nbr':_nbr.__str__()}, 
        skip_sid=True)      
"""
@sio.on('connect')
def on_connect(sid, environ):   
    global t 
    print("connect ", sid)
    send_step()
    if len(t) == 0:
        t.append(threading.Thread(target=run))
        t[0].start()
    
def send_step(): 
    print('send_step')   
    sio.emit(
        'ai_move', 
        data = {'loc':"3,5"}, 
        skip_sid=True) 
    eventlet.sleep(0)

def has_winner(winner): 
    print('has winner!')
    sio.emit(
        'winner', 
        data = {'winner':"winner is :{}".format(winner)}, 
        skip_sid=True) 
    eventlet.sleep(0)

@sio.on('pl_move')
def pl_move(sid, data):    
    if data:
        global loc
        print ('pl_move : %s' % data['loc'])
        loc.append(data['loc'])
    else:
        print ('Recieved Empty Data!')


def wait_client():
    global loc
    while len(loc) == 0: 
        eventlet.sleep(1)
    else:
        send_step()
        ret = loc.pop(0)
        print(ret)
        return ret

class Client(object):
    """
    human player, at Client
    """

    def __init__(self):
        self.player = None

    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board):
        try:
            global loc, t
            location = wait_client()
            print(location)

            if isinstance(location, str):  # for python3
                location = [int(n, 10) for n in location.split(",")]
            move = board.location_to_move(location)

        except Exception as e:
            print(e)
            move = -1
        if move == -1 or move not in board.availables:
            print("invalid move")
            move = self.get_action(board)
        return move

    def __str__(self):
        return "Human {}".format(self.player)

def run():
    n = 5
    width, height = 13,13
    try:
        global winner, t
        board = Board(width=width, height=height, n_in_row=n)
        game = Game(board)

        # set start_player=0 for human first
        winner = game.start_play(Client(), Client(), start_player=0, is_shown=1)
        has_winner(winner)

    except KeyboardInterrupt:
        print('\n\rquit')

if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
    
