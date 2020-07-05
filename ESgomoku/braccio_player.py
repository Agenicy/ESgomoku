import sys
sys.path.extend(['./serial', './Braccio'])
from usb import usb
from solver import solver
from time import sleep
from math import sqrt, atan, pi
import numpy as np

# 常數修正項 ------------------------------------------------------
testMode = False
port = 'COM4'
x_offset = 150 # 棋盤中點左右偏差值 (絕對值)
y_offset = 0 # 棋盤高度偏差值 (向上為正)
block_length = 23.7 # 棋盤格子長度
block_width = 23

# 以下 板子正中央為 90 deg
waiting_action_pre = [30, 0, 64, 178, 179, 0, 20] # 落子後的待機位置
waiting_action = [30, 0, 64, 178, 179, 0, 38] # 落子後的待機位置

y_150 = 100 # 150.0時相對於基準面的高度
y_400 = 145 # 400.0時相對於基準面的高度
y_board = -93 + 25 # 落子的高度
y_board_chess = -40 # 夾棋子的高度

def y_function(x, y):
    return y - (x - (-150)) * (y_400 - y_150) / ((-400) - (-150)) # Δy - Δx * 修正函數(實驗求得)

def MakeData(x, y,ang = 90,catch=0,time=20):
    """將距離xy轉換為指令"""
    y = y_function(x, y)
    t, o, p = s.Calc(x, y)
    if t != 0:
        return [time, ang, t, o, p, 180 - (180 * catch), 38]
    else:
        return False

def LocToRec(loc = list):
    """
    ### 將座標點轉換為機械手臂指令
    
    初始輸入 [y, x]:
    3*3 board's moves like:
        6 7 8
        3 4 5
        0 1 2
    and move 5's location is (1,2)
    
    (手臂的左上方[y, x]為[0, 8] 右上方為[0, 0]，向手臂為y pos)
    
    x轉為: 手臂左右位移
    y轉為: 手臂前後位移
    """
    x, y = loc[1], 8-loc[0] # x, y swap
    x = x - 4 # 以手臂左方為正, 中央為 0
    x , y = int(x * block_width), int(y * block_length) # 轉換為mm
    y = x_offset + y # 轉換為 (板子)前後偏移量 + loc y 位移 
    
    r = sqrt(pow(x,2)+pow(y,2)) # 平面半徑
    if x == 0:
        # 正中央
        ang = 90
    else:
        ang = atan(y/x)*180/pi
        if ang < 0:
            ang += 180
    
    return r, ang # 弳度轉弧度
    
# -----------------------------------------------------------------
s = solver()
u = usb()
u.AddClient(port, 9600, show = False, testMode = testMode)
u.Run()
u.UserSend(data = waiting_action_pre, port = port)
u.Wait(port=port)
a = input('install the claw and press enter:')
u.UserSend(data = waiting_action, port = port)
u.Wait(port=port)

def catch():
    # 夾棋子 --------------------------------------------------------------------
    # move
    """
    prepare = MakeData(x = -150, y= y_board_chess ,ang = 0, catch = 1)
    u.UserSend(data = prepare, port = port)
    u.Wait(port=port)
    sleep(1)
    # catch
    prepare[0], prepare[5] = 10, 68
    u.UserSend(data = prepare, port = port)
    u.Wait(port=port)"""
    # take up
    # prepare[0], prepare[3]= 10, 145
    # u.UserSend(data = prepare, port = port)
    # u.Wait(port=port)
    # ready
    u.UserSend(data = MakeData(x = -150, y= 0 ,ang = 90, catch = 1), port = port)
    u.Wait(port=port)
    # --------------------------------------------------------------------------

from mcts_alphaZero import MCTS, TreeNode, softmax
class BraccioPlayer(object):
    """AI player based on MCTS, act wuth braccio"""

    def __init__(self, policy_value_function,
                 c_puct=5, n_playout=2000, is_selfplay=0):
        self.mcts = MCTS(policy_value_function, c_puct, n_playout)
        self._is_selfplay = is_selfplay
        self.tag = 'AI'

    def set_player_ind(self, p):
        self.player = p

    def reset_player(self):
        self.mcts.update_with_move(-1)

    def get_action(self, board, temp=1e-2, return_prob=0):
        sensible_moves = board.availables
        # the pi vector returned by MCTS as in the alphaGo Zero paper
        move_probs = np.zeros(board.width*board.height)
        if len(sensible_moves) > 0:
            acts, probs = self.mcts.get_move_probs(board, temp)
            move_probs[list(acts)] = probs
            if self._is_selfplay:
                # add Dirichlet Noise for exploration (needed for
                # self-play training)
                move = np.random.choice(
                    acts,
                    p=0.75*probs + 0.25*np.random.dirichlet(0.3*np.ones(len(probs)))
                )
                # update the root node and reuse the search tree
                self.mcts.update_with_move(move)
            else:
                # with the default temp=1e-3, it is almost equivalent
                # to choosing the move with the highest prob
                move = np.random.choice(acts, p=probs)
                # reset the root node
                self.mcts.update_with_move(-1)
#                location = board.move_to_location(move)
#                print("AI move: %d,%d\n" % (location[0], location[1]))

            def move_to_location(move):
                """
                3*3 board's moves like:
                6 7 8
                3 4 5
                0 1 2
                and move 5's location is (1,2)
                """
                h = move // 9
                w = move % 9
                return [h, w]
            
            print('braccio move: {}'.format(move_to_location(move)))
            
            self.Action(move_to_location(move))
            u.Wait(port=port)

            if return_prob:
                return move, move_probs
            else:
                return move
        else:
            print("WARNING: the board is full")

    def __str__(self):
        return "MCTS {}".format(self.player)

    def Action(self, loc = list):
        """落子"""
        catch()
        
        r, ang = LocToRec(loc)
        
        serial = MakeData(x = -r, y= y_board ,ang = ang, catch = 1)
        serial2 = MakeData(x = -r, y= y_board ,ang = ang, catch = 0, time = 10)
        end_action = MakeData(x = -r, y= 0 ,ang = ang, catch = 0)
        
        if serial != False:
            u.UserSend(data = serial, port = port)
            u.Wait(port=port)
            u.UserSend(data = serial2, port = port)
            u.Wait(port=port)
            u.UserSend(data = end_action, port = port)
            u.Wait(port=port)
        u.UserSend(data = waiting_action, port = port)
    

if __name__ == '__main__':
    b = BraccioPlayer(None)
    while True:
        try:
            word = input(f'Enter Data (y, x), use dot(".") to seprate...').replace('\n','').split('.')
            loc = [int(word[0]), int(word[1])]
            if loc[0] == -1:
                u.UserSend(data = waiting_action_pre, port = port)
            else:
                b.Action(loc)
        except Exception as e:
            u.UserSend(data = waiting_action_pre, port = port)
            u.Wait(port=port)
            print(e)
            
    