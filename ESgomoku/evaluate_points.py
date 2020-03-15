import cupy as np
#import numpy as np
"""
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D
"""

from game_engine import const

# 加速器
#from numba import jit

from copy import deepcopy

class JudgeArray(object):
    
    #! 有許多list會在第一個judge出來後被建構
    
    # 定義需要防守的對方 pattern
    #? 對方活三可以用死四強推，或許可以拚到死四活三，因此不列入強制防守範圍
    #? 被玩家用跳四轉移焦點的可能性?
    defPattern = np.array([
        0, 0, 0, 0,         # '五連','活四','活三','活二',
        1, 1, 1, 1,         # '跳四(長邊)','跳四(短邊)','跳四(中間)','死四',
        # '跳三(長邊)','跳三(短邊)','跳三(長邊死, 長邊)','跳三(短邊死, 長邊)','跳三(長邊死, 短邊)','跳三(短邊死, 短邊)',
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0         # '死三','跳二','弱活二','死二'
    ])

    # 把活四拿掉了
    winDetect = np.array([
        1, 0.5, 0.5, 0,         # '五連','活四','活三','活二',
        0.5, 0.5, 0.5, 0.5,         # '跳四(長邊)','跳四(短邊)','跳四(中間)','死四',
        # '跳三(長邊)','跳三(短邊)','跳三(長邊死, 長邊)','跳三(短邊死, 長邊)','跳三(長邊死, 短邊)','跳三(短邊死, 短邊)',
        0.5, 0.5, 0, 0, 0, 0,
        0, 0, 0, 0         # '死三','跳二','弱活二','死二'
    ])
    
    # 用 matmul 將現在的 pattern 轉換成過去的 pattern
    futurePattern = np.array([
        # will be 5
        [0, 1, 0, 0,
         1, 1, 1, 1,
         0, 0, 0, 0, 0, 0,
         0, 0, 0, 0],
        # will be 4
        [0, 0, 1, 0,
         0, 0, 0, 0,
         1, 1, 1, 1, 1, 1,
         1, 0, 0, 0],
        # will be 3
        [0, 0, 0, 1,
         0, 0, 0, 0,
         0, 0, 0, 0, 0, 0,
         0, 1, 1, 1]]).T
    
    nowPattern = np.array([
        # is 5
        [1, 0, 0, 0,
         0, 0, 0, 0,
         0, 0, 0, 0, 0, 0,
         0, 0, 0, 0],
        # is 4
        [0, 1, 0, 0,
         1, 1, 1, 1,
         0, 0, 0, 0, 0, 0,
         0, 0, 0, 0],
        # is 3
        [0, 0, 1, 0,
         0, 0, 0, 0,
         1, 1, 1, 1, 1, 1,
         1, 0, 0, 0],
        # is 2
        [0, 0, 0, 1,
         0, 0, 0, 0,
         0, 0, 0, 0, 0, 0,
         0, 1, 1, 1]]).T
        
    pastPattern = np.array([
        # was 4
        [1, 0, 0, 0,
         0, 0, 0, 0,
         0, 0, 0, 0, 0, 0,
         0, 0, 0, 0],
        # was 3
        [0, 1, 0, 0,
         1, 1, 1, 1,
         0, 0, 0, 0, 0, 0,
         0, 0, 0, 0],
        # was 2
        [0, 0, 1, 0,
         0, 0, 0, 0,
         1, 1, 1, 1, 1, 1,
         1, 0, 0, 0],
        # was 1
        [0, 0, 0, 1,
         0, 0, 0, 0,
         0, 0, 0, 0, 0, 0,
         0, 1, 1, 1]]).T

class Score(object):
    """用來記錄盤勢，存在於每個NODE與global中
    player: 0 = enemy, 1 = self
    """
    
    #計算上限 (必須是 unity 端 Max 的一半)
    limit = 10000
    
    def __init__(self, copyFrom = None):
        '''set pattern to zero array'''
        if copyFrom is None:
            self.blackScore = 600
            self.whiteScore = 500
        else:
            # 複製一份現存的 Score 物件
            self.blackScore = deepcopy(copyFrom.blackScore)
            self.whiteScore = deepcopy(copyFrom.whiteScore)
    
    def Get(self, selfIsBlack = True): 
        """回傳敵我分數"""
        if selfIsBlack:
            return self.whiteScore, self.blackScore
        else:     
            return self.blackScore, self.whiteScore
    
    def GetScore(self, selfIsBlack = True):
        """回傳計算後 self 的盤勢分數"""
        if selfIsBlack:
            return (float)(self.blackScore / (self.blackScore + self.whiteScore))
        else:
            return (float)(self.whiteScore / (self.blackScore + self.whiteScore))
        
    def Add(self, patternList, playerNum = -1, selfIsBlack = None):
        #*print
        # print('Score add, score = {}/{}'.format(self.blackScore,self.whiteScore))
        """傳入pattern = [enemypat, selfPat]，紀錄到Score裡面
        
        Arguments:
            pattern {list} -- [阻擋敵方 pattern, 自己達成 pattern]
        
        Keyword Arguments:
            playerNum {int} -- 用於 server，0 代表當前玩家執黑 (default: {-1})
            selfIsBlack {bool} -- True代表當前玩家執黑 (default: {None})
        """
        #! pattern = [enemy, self]
        #! playerNum : black = 0, white = 1
        # 傳入 playerNum 或 selfIsBlack
        pattern = np.array(patternList, dtype=np.float32)
        
        
        # 決定自己的分數要放在 black 或 white
        if playerNum == 0 or selfIsBlack:
            # 如果一次連成大量 pattern 會有額外 combe 分數 ( 自己 * np.sum(pattern[1]) )
            self.blackScore += np.dot(pattern[1],  np.array(JudgeArray.judge_score, dtype=np.float32)) * np.sum(pattern[1])
            self.whiteScore -= np.dot(np.matmul(pattern[0], np.array(JudgeArray.pastPattern, dtype=np.float32)), np.array(JudgeArray.block_score, dtype=np.float32))
            # print(f'b + {np.dot(pattern[1], JudgeArray.judge_score)}, w - {np.dot(np.matmul(pattern[0], JudgeArray.pastPattern), JudgeArray.block_score)}')
        else:
            self.blackScore -= np.dot(np.matmul(pattern[0], np.array(JudgeArray.pastPattern, dtype=np.float32)), np.array(JudgeArray.block_score, dtype=np.float32))
            self.whiteScore += np.dot(pattern[1], np.array(JudgeArray.judge_score, dtype=np.float32)) * np.sum(pattern[1])
            # print(f'b - {np.dot(np.matmul(pattern[0], JudgeArray.pastPattern), JudgeArray.block_score)}, w + {np.dot(pattern[1], JudgeArray.judge_score)}')
        
        # 上限
        if self.blackScore > self.limit or self.whiteScore > self.limit:
            self.blackScore = 2 * self.limit * self.blackScore / (self.blackScore + self.whiteScore)
            self.whiteScore = 2 * self.limit - self.blackScore

class AIMemory(object):
    """AI會記得他自己與對手進攻的位置，避免被玩家誤導
    
        selfLastLoc(list) -- 上次自己的進攻位置，使用類LSTM法判斷何時須忘記
        enemyLastLoc(list) -- 敵人的上一步，每次更新
    """
    selfLastLoc = []
    enemyLastLoc = []

class Judge(object):
    """評估器
    player: 0 = enemy, 1 =  self"""
    
    # 兩格內有棋子的點
    solvePoint = []
    solveRange = []

    def ResetJudgeArray(self):
        """generate judge_array and judge_weight by analyzing the lists named pattern and pattern_kind"""

        # judge_array dot plate = whether there is a shape or not
        JudgeArray.judge_array = []
        JudgeArray.judge_weight = []
        JudgeArray.judge_score = []

        # 最終用於平坦化的矩陣(一開始輸入數量，等得知最終大小後才開始建造list)
        JudgeArray.flattern = 0

        # 可以平移的圖形
        JudgeArray.pattern_shift = [
            # white(self)          black(enemy)
            [[0, 0, 0, 0, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0]],  # 五
            [[0, 0, 0, -1, 1, 1, 1, 1, -1], [0, 0, 0, -1, 0, 0, 0, 0, -1]],  # 活四
            [[0, 0, -1, -1, 1, 1, 1, -1, -1], [0, 0, 0, -1, 0, 0, 0, -1, 0]],  # 活三
            # [[0, 0, -1, -1, 1 ,1, 1, -1, -1], [0, 0, 1, -1, 0 , 0, 0, -1, 1]], # 假活三(被夏止防守)
            [[0, 0, -1, -1, 1, 1, -1, -1, 0], [0, 0, -1, -1, 0, 0, -1, -1, 0]]  # 活二
        ]
        # 圖形，包含移動前共有幾個
        JudgeArray.pattern_kind = [5, 4, 3, 2]
        # 滿足圖形所需的激活分數
        JudgeArray.pattern_esti = [5, 4, 3, 2]
        # 圖形的分數
        #> 形成 5 = 10000, 4 = 600, 3 = 400, 2 = 100
        #> 阻擋 5 = 10000, 4 = 500, 3 = 300, 2 = 80
        # 組成 5/ 4/ 3/ 2
        JudgeArray.pattern_score = [1000000, 80000, 400, 40]
        
        #* 對稱圖形
        # 對稱圖形，包含移動前共有幾個
        JudgeArray.pattern_mirror_total_appear_times = [3, 1, 2, 4, 2, 1, 2, 2, 1, 1, 3, 1, 2, 2]
        # 對稱圖形的分數
        # 組成                             跳四(長邊), 跳四(短邊), 跳四(中間), 死四, 
        JudgeArray.pattern_mirror_score = [510, 510, 510, 550, 
                                           # 跳三(長邊), 跳三(短邊), 跳三(長邊死,長邊), 跳三(短邊死,長邊), 
                                           380, 380, 350, 350, 
                                           # 跳三(長邊死,短邊),跳三(短邊死,短邊),死三,
                                           350, 350, 350, 
                                           # 跳二,弱活二,死二
                                           30, 20, 10]
        
        # 滿足對稱圖形所需的激活分數
        JudgeArray.pattern_mirror_esti = [4, 4, 4, 5, 3, 3, 4, 4, 4, 4, 4, 2, 3, 3]
        
        
        # 無法只靠平移檢測的圖形
        JudgeArray.pattern_mirror = [
                [[0, 0, 0, -9, 1, 1, 1, -9, 1],[0, 0, 0, 0, 0, 0, 0, -9, 0]],  # 跳四(長邊)
                [[0, 0, 0, -9, 1, -9, 1, 1, 1],[0, 0, 0, 0, 0, -9, 0, 0, 0]],  # 跳四(短邊)
                [[0, 0, 0, -9, 1, 1, -9, 1, 1],[0, 0, 0, 0, 0, -9, 0, 0, 0]],  # 跳四(中間)
                [[0, 0, 0, -9, 1, 1, 1, 1, -9], [0, 0, 0, -9, 0, 0, 0, 0, 1]],  # 死四
                [[0, 0, -9, -9, 1, 1, -9, 1, -9],[0, 0, 0, -9, 0, 0, -9, 0, -9]],  # 跳三(長邊)
                [[0, 0, -9, -9, 1, -9, 1, 1, -9],[0, 0, 0, -9, 0, -9, 0, 0, -9]],  # 跳三(短邊)
                [[0, 0, -9, -9, 1, 1, -9, 1, -9],[0, 0, 0, 1, 0, 0, -9, 0, -9]],  # 跳三(長邊死, 長邊)
                [[0, 0, -9, -9, 1, 1, -9, 1, -9],[0, 0, 0, -9, 0, 0, -9, 0, 1]],  # 跳三(短邊死, 長邊)
                [[0, 0, -9, -9, 1, -9, 1, 1, -9], [0, 0, 0, -9, 0, -9, 0, 0, 1]],  # 跳三(長邊死, 短邊)
                [[0, 0, -9, -9, 1, -9, 1, 1, -9],[0, 0, 0, 1, 0, -9, 0, 0, -9]],  # 跳三(短邊死, 短邊)
                [[0, 0, -9, -9, 1, 1, 1, -9, 0], [0, 0, -9, -9, 0, 0, 0, 1, 0]],  # 死三
                [[0, 0, 0, -9, 1, -9, 1, -9, 0], [0, 0, 0, -9, 0, -9, 0, -9, 0]],  # 跳二
                [[0, 0, -9, -9, 1, 1, -9, -9, 0],[0, 0, -9, -9, 0, 0, -9, 1, 0]],  # 比較弱的活二(單面開)
                [[0, 0, -9, -9, 1, 1, -9, -9, 0], [0, -9, -9, -9, 0, 0, 1, 0, 0]]  # 死二
        ]

        # 每個圖形對應的名稱，用於debug
        JudgeArray.pattern_name = ['五連', '活四', '活三', '活二',
                                   '跳四(長邊)', '跳四(短邊)', '跳四(中間)', '死四',
                                   '跳三(長邊)', '跳三(短邊)', '跳三(長邊死, 長邊)', '跳三(短邊死, 長邊)', '跳三(長邊死, 短邊)', '跳三(短邊死, 短邊)',
                                   '死三', '跳二', '弱活二', '死二']

        # flattern使用的計數器
        JudgeArray.flag = 0

    def __init__(self, width = 13, copyFrom = None):
        
        self.width = width
        
        if not copyFrom is None:
            self.solvePoint = deepcopy(copyFrom.solvePoint)
            self.solveRange = deepcopy(copyFrom.solveRange)
        else:
            # 清空[附近有棋子]的資訊
            self.solvePoint = []
            for i in range(0, width):
                self.solvePoint.append([0]*width)

        try:
            try:
                # print('Try to find JudgeArray...', end=' ')
                JudgeArray.judge_array
                # print('JudgeArray exist')
            except AttributeError:
                # print('JudgeArray not exist')
                self.ResetJudgeArray()
            # print('try to load file...', end=' ')
            
            # pattern 達成後的分數
            JudgeArray.judge_score = JudgeArray.pattern_score + JudgeArray.pattern_mirror_score
            # 阻擋分數
            JudgeArray.block_score = [500, 300, 40, 0] # 阻擋分數
            
            # 判斷 pattern 的矩陣
            JudgeArray.judge_array = np.load('judge_array.npy')
            
            
            # 達成每個 pattern 分別需要的激活分數
            JudgeArray.judge_weight = np.load('judge_weight.npy')
            
            # 將 68 種不同位置的pattern 集結成 18 種類型
            JudgeArray.flattern = np.load('judge_flattern.npy')
            # print('Evaluate matrix load from files.')
        except FileNotFoundError:

            # 如果沒有檔案 -> 生成檔案
            # print('Evaluate matrix not found, creating a new one...', end=' ')
            # 初始化
            JudgeArray.judge_array = []
            JudgeArray.judge_weight = []
            JudgeArray.flattern = 0

            # 非對稱圖形
            for index, x in enumerate(JudgeArray.pattern_kind):
                for i in range(0, x):
                    # roll the list
                    JudgeArray.judge_array.append([JudgeArray.pattern_shift[index][0][i:] + JudgeArray.pattern_shift[index]
                                                [0][:i], JudgeArray.pattern_shift[index][1][i:] + JudgeArray.pattern_shift[index][1][:i]])
                    
                    
                    # 圖形的激活分數
                    JudgeArray.judge_weight.append(
                        1/JudgeArray.pattern_esti[index])
                    # 註冊平坦化
                    JudgeArray.flattern += 1
            # 對稱圖形
            for index, x in enumerate(JudgeArray.pattern_mirror_total_appear_times):
                for i in range(0, x):
                    # reflect the list in "mirror"
                    JudgeArray.judge_array.append([JudgeArray.pattern_mirror[index][0][i:] + JudgeArray.pattern_mirror[index]
                                                [0][:i], JudgeArray.pattern_mirror[index][1][i:] + JudgeArray.pattern_mirror[index][1][:i]])

                    JudgeArray.judge_score.append(
                        JudgeArray.pattern_mirror_score[index])
                    # 圖形的激活分數
                    JudgeArray.judge_weight.append(
                        1/JudgeArray.pattern_mirror_esti[index])
                    # 註冊平坦化
                    JudgeArray.flattern += 1

                    # 反轉圖形
                    lst1, lst2 = JudgeArray.pattern_mirror[index][0][i:] + JudgeArray.pattern_mirror[index][0][:
                                                                                                            i], JudgeArray.pattern_mirror[index][1][i:] + JudgeArray.pattern_mirror[index][1][:i]
                    lst1.reverse()
                    lst2.reverse()
                    JudgeArray.judge_array.append([lst1, lst2])
                    
                    
                    # 圖形的激活分數
                    JudgeArray.judge_weight.append(
                        1/JudgeArray.pattern_mirror_esti[index])
                    # 註冊平坦化
                    JudgeArray.flattern += 1

            # 建立平坦化矩陣
            JudgeArray.flattern = np.zeros((JudgeArray.flattern, len(
                JudgeArray.pattern_kind)+len(JudgeArray.pattern_mirror_total_appear_times)))
            for index, times in enumerate(JudgeArray.pattern_kind):

                for i in range(0, times):
                    JudgeArray.flattern[JudgeArray.flag][index] = 1
                    JudgeArray.flag += 1

            for index, times in enumerate(JudgeArray.pattern_mirror_total_appear_times):
                for i in range(0, times):
                    # 因為有鏡射所以做兩次
                    JudgeArray.flattern[JudgeArray.flag][len(
                        JudgeArray.pattern_kind) + index] = 1
                    JudgeArray.flag += 1
                    JudgeArray.flattern[JudgeArray.flag][len(
                        JudgeArray.pattern_kind) + index] = 1
                    JudgeArray.flag += 1
            # list轉array
            JudgeArray.judge_array = np.array(JudgeArray.judge_array)
            # 加權函數轉成對角矩陣
            JudgeArray.judge_weight = np.diag(
                np.array(JudgeArray.judge_weight))

            # 轉換形狀方便運算
            JudgeArray.judge_array = JudgeArray.judge_array.swapaxes(
                0, 1).swapaxes(1, 2)

            np.save('judge_array.npy', JudgeArray.judge_array)
            np.save('judge_weight.npy', JudgeArray.judge_weight)
            np.save('judge_flattern.npy', JudgeArray.flattern)
            # print("Evaluate matrix done.")
                

    #@jit(forceobj=True)
    def force_nined(self, board, loc):
        """Input a location, return a 9*1 list. If the list ins't big enough(out of board), let white fill 0 and black fill 1  """

        target = [[], [], [], []]

        for x in range(-4, 5):
            if loc[0]+x in range(0, len(board[0])) and loc[1]+x in range(0, len(board[0])):
                target[0].append([board[0][loc[0]+x][loc[1]+x],
                                  board[1][loc[0]+x][loc[1]+x]])
            else:
                target[0].append([0, 1])
            if loc[0]-x in range(0, len(board[0])) and loc[1]+x in range(0, len(board[0])):
                target[1].append([board[0][loc[0]-x][loc[1]+x],
                                  board[1][loc[0]-x][loc[1]+x]])
            else:
                target[1].append([0, 1])
            if loc[0] in range(0, len(board[0])) and loc[1]+x in range(0, len(board[0])):
                target[2].append([board[0][loc[0]][loc[1]+x],
                                  board[1][loc[0]][loc[1]+x]])
            else:
                target[2].append([0, 1])
            if loc[0]+x in range(0, len(board[0])) and loc[1] in range(0, len(board[0])):
                target[3].append([board[0][loc[0]+x][loc[1]],
                                  board[1][loc[0]+x][loc[1]]])
            else:
                target[3].append([0, 1])
        return target

    def Solve(self, board_init, loc):
        """針對單一位置做評估，回傳 [破壞對手形狀 與 達成己方形狀]，運算時的改動不會影響到傳入的矩陣"""
        
        board = deepcopy(board_init)
        # 儲存結果
        self.enemyValue = self.Analyze_self([board[1], board[0]], loc)

        board = deepcopy(board_init)
        # 儲存結果
        self.selfValue = self.Analyze_self([board[0], board[1]], loc)

        return [self.enemyValue, self.selfValue]

    def Solve_and_DetectWin(self, board_init, loc):
        """等同於Solve，但額外紀錄盤勢；會回傳是否已經勝利"""
        solution = self.Solve(board_init, loc)

        # 偵測是否勝利
        isWin = list([False, True])[int(np.dot(self.selfValue, JudgeArray.winDetect))]

        return solution, isWin

    def AI_Solve(self, board, last_loc, score, judge, alphaIsBlack):
        """遍歷所有附近有棋子的點，找出最佳落子位置"""
        from pruning_tree import alpha_beta_tree, Node
        #! board = [player, AI]
        tree = alpha_beta_tree(board, enemyLastLoc = last_loc, deep = const.deep, score = score, judge = judge, alphaIsBlack = alphaIsBlack)
        
        return tree.Run()

    def AddSolveRange(self, board, loc):
        """在loc處放置棋子後，更新 self.solvePoint & self.solveRange 並回傳新的 [[pos 1],[pos 2],...] """
        #* 現在的做法是只取 [最後落子位置附近的4格內] 範圍
        #* 取代了以前 [所有棋子附近2格的範圍] 的做法
        self.solveRange = []
        # loc
        for x in range(loc[0]-4, loc[0]+5):
            for y in range(loc[1]-4, loc[1]+5):
                try:
                    if x >= 0 and y >= 0 :
                        if self.solvePoint[x][y] == 0 and board[0][x][y] == 0 and board[1][x][y] == 0 and [x, y] != loc:
                            self.solvePoint[x][y] = 1
                            self.solveRange.insert(0, [x, y])
                except IndexError:
                    # location outside of board
                    pass

    def Analyze_self(self, board, loc):
        """檢查 player 0 落子於 {board[0]} 的 {loc} 對盤面的影響"""

        # put testing chess
        board[0][loc[0]][loc[1]] = 1
        # fill testing board with spec value
        target = self.force_nined(board=board, loc=loc)
        total_pattern = None

        target = np.array(target).swapaxes(0, 2).swapaxes(1, 2)

        # 用矩陣判斷
        ret = np.matmul(target, JudgeArray.judge_array)

        #ret = ret.reshape(JudgeArray.judge_array.shape[0], 2*len(target[0][0]))
        # 加總主對角線
        ret = ret[0]+ret[1]

        # 運算是否存在pattern (1/2)
        ret = np.matmul(ret, JudgeArray.judge_weight)

        # 判斷種類，1 = 有此種類 (2/2)
        ret = np.maximum(np.floor(ret), 0)

        # 平坦化
        ret = np.dot(ret, JudgeArray.flattern)

        total_pattern = ret[0]+ret[1]+ret[2]+ret[3]

        return total_pattern
    

# 測試輸入
if __name__ == '__main__':
    judge = Judge()
    test = [[[0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 1, 0, 0],
             [0, 0, 0, 1, 0, 1, 0, 0, 0],
             [0, 0, 0, 0, 0, 1, 1, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 1, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 1, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0]],
            [[0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 1, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0]]]

    detect = judge.Solve([test[0], test[1]], loc=[5, 5])

    print("阻擋了:")
    for i in range(0, len(JudgeArray.pattern_name)):
        if detect[0][i] >= 1:
            print("{}:{}".format(
                JudgeArray.pattern_name[i], (int)(detect[0][i])))
    print("達成了:")
    for i in range(0, len(JudgeArray.pattern_name)):
        if detect[1][i] >= 1:
            print("{}:{}".format(
                JudgeArray.pattern_name[i], (int)(detect[1][i])))

