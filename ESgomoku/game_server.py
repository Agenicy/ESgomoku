import socketio
import eventlet
eventlet.monkey_patch()

import eventlet.wsgi
from flask import Flask
import threading, time
BlockingThread = True

from game_engine import *

from mcts_alphaZero import MCTSPlayer
from policy_value_net_keras import PolicyValueNet  # Keras

# 評估器
from evaluate_points import Judge, JudgeArray, Score, AIMemory

judge = Judge(13)
score = None

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

# 整盤棋的上一手
last_loc = []

# main game
game = None


def Reset():
    global t, judge, loc, game, chess_graph, chess_graph_width, now_pl, next_pl, BlockingThread, score
    print("game restart.")
    judge = None
    score = None
    
    if len(t) > 0:
        BlockingThread = False
    game.board.__init__()
    game.board.current_player = game.board.players[game.start_player]  # start player
    judge = Judge()
    loc = []
    chess_graph = [[],[]]
    now_pl, next_pl = 0, 1
    for i in range(0,chess_graph_width):
        chess_graph[0].append([0]*chess_graph_width)
        chess_graph[1].append([0]*chess_graph_width)

# 連接成功
@sio.on('connect')
def on_connect(sid, environ):   
    global t, judge, loc, BlockingThread
    print("connect ", sid)
    if len(t) == 0:
        print('new game.')
        t.append(threading.Thread(target=run))
        BlockingThread = True
        t[0].start()
    else:
        Reset()
        pass

# 斷開連結
@sio.on('disconnect')
def disconnect(sid):   
    global game, t
    print("disconnect ", sid)

@sio.on('restart')
def restart(sid, data):    
    Reset()

# 電腦落子
def send_step(location): 
    """傳遞location給unity
    
    Arguments:
        location {string}} -- 'x,y' 格式的字串
    """
    print(f'send step: {location}')   
    sio.emit(
        'ai_move', 
        data = {'loc':location}, 
        skip_sid=True) 
    eventlet.sleep(1)

# 冠軍出爐
def has_winner(winner): 
    print(winner)
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
        print ('pl_move : {}'.format(data['loc'])) # loc
        loc.append(data['loc'])
    else:
        print ('Recieved Empty Data!')

# 允許玩家落子
def call_player():
    sio.emit(
        'pl_turn', 
        data = {}, # location = AI move (format: '5,5')
        skip_sid=True) 
    eventlet.sleep(0)

# 等待並從佇列中讀取玩家落子
def wait_client():
    global loc
    while len(loc) == 0:
        call_player()
        eventlet.sleep(1)
    else:
        ret = loc.pop(0) # loc
        after_get_loc(ret)
        
        return ret

def after_get_loc(loc):
    """任一方回傳落子後，統整局勢變化並傳遞給unity
    
    Arguments:
        loc {list} -- 落子位置(loc-type)
    """
    
    # evaluate the point
    global chess_graph, now_pl, next_pl, last_loc
    step = loc.split(',')
    # 順便紀錄到 global 變數中
    last_loc = step = [ (int)(step[0]), (int)(step[1]) ]

    # 儲存棋盤
    detect = judge.Solve(board_init = [chess_graph[now_pl],chess_graph[next_pl]], loc = step)

    # 分析結果
    detect_enemy, detect_self = detect[0], detect[1]
    enemy_value = ''
    for i in range(0,len(JudgeArray.pattern_name)):
        enemy_value += (str)((int)(detect_enemy[i]))
        if detect_enemy[i] >= 1:
            print("阻擋了 {}:{}".format(JudgeArray.pattern_name[i],(int)(detect_enemy[i])))
    
    self_value = ''
    for i in range(0,len(JudgeArray.pattern_name)):
        self_value += (str)((int)(detect_self[i]))
        if detect_self[i] >= 1:
            print("達成了 {}:{}".format(JudgeArray.pattern_name[i],(int)(detect_self[i])))

    # 確定落子
    chess_graph[now_pl][step[0]][step[1]] = 1

    #* 登記分數
    global score
    if score is None:
        score = Score()
    else:
        score.Add(detect, playerNum = now_pl)
    whiteScore, blackScore = score.Get(selfIsBlack = True)

    # 回傳結果
    sio.emit(
        'judge', 
        data = {'self_value':self_value,
                'enemy_value':enemy_value,
                'blackScore':(str)(blackScore),
                'whiteScore':(str)(whiteScore)
                }, 
        skip_sid=True) 
    eventlet.sleep(1)

    # 交換先後手
    now_pl, next_pl = next_pl, now_pl


class Client(object):
    """
    human player, at Client
    """

    def __init__(self):
        self.player = None
        self.tag = 'Client'

    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board):
        print("player's turn")
        try:
            location = wait_client()

            if isinstance(location, str):  # for python3
                location = [int(n, 10) for n in location.split(",")]
            move = board.location_to_move(location)

        except Exception as e:
            print(e)
            move = -1
        if move == -1 or move not in board.availables:
            print(f"invalid move: {move}")
            move = self.get_action(board)
        return move

    def __str__(self):
        return "Human {}".format(self.player)
'''
class AI_ABTree(object):
    """
    human player, at Client
    """
    memory = AIMemory()
    
    def __init__(self):
        self.player = None

    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board):
        print("AI's turn")
        try:
            global chess_graph, now_pl, next_pl, last_loc, score
            #* 預測最佳落點
            location = judge.AI_Solve(board = [chess_graph[next_pl],chess_graph[now_pl]], last_loc = last_loc ,
                                score = score, judge = judge, alphaIsBlack = False)
            
            print(f"get loc: {location}")
            
            # loc(list) to location(string)
            location = f'{location[0]},{location[1]}'
            
            # 紀錄並計算
            after_get_loc(location)
            print('ab-tree solved.')
            
            # 傳給 unity
            send_step(location)
            
            if isinstance(location, str):  # for python3
                location = [int(n, 10) for n in location.split(",")]
            move = board.location_to_move(location)

        except Exception as e:
            print(e)
            move = -1
        if move == -1 or move not in board.availables:
            print(f"invalid move: {move}")
            move = self.get_action(board)
        return move

    def __str__(self):
        return "Human {}".format(self.player)
'''
def run():
    n = 5
    width, height = 13, 13
    model_file = './current_model_13_13_5.h5'
    try:
        global winner, game, BlockingThread
        board = Board(width=width, height=height, n_in_row=n)
        game = Game(board)

        # USE ML
        best_policy = PolicyValueNet(width, height, model_file = model_file)
        mcts_player = MCTSPlayer(best_policy.policy_value_fn, c_puct=5, n_playout=400)
        ###
        
        while True:
            BlockingThread = True # blocking
            print("new game starts")
            # set start_player=0 for human first
            winner = game.start_play(Client(), mcts_player, start_player=0, is_shown=1, send_step = send_step)
            has_winner(winner)
            eventlet.sleep(1)
            print("game end")
            while BlockingThread: # blocking
                eventlet.sleep(2)

    except KeyboardInterrupt:
        print('\n\rquit')

if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
