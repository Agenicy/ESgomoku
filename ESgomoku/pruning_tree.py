import math

class Node(object):
    """子節點，可用方法如下\n
        生成child/ 得到自己的分數/ """
    def __init__(self, parent, name = "'undefined'", value = 0, isAlpha = True, 
                 board = [], searchRange = [], WayToSpanTree = None, WayToGetValue = None):
        # Judge
        self.judge = parent.judge
        # vars
        self.name = name
        self.child = []
        self.parent = parent
        self.value = value
        self.isAlpha = isAlpha
        # vars
        self.board = board
        self.searchRange = searchRange
        # func
        if WayToGetValue is None:
            self.GetValue = parent.WayToGetValue
        else:
            self.GetValue = WayToGetValue

        if WayToSpanTree is None:
            self.SpanChild = parent.SpanChild
        else:
            self.SpanChild = WayToSpanTree
        
    def is_Leaf(self):
        return len(self.child) == 0

    def is_Root(self):
        return self.parent is None


class alpha_beta_tree(object):
    def __init__(self, step = -1, WayToSpanTree = None, WayToEvaluate = None, board = [], searchRange = [], judge = None):
        """按照 搜索深度step，使用WayToSpanTree的方式添加子節點，每個節點運用WayToEvaluate計算自身價值\n
           可以展開節點的位置為range，而局勢的資料為board\n
           """
        # Judge
        self.judge = judge
        # labels
        self.name = 'tree'
        self.max = -math.nan
        self.min = math.nan
        self.step = step
        self.board = board
        self.searchRange = searchRange
        self.root = Node(parent = self, name = "0", value = 0, isAlpha = True, 
                         board = board, searchRange = searchRange, WayToSpanTree = WayToSpanTree, WayToGetValue = WayToEvaluate)
        # functions

    def StartPruning(self):
        self.root.SpanChild(None,self.root)

    def PruningOneNode(self, node):
        pass
        # return targetNode


