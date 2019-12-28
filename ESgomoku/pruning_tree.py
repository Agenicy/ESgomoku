import math
from evaluate_points import Judge, JudgeArray, Score, np # np will be numpy or cupy
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
    """
    > 總盤勢分數 = 我方盤勢分數 * (進攻係數) - 敵方盤勢分數
    > 我方盤勢分數 = 整個版面上我方 pattern 分數 * [(達成權值)] - 被敵方阻擋的 pattern 分數 * [(阻擋權值)]
    > 我方盤勢分數 = 整個版面上敵方 pattern 分數 * [(達成權值)] - 被我方阻擋的 pattern 分數 * [(阻擋權值)]
        - 從第一手開始持續記錄各種pattern數量
        
    [第零層]
        玩家落子，是為 root
    [第一層 - Alpha]
        從敵方落子後開始，計算第一次候選步
            ! 此時節點 board = [ [AI], [Player] ]
            - 每個候選步都是一個節點，節點的 board 為候選步落子後的盤勢
            ! 此時 board 順序未變
            - 如果勝利則停止計算 並回傳
            - 如果未勝利，按照候選步更新可落子區域( judge.solvePoint )，並取得新的 searchRange
            - 按照新的 searchRange 計算第二次候選步
    [第二層 - Beta]
        計算第二次候選步
            ! 此時節點 board = [ [Player], [AI] ]
            - 方法與第一次相同
            - 按照新的 searchRange 計算第三次候選步
    [第三層 - Alpha]
        計算第三次候選步
            ! 此時節點 board = [ [AI], [Player] ]
            - 方法與第一次相同
            - 因為抵達深度盡頭 ( step = 0 )，不再延伸子樹
            * 現在位於「第一個抵達深度盡頭」的節點
            - 回傳自己的盤勢分數 value
    [剪枝與持續搜尋]
            * 現在回到 parent ( 第二層 )
            - 檢查 child.value 是否「小於」 childValueFinal ( 因為第二層是beta，他會取AI分數的最小值 )
                > 是
                - 修改 childValueFinal = child.value
            - 由於 for 迴圈，這個動作會持續到所有節點都走過一次
            - 得到自己該選擇的最佳位置
            - 回傳最後的盤勢分數
            
            * 現在回到 parent ( 第一層 )
            - 檢查 child.value 是否「大於」 childValueFinal ( 第一層是alpha )
                > 是
                - 修改 childValueFinal = child.value
                - 紀錄 stepChoose = 候選步
            - 由於 for 迴圈，這個動作會持續到所有節點都走過一次
            
            [loop]
            * 由於迴圈，現在進入 child ( 第二層，第二棵子樹 )
            /* 現在會開始剪枝 */
            - [計算新的第三次候選步]
            - 由於 for 迴圈，會持續收到child.value
            /* 如果收到了比之前更小的總和盤勢分數，代表進入第二層的這一步對AI不利，因此放棄 */
            - 檢查 child.value 是否小於 childValueFinal
                > 是
                - 放棄搜尋，回傳 None
            > 最大的 child.value 比 childValueFinal 大
            - 回傳最大的 child.value， parent 端會做後續處理
            
            [loop]
            * 又回到 parent ( 第一層 )
            - 檢查 child.value 是否大於 childValueFinal
                > 是
                - 修改 childValueFinal = child.value
                - 紀錄 stepChoose = 候選步
                > 否
                - 跳過
            - 繼續尋找下一棵子樹
    [結束]
        回傳 stepChoose        
    """
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
            
