
import numpy as np

class Analyze():
    """Read file from txt and output as (x, y) by calling function 'Shot()'\n
        when one round is ended, output (0, who_wins); when all data showed, output (-1, -1)"""
    # datasetPath = r'raw_dataset/good_ones.txt'
    datasetPath = r'raw_dataset/test.txt'
    dataset = []
    # if the graph of a round is larger then "board_range", discard the round
    board_range = 13
    
    # vars used in Shot
    # ★ notice that now_step_place is start form 1 bcoz 0 is the winner
    now_line, now_step_place = 0, 1

    # the winner in this round; (black: 0, white: 1)
    winner = [0, 0]

    # graph of a round
    # ★ notice that this is no [is first player] inside
    graph = np.zeros((3, board_range, board_range))

    def __init__(self, board_range=13):
        self.board_range = board_range
        totalRounds = self.Read(self.datasetPath)
        print("Done. Return ({}/{}) rounds in file, with board larger then {} is discarded.".format(len(self.dataset), totalRounds, self.board_range))

    def Read(self, path):
        """read file and save"""
        with open(path,'r') as f:
	        lines = f.readlines()
        for line in lines:
            line = line.replace('\n','')
            item = line.split(' ')
        
            step = self.ModifyOneLine(item)
            # not need to care about the first player 
            if(step):
                self.dataset.append(step)
        return len(lines)

    def ModifyOneLine(self, lineList):
        """translate one line items to steps"""
        data, ret = [], []
        col_min, col_max = 19, 1
        row_min, row_max = 19, 1

        # abstract the winner
        self.winner = [0.0, 0.0]
        self.winner[ {"black":0, "white":1}.get(lineList[0]) ] = 1.0
        lineList = lineList[1:]

        for step in lineList:
            col, row = self.FormatStep(step)
            col_min, row_min = min(col_min,col), min(row_min,row)
            col_max, row_max = max(col_max,col), max(row_max,row)
            step = (col,row)
            data.append(step)
        if(col_max - col_min < self.board_range and row_max - row_min < self.board_range):
            for step in data:
                #relocation graph, let new center of graph match to the center of the board
                ret.append( (int(step[0]) - col_min + int((self.board_range- (col_max - col_min) )/2 ), (int(step[1]) - row_min + int((self.board_range -(row_max - row_min))/2)) ) )
            return ret
        else:
            return None
    
    def FormatStep(self, step):
        """input h8 -> return (8, 8)"""
        # raw date skipped 'i'
        if(ord(step[0]) - ord('a') >= ord('j') - ord('a')):
            return int(ord(step[0]) - ord('a'))-1 , int(step[1:])
        else:
            return int(ord(step[0]) - ord('a')), int(step[1:])
            

    def Shot(self):
        """output (x,y) in dataset[line,place]"""
        if(self.now_step_place == len(self.dataset[self.now_line])):
            self.now_line += 1
            self.now_step_place = 1
            return 0, self.winner

        if(self.now_line == len(self.dataset) ):
            print("Dataset has no more steps.")
            return -1, -1
        
        ret = self.dataset[self.now_line][self.now_step_place]

        self.now_step_place += 1
        return ret

    def GetGraphic(self):
        # restart one round
        self.now_step_place = 1

        # set now player = black
        now_player = 1

        # shot, loop, until the game is ended !
        while(now_player != 0):
            now_player = self.GetShot(now_player)

        for x in range(0,3):
            print(self.graph[x])
        print(self.winner)


    def GetShot(self, now_player):
        """Return game_ended ? 0 : (now_player * -1) , and modify self.graph"""

        # loc to mov
        location = self.Shot()
        if location[0] == 0: # round end
            return 0
        h = location[0]
        w = location[1]
        move = h * self.board_range + w

        if now_player == 1: # black
            self.graph[0][move // self.board_range, move % self.board_range] = 1.0
        elif now_player == -1: # white
            self.graph[1][move // self.board_range, move % self.board_range] = 1.0
        else: # error
            print("A fatal error exist, in 'GetShot' of 'Analyze'")

        self.graph[2] = np.zeros( (self.board_range, self.board_range) )
        self.graph[2][move // self.board_range, move % self.board_range] = 1.0

        return now_player * -1


if __name__ == '__main__':
    analyze = Analyze()
    analyze.GetGraphic()