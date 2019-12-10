import numpy as np
"""
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D
"""

from game_engine import const

class Evaluater(object):
    """Evaluate each point of the Board"""
    # Board with black = 1 , white = -1
    board = []
    def __init__(self, board):
        self.board = board

class Judge(object):
    #judge_array dot plate = whether there is a shape or not
    judge_array = np.array([
         # white(self)          black(enemy)
        [[0,0,0,-1, 1 ,1,1,1,-1],[0,0,0,-1, 0 ,0,0,0,-1]], #活四
        [[0,0,-1,1, 1 ,1,1,-1,0],[0,0,-1,0, 0 ,0,0,-1,0]], #活四
        [[0,-1,1,1, 1 ,1,-1,0,0],[0,-1,0,0, 0 ,0,-1,0,0]], #活四
        [[-1,1,1,1, 1 ,-1,0,0,0],[-1,0,0,0, 0 ,-1,0,0,0]], #活四
        [[0,0,0,-1, 1 ,1,1,-1,0],[0,0,0,-1, 0 ,0,0,-1,0]], #活三
        [[0,0,-1,1, 1 ,1,-1,0,0],[0,0,-1,0, 0 ,0,-1,0,0]], #活三
        [[0,-1,1,1, 1 ,-1,0,0,0],[0,-1,0,0, 0 ,-1,0,0,0]], #活三
        [[0,0,0,0, 0 ,0,0,0,0],  [0,0,0,0, 0 ,0,0,0,0]], #補零
        ])

    def Eva_Range(self, location = (0, 0)):
        """Input a location, return a 5*5(or, at edge of the board, return 3*3) list.  """
        x_min, x_max = max(0, location[0] - 2 ), min(const.default_width, location[0] + 2 )
        y_min, y_max = max(0, location[1] - 2 ), min(const.default_height, location[1] + 2 )
        return Evaluater.board[x_min:x_max, y_min:y_max]

    def has_neighbor(self, location = (0, 0)):
        """Return the location is isolated(5*5 no other chesses) or not."""
        for each_point in self.Eva_Range(location):
            if not each_point == 0:
                return True
        return False

    def test(self, board, loc):
        target = []
        for x in range(-4,5):
            target.append([board[loc+x][0][loc+x], board[loc+x][1][loc+x]])
        ret = np.matmul(self.judge_array, target).reshape(self.judge_array.shape[0], 4)  # 用矩陣判斷
        ret = np.dot(ret, np.array([1, 0, 0, 1]).T) #加總主對角線
        ret = ret.reshape((int)(self.judge_array.shape[0]/4), 4) # 將不同種類的判斷式分開
        ret = np.dot( ret, np.array([[1,1,1,1],[1,1,1,1]]).T) # 運算
        ret = np.floor(ret) # 判斷種類，1 = 有此種類
        return ret
            
judge = Judge()
print(judge.test([ [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
                   [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
                   [[0,0,1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
                   [[0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
                   [[0,0,0,0,1,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
                   [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
                   [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
                   [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
                   [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]] , loc = 4))