import socketio
import eventlet
eventlet.monkey_patch()

import eventlet.wsgi
from flask import Flask
import threading, time

from game_engine import *

# 單步評估器
from evaluate_points import Judge
judge = Judge()
chess_graph = [[],[]]
chess_graph_width = 13
for i in range(0,chess_graph_width):
    chess_graph[0].append([0]*chess_graph_width)
    chess_graph[1].append([0]*chess_graph_width)

now_pl, next_pl = 0, 1

# server
sio = socketio.Server()
app = Flask(__name__)

# thread
t = []

# client input queue
loc = []

# main game
game = None

# 連接成功
@sio.on('connect')
def on_connect(sid, environ):   
    global t 
    print("connect ", sid)
    if len(t) == 0:
        t.append(threading.Thread(target=run))
        t[0].start()
    else:
        print("OH")

# 斷開連結
@sio.on('disconnect')
def disconnect(sid):   
    global game, t
    print("disconnect ", sid)
    if game is not None:
        print(t[0]._stop)
        game.Stop()

# 電腦落子
def send_step(): 
    print('send_step')   
    sio.emit(
        'ai_move', 
        data = {'loc':"3,5"}, 
        skip_sid=True) 
    eventlet.sleep(0)

# 冠軍出爐
def has_winner(winner): 
    print('has winner!')
    sio.emit(
        'winner', 
        data = {'winner':"winner is :{}".format(winner)}, 
        skip_sid=True) 
    eventlet.sleep(0)

# 玩家落子
@sio.on('pl_move')
def pl_move(sid, data):    
    if data:
        global loc
        print ('pl_move : %s' % data['loc'])
        loc.append(data['loc'])
    else:
        print ('Recieved Empty Data!')

# 允許玩家落子
def call_player():
    sio.emit(
        'pl_turn', 
        data = {}, 
        skip_sid=True) 
    eventlet.sleep(0)

# 等待並從佇列中讀取玩家落子
def wait_client():
    global loc
    call_player()
    while len(loc) == 0:
        eventlet.sleep(1)
        print("Mom, I'm here!")
        if game.isNotRunning():
            raise KeyboardInterrupt
    else:
        ret = loc.pop(0)
        
        # evaluate the point
        global chess_graph, now_pl, next_pl
        step = ret.split(',')

        # 儲存棋盤 並 印出結果
        detect = judge.Solve([chess_graph[now_pl],chess_graph[next_pl]], [(int)(step[1])+1 , (int)(step[0])+1])
        value = ''
        for i in range(0,len(judge.pattern_name)):
            value += (str)((int)(detect[i]))
            if detect[i] >= 1:
                print("{}:{}".format(judge.pattern_name[i],(int)(detect[i])))

        """for i in range(0,13):
            print(f"{chess_graph[0][i]}   {chess_graph[1][i]}")"""

        sio.emit(
            'judge', 
            data = {'value':value}, 
            skip_sid=True) 
        eventlet.sleep(0)

        # 交換先後手
        now_pl, next_pl = next_pl, now_pl

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
        global winner, game
        board = Board(width=width, height=height, n_in_row=n)
        game = Game(board)

        # set start_player=0 for human first
        winner = game.start_play(Client(), Client(), start_player=0, is_shown=0)
        has_winner(winner)
        raise KeyboardInterrupt
        
    except KeyboardInterrupt:
        print('\n\rquit')

if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
    
