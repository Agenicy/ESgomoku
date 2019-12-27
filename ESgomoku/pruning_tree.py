import math
from evaluate_points import Judge, JudgeArray, np # np will be numpy or cupy
import copy

class Data:
    step = []
    board = []
    isAlpha = True

class Node(object):
    """敵方盤勢board - 我方動作loc"""
    def __init__(self, step = 0, isAlpha = True):
        self.pattern = [[],[]]
        self.value = 0
        self.child = []
        # 剩餘搜索深度
        self.step = step
        self.isAlpha = isAlpha

    def Set(self, loc = [0,0], board = [], path = [], searchRange = [], judge = None, enemyLastLoc = None):
        self.loc = loc
        self.board = board
        self.path = path
        self.judge = judge
        self.enemyLastLoc = enemyLastLoc # 僅 root Node 使用
        
        self.searchRange = searchRange
        
        # TODO: searchRange 標上 推演步(loc)的影響
        
        # TODO 計算盤勢
        
        

    def is_Need_to_defense(self, parentNode = None):
        """判斷對方是否組成活三等攻擊型pattern"""        
        # 對方是否組成 我方一定要防守 的型式，減少搜尋時間
        if not parentNode is None:
            return list([False, True])[int(np.dot(parentNode.judge.selfValue, JudgeArray.defPattern))]
        else:
            # 僅 root Node 使用
            return list([False, True])[int(np.dot(self.judge.Solve(self.board, self.enemyLastLoc)[0],JudgeArray.defPattern))]


class alpha_beta_tree(object):
    def __init__(self, step, board, searchRange, judge, enemyLastLoc):
        """敵方盤勢board - 我方動作loc"""
        self.minV = math.nan
        self.maxV = -math.nan

        self.root = self.parent = Node(step = step, isAlpha = True)
        self.root.Set(board = board, path = [], searchRange = searchRange, judge = judge, enemyLastLoc = enemyLastLoc)


    def GetNewNode(self, parentNode, loc):
        """根據輸入位置，回傳一個新的節點"""
        if parentNode.step == 0:
            raise Exception('Error: Step = 0')
        return Node(step = parentNode.step - 1, isAlpha = not parentNode.isAlpha)


    def GoThrough(self):
        """遍歷所有可能是下一步的點，深度優先"""
        self.SpanChild(self.root)

    def SpanChild(self, target_node):
        # searchRange 已經為 alpha-beta 排序
        # 根據 target_node 當前盤勢，推演一步
        
        for point in target_node.searchRange:
            child = self.GetNewNode(self.root, loc = point)
            
            # 判斷新的 searchRange
            # TODO 判斷新的 searchRange
            
            # 深度優先
            if child.step > 0:
                self.SpanChild(child)
                
            # 抵達深度盡頭，計算本節點分數 = 當前盤勢
            child.Set(loc = point, board = target_node.board, 
                      path = target_node.path, searchRange = target_node.searchRange, judge = target_node.judge)
            
            child.value
            
