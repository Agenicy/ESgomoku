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
    judge_array = []
    judge_weight = []
    judge_score = []

    # 可以平移的圖形
    pattern_shift = [
         # white(self)          black(enemy)
        [[0,0,0,-1, 1 ,1,1,1,-1],[0,0,0,-1, 0 ,0,0,0,-1]], # 活四
        [[0,0,-1,-1, 1 ,1,1,-1,-1],[0,0,0,-1, 0 ,0,0,-1,0]], # 活三
        #[[0,0,-1,-1, 1 ,1,1,-1,-1],[0,0,1,-1, 0 ,0,0,-1,1]], # 假活三(被夏止防守)
        [[0,0,-1,-1, 1 ,1,-1,-1,0],[0,0,-1,-1, 0 ,0,-1,-1,0]] # 活二
        ]
    # 圖形，包含移動前共有幾個
    pattern_kind = [4,3,2]
    # 滿足圖形所需的激活分數
    pattern_esti = [4,3,2]
    # 圖形的分數
    pattern_score = [100,50,10]
    # 無法只靠平移檢測的圖形
    pattern_mirror = [
        [[0,0,0,-1, 1 ,1,1,-1,1],[0,0,0,0, 0 ,0,0,-1,0]], # 跳四(長邊)
        [[0,0,0,-1, 1 ,-1,1,1,1],[0,0,0,0, 0 ,-1,0,0,0]], # 跳四(短邊)
        [[0,0,0,-1, 1 ,1,1,1,-1],[0,0,0,-1, 0 ,0,0,0,1]], # 死四
        [[0,0,-1,-1, 1 ,1,-1,1,-1],[0,0,0,-1, 0 ,0,-1,0,-1]], # 跳三(長邊)
        [[0,0,-1,-1, 1 ,-1,1,1,-1],[0,0,0,-1, 0 ,-1,0,0,-1]], # 跳三(短邊)
        [[0,0,-1,-1, 1 ,1,-1,1,-1],[0,0,0,1, 0 ,0,-1,0,-1]], # 跳三(長邊死, 長邊)
        [[0,0,-1,-1, 1 ,1,-1,1,-1],[0,0,0,-1, 0 ,0,-1,0,1]], # 跳三(短邊死, 長邊)
        [[0,0,-1,-1, 1 ,-1,1,1,-1],[0,0,0,-1, 0 ,-1,0,0,1]], # 跳三(長邊死, 短邊)
        [[0,0,-1,-1, 1 ,-1,1,1,-1],[0,0,0,1, 0 ,-1,0,0,-1]], # 跳三(短邊死, 短邊)
        [[0,0,-1,-1, 1 ,1,1,-1,0],[0,0,0,-1, 0 ,0,0,1,0]], # 死三
        [[0,0,0,-1, 1 ,-1,1,-1,0],[0,0,0,-1, 0 ,-1,0,-1,0]], # 跳二
        [[0,0,-1,-1, 1 ,1,-1,-1,0],[0,0,-1,-1, 0 ,0,-1,1,0]] # 比較弱的活二(單面開)
    ]
    # 對稱圖形，包含移動前共有幾個
    pattern_mirror_total_appear_times = [3,1,4 ,2,1, 2,2,1,1, 3, 1,2]
    # 對稱圖形的分數
    pattern_mirror_score = [60,60,30, 50,50, 45,45,45,45, 20, 5,5]
    # 滿足對稱圖形所需的激活分數
    pattern_mirror_esti = [4,4,5, 3,3, 4,4,4,4, 4, 2,3]

    # 每個圖形對應的名稱，用於debug
    pattern_name = ['活四','活三','活二',
    '跳四(長邊)','跳四(短邊)','死四',
    '跳三(長邊)','跳三(短邊)','跳三(長邊死, 長邊)','跳三(短邊死, 長邊)','跳三(長邊死, 短邊)','跳三(短邊死, 短邊)',
    '死三','跳二','弱活二']

    # 最終用於平坦化的矩陣(一開始輸入數量，等得知最終大小後才開始建造list)
    flattern = 0
    flag = 0

    def __init__(self):
        """generate judge_array and judge_weight by analyzing the lists named pattern and pattern_kind"""
        # 非對稱圖形
        for index, x in enumerate(self.pattern_kind):
            for i in range(0,x):
                # roll the list
                self.judge_array.append([ self.pattern_shift[index][0][i:] + self.pattern_shift[index][0][:i], self.pattern_shift[index][1][i:] + self.pattern_shift[index][1][:i]])
                # 圖形的分數
                self.judge_score.append(self.pattern_score[index])
                #圖形的激活分數
                self.judge_weight.append(1/self.pattern_esti[index])
                #註冊平坦化
                self.flattern += 1
        # 對稱圖形
        for index, x in enumerate(self.pattern_mirror_total_appear_times):
            for i in range(0,x):
                # reflect the list in "mirror"
                self.judge_array.append([self.pattern_mirror[index][0][i:] + self.pattern_mirror[index][0][:i], self.pattern_mirror[index][1][i:] + self.pattern_mirror[index][1][:i]])

                self.judge_score.append(self.pattern_mirror_score[index])
                #圖形的激活分數
                self.judge_weight.append(1/self.pattern_mirror_esti[index])
                #註冊平坦化
                self.flattern += 1

                # 反轉圖形
                lst1, lst2 = self.pattern_mirror[index][0][i:] + self.pattern_mirror[index][0][:i], self.pattern_mirror[index][1][i:] + self.pattern_mirror[index][1][:i]
                lst1.reverse()
                lst2.reverse()
                self.judge_array.append([lst1, lst2])
                # 圖形的分數
                self.judge_score.append(self.pattern_mirror_score[index])
                #圖形的激活分數
                self.judge_weight.append(1/self.pattern_mirror_esti[index])
                #註冊平坦化
                self.flattern += 1

        # 建立平坦化矩陣
        self.flattern = np.zeros((self.flattern,len(self.pattern_kind)+len(self.pattern_mirror_total_appear_times)))
        for index,times in enumerate(self.pattern_kind):
            
            for i in range(0,times):
                self.flattern[self.flag][index] = 1
                self.flag += 1
        
        for index,times in enumerate(self.pattern_mirror_total_appear_times):
            for i in range(0, times):
                # 因為有鏡射所以做兩次
                self.flattern[self.flag][len(self.pattern_kind) + index] = 1
                self.flag += 1
                self.flattern[self.flag][len(self.pattern_kind) + index] = 1
                self.flag += 1
        # list轉array
        self.judge_array = np.array(self.judge_array)
        # 加權函數轉成對角矩陣
        self.judge_weight = np.diag(np.array(self.judge_weight))

        print("Evaluate matrix done.")

    #unused
    def Eva_Range(self, location = (0, 0)):
        """Input a location, return a 5*5(or, at edge of the board, return 3*3) list.  """
        x_min, x_max = max(0, location[0] - 2 ), min(const.default_width, location[0] + 2 )
        y_min, y_max = max(0, location[1] - 2 ), min(const.default_height, location[1] + 2 )
        return Evaluater.board[x_min:x_max, y_min:y_max]

    #unused
    def has_neighbor(self, location = (0, 0)):
        """Return the location is isolated(5*5 no other chesses) or not."""
        for each_point in self.Eva_Range(location):
            if not each_point == 0:
                return True
        return False

    def test(self, board, loc):
        dir1,dir2,dir3,dir4 = [], [], [], []
        target = [dir1,dir2,dir3,dir4]
        total_pattern = []
        for x in range(-4,5):
            dir1.append([board[loc+x][0][loc+x], board[loc+x][1][loc+x]])
            dir2.append([board[loc-x][0][loc+x], board[loc-x][1][loc+x]])
            dir3.append([board[loc][0][loc+x], board[loc][1][loc+x]])
            dir4.append([board[loc+x][0][loc], board[loc+x][1][loc]])
        
        # 四個方向各算一次
        for i in range(0,4):
            target[i] = np.array(target[i])
            # 用矩陣判斷
            ret = np.matmul(self.judge_array, target[i])
            ret = ret.reshape(self.judge_array.shape[0], 2*len(target[i][0]))
            # 加總主對角線
            ret = np.dot(ret, np.array([1, 0, 0, 1]))
            # 運算是否存在pattern (1/2)
            ret = np.dot( self.judge_weight, ret)
            # 判斷種類，1 = 有此種類 (2/2)
            ret = np.maximum(np.floor(ret),0)
            # 平坦化
            ret = np.dot(ret, self.flattern)
            #print("flattern:{}".format(ret))

            if total_pattern == []:
                total_pattern = ret
            else:
                total_pattern += ret
        return total_pattern

# 測試輸入
if __name__ == '__main__':       
    judge = Judge()
    detect = judge.test([ 
                        [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
                        [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
                        [[0,0,0,0,0,0,0,0,0],[0,0,1,0,0,0,0,0,0]],
                        [[0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
                        [[0,0,0,0,1,0,1,1,0],[0,0,0,1,0,0,0,0,0]],
                        [[0,0,0,1,0,1,0,0,0],[0,0,0,0,0,0,0,0,0]],
                        [[0,0,1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
                        [[0,0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,0,0]],
                        [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]] , loc = 4)

    #print(judge.pattern_name)
    #print(detect)
    for i in range(0,len(judge.pattern_name)):
        if detect[i] == 1:
            print("{}:{}".format(judge.pattern_name[i],(int)(detect[i])))