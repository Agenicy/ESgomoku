#import cupy as np
import numpy as np
"""
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D
"""

from game_engine import const

# 加速器
from numba import jit

from pruning_tree import alpha_beta_tree, Node


class JudgeArray(object):
    # 定義需要防守的對方 pattern
    defPattern = np.array([
        1, 1, 1, 0,         # '五連','活四','活三','活二',
        1, 1, 1, 1,         # '跳四(長邊)','跳四(短邊)','跳四(中間)','死四',
        # '跳三(長邊)','跳三(短邊)','跳三(長邊死, 長邊)','跳三(短邊死, 長邊)','跳三(長邊死, 短邊)','跳三(短邊死, 短邊)',
        1, 1, 0, 0, 0, 0,
        0, 0, 0, 0         # '死三','跳二','弱活二','死二'
    ])

    winDetect = np.array([
        1, 1, 0.5, 0,         # '五連','活四','活三','活二',
        0.5, 0.5, 0.5, 0.5,         # '跳四(長邊)','跳四(短邊)','跳四(中間)','死四',
        # '跳三(長邊)','跳三(短邊)','跳三(長邊死, 長邊)','跳三(短邊死, 長邊)','跳三(長邊死, 短邊)','跳三(短邊死, 短邊)',
        0.5, 0.5, 0, 0, 0, 0,
        0, 0, 0, 0         # '死三','跳二','弱活二','死二'
    ])


class Judge(object):
    """評估器"""

    # 兩格內有棋子的點
    solvePoint = None

    # 搜索深度(-1 = nan)
    searchStep = 1

    # 自己上一次落子位置
    # ? 存到別的地方去 (評估的第一步會出問題)
    myLastLoc = []

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
            # [[0,0,-1,-1, 1 ,1,1,-1,-1],[0,0,1,-1, 0 ,0,0,-1,1]], # 假活三(被夏止防守)
            [[0, 0, -1, -1, 1, 1, -1, -1, 0], [0, 0, -1, -1, 0, 0, -1, -1, 0]]  # 活二
        ]
        # 圖形，包含移動前共有幾個
        JudgeArray.pattern_kind = [5, 4, 3, 2]
        # 滿足圖形所需的激活分數
        JudgeArray.pattern_esti = [5, 4, 3, 2]
        # 圖形的分數
        JudgeArray.pattern_score = [999, 100, 50, 10]
        # 無法只靠平移檢測的圖形
        JudgeArray.pattern_mirror = [
            [[0, 0, 0, -9, 1, 1, 1, -9, 1],
                [0, 0, 0, 0, 0, 0, 0, -9, 0]],  # 跳四(長邊)
            [[0, 0, 0, -9, 1, -9, 1, 1, 1],
                [0, 0, 0, 0, 0, -9, 0, 0, 0]],  # 跳四(短邊)
            [[0, 0, 0, -9, 1, 1, -9, 1, 1],
                [0, 0, 0, 0, 0, -9, 0, 0, 0]],  # 跳四(中間)
            [[0, 0, 0, -9, 1, 1, 1, 1, -9], [0, 0, 0, -9, 0, 0, 0, 0, 1]],  # 死四
            [[0, 0, -9, -9, 1, 1, -9, 1, -9],
                [0, 0, 0, -9, 0, 0, -9, 0, -9]],  # 跳三(長邊)
            [[0, 0, -9, -9, 1, -9, 1, 1, -9],
                [0, 0, 0, -9, 0, -9, 0, 0, -9]],  # 跳三(短邊)
            [[0, 0, -9, -9, 1, 1, -9, 1, -9],
                [0, 0, 0, 1, 0, 0, -9, 0, -9]],  # 跳三(長邊死, 長邊)
            [[0, 0, -9, -9, 1, 1, -9, 1, -9],
                [0, 0, 0, -9, 0, 0, -9, 0, 1]],  # 跳三(短邊死, 長邊)
            [[0, 0, -9, -9, 1, -9, 1, 1, -9],
                [0, 0, 0, -9, 0, -9, 0, 0, 1]],  # 跳三(長邊死, 短邊)
            [[0, 0, -9, -9, 1, -9, 1, 1, -9],
                [0, 0, 0, 1, 0, -9, 0, 0, -9]],  # 跳三(短邊死, 短邊)
            [[0, 0, -9, -9, 1, 1, 1, -9, 0], [0, 0, 0, -9, 0, 0, 0, 1, 0]],  # 死三
            [[0, 0, 0, -9, 1, -9, 1, -9, 0], [0, 0, 0, -9, 0, -9, 0, -9, 0]],  # 跳二
            [[0, 0, -9, -9, 1, 1, -9, -9, 0],
                [0, 0, -9, -9, 0, 0, -9, 1, 0]],  # 比較弱的活二(單面開)
            [[0, 0, -9, -9, 1, 1, -9, -9, 0], [0, -9, -9, -9, 0, 0, 1, 0, 0]]  # 死二
        ]
        # 對稱圖形，包含移動前共有幾個
        JudgeArray.pattern_mirror_total_appear_times = [
            3, 1, 2, 4, 2, 1, 2, 2, 1, 1, 3, 1, 2, 2]
        # 對稱圖形的分數
        JudgeArray.pattern_mirror_score = [
            60, 60, 30, 30, 50, 50, 45, 45, 45, 45, 20, 5, 5, 1]
        # 滿足對稱圖形所需的激活分數
        JudgeArray.pattern_mirror_esti = [
            4, 4, 4, 5, 3, 3, 4, 4, 4, 4, 4, 2, 3, 3]

        # 每個圖形對應的名稱，用於debug
        JudgeArray.pattern_name = ['五連', '活四', '活三', '活二',
                                   '跳四(長邊)', '跳四(短邊)', '跳四(中間)', '死四',
                                   '跳三(長邊)', '跳三(短邊)', '跳三(長邊死, 長邊)', '跳三(短邊死, 長邊)', '跳三(長邊死, 短邊)', '跳三(短邊死, 短邊)',
                                   '死三', '跳二', '弱活二', '死二']

        # flattern使用的計數器
        JudgeArray.flag = 0

    def __init__(self):

        # 自己上一次落子位置
        self.myLastLoc = []

        # 清空[附近有棋子]的資訊
        self.solvePoint = None

        try:
            try:
                print('Try to find JudgeArray...', end=' ')
                JudgeArray.judge_array
                print('JudgeArray exist')
            except AttributeError:
                print('JudgeArray not exist')
                self.ResetJudgeArray()
            print('try to load file...', end=' ')
            JudgeArray.judge_array = np.load('judge_array.npy')
            JudgeArray.judge_score = np.load('judge_score.npy')
            JudgeArray.judge_weight = np.load('judge_weight.npy')
            JudgeArray.flattern = np.load('judge_flattern.npy')
            print('Evaluate matrix load from files.')
        except FileNotFoundError:

            # 如果沒有檔案 -> 生成檔案
            print('Evaluate matrix not found, creating a new one...', end=' ')
            # 初始化
            JudgeArray.judge_array = []
            JudgeArray.judge_weight = []
            JudgeArray.judge_score = []
            JudgeArray.flattern = 0

            # 非對稱圖形
            for index, x in enumerate(JudgeArray.pattern_kind):
                for i in range(0, x):
                    # roll the list
                    JudgeArray.judge_array.append([JudgeArray.pattern_shift[index][0][i:] + JudgeArray.pattern_shift[index]
                                                   [0][:i], JudgeArray.pattern_shift[index][1][i:] + JudgeArray.pattern_shift[index][1][:i]])
                    # 圖形的分數
                    JudgeArray.judge_score.append(
                        JudgeArray.pattern_score[index])
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
                    # 圖形的分數
                    JudgeArray.judge_score.append(
                        JudgeArray.pattern_mirror_score[index])
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
            np.save('judge_score.npy', JudgeArray.judge_score)
            np.save('judge_weight.npy', JudgeArray.judge_weight)
            np.save('judge_flattern.npy', JudgeArray.flattern)
            print("Evaluate matrix done.")

    # @jit(forceobj=True,nopython=True)
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

        loc[0] = len(board_init[0]) - loc[0]
        loc[1] -= 1

        import copy
        board = copy.deepcopy(board_init)
        # 儲存結果
        self.enemyValue = self.Analyze_self([board[1], board[0]], loc)

        board = copy.deepcopy(board_init)
        # 儲存結果
        self.selfValue = self.Analyze_self([board[0], board[1]], loc)

        return [self.enemyValue, self.selfValue]

    def Solve_and_DetectWin(self, board_init, loc):
        """等同於Solve，但額外回傳是否已經勝利"""
        board = self.Solve(board_init, loc)

        # 偵測是否勝利
        isWin = list([False, True])[
            int(np.dot(self.selfValue, JudgeArray.winDetect))]

        return board, isWin

    def AI_Solve(self, board, last_loc=None):
        """遍歷所有附近有棋子的點，找出最佳落子位置"""

        # 尚未建立[需評估位置( = 附近有棋子的位置 )]
        if self.solvePoint is None:
            # 依據現在盤面建立[初始 需評估位置]
            self.Generate_SolvePoint(board)

        # 建立 alpha_beta_tree ，並讓它學會建立子節點
        # TODO 修好這個
        '''searchTree = alpha_beta_tree(step = self.searchStep, board = board, 
                                     searchRange = self.SolveRange(board, need_to_defense, last_loc),
                                     judge = self)

        # 自動根據 need_to_defense 標出需搜索範圍
        searchTree.GoThrough()'''
        return [[0], [0]]

    @jit(forceobj=True, nopython=True)
    def Generate_SolvePoint(self, board):
        """初始化 self.solvePoint"""
        self.solvePoint = []
        # 初始化
        for i in range(0, len(board[0])):
            self.solvePoint.append([0]*len(board[0]))

        # 建立後續的位置
        for x in range(0, len(board[0])):
            for y in range(0, len(board[0])):
                if board[0][x][y] or board[1][x][y] == 1:
                    # 有棋子，未來不用檢測
                    self.solvePoint[x][y] = -1
                    for h in range(max(0, y-2), min(y+3, len(board[0]))):
                        for w in range(max(0, x-2), min(x+3, len(board[0]))):
                            # 原本是空位子，需要被檢測
                            if self.solvePoint[w][h] == 0:
                                self.solvePoint[w][h] = 1

    @jit(forceobj=True, nopython=True)
    def SolveRange(self, board, needToDefense=False, last_loc=None):
        """解讀 self.solvePoint，回傳 [[pos 1],[pos 2],...] """
        ret = []

        if needToDefense:
            for x in range(-4, 5):
                self.check(board, last_loc[0]+x,    last_loc[1]+x, ret)
                self.check(board, last_loc[0]-x,    last_loc[1]+x, ret)
                self.check(board, last_loc[0],      last_loc[1]+x, ret)
                self.check(board, last_loc[0]+x,    last_loc[1]  , ret)
        else:
            for x in range(0, len(board[0])):
                for y in range(0, len(board[0])):
                    if self.solvePoint[x][y] == 1:
                        # 如果和自己上次落子位置有連線
                        if abs(x - self.myLastLoc[0]) == abs(y - self.myLastLoc[1]) \
                                or (x - self.myLastLoc[0]) == 0 or (y - self.myLastLoc[1]) == 0:
                            ret.insert(0, [x, y])
                        # 如果沒有
                        else:
                            ret.append([x, y])
        return ret

    def check(self, board, posX, posY, ret):
        if posX in range(0, len(board[0])) and posY in range(0, len(board[0])):
            if self.solvePoint[posX][posY] == 1:
                ret.append([[posX], [posY]])

    def Mark_OnePoint(self, loc):
        return

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
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
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
    if True:
        detect = judge.Solve([test[0], test[1]], loc=[5, 5])

        print("阻擋了:")
        for i in range(0, len(JudgeArray.pattern_name)):
            if detect[0][i] >= 1:
                print("{}:{}".format(
                    judge.pattern_name[i], (int)(detect[0][i])))
        print("達成了:")
        for i in range(0, len(JudgeArray.pattern_name)):
            if detect[1][i] >= 1:
                print("{}:{}".format(
                    JudgeArray.pattern_name[i], (int)(detect[1][i])))
    else:
        judge.AI_Solve([test[1], test[0]], last_loc=[5, 5])
