
class Analyze():
    """Read file from txt and output as (x, y) by calling function 'Shot()'\n
        when one round is ended, output (0, 0); when all data showed, output (-1, -1)"""
    datasetPath = r'raw_dataset/good_ones.txt'
    dataset = []
    #if the graph of a round is larger then "board_range", discard the round
    board_range = 13
    
    now_line, now_step_place = 0, 0

    def __init__(self):
        totalRounds = self.Read(self.datasetPath)
        print("Done. Return ({}/{}) rounds in file, with board larger then {} is discarded.".format(len(self.dataset), totalRounds, self.board_range))

    def Read(self, path):
        """read file and save"""
        with open(path,'r') as f:
	        lines = f.readlines()
        for index, line in enumerate(lines):
            line = line.replace('\n','')
            item = line.split(" ")[1:]
            step = self.ModifyOneLine(item)
            #not need to care about the first player 
            if(step):
                self.dataset.append(step)
        return len(lines)

    def ModifyOneLine(self, lineList):
        data, ret = [], []
        col_min, col_max = 19, 1
        row_min, row_max = 19, 1
        for index, step in enumerate(lineList):
            col, row = self.FormatStep(step)
            col_min, row_min = min(col_min,col), min(row_min,row)
            col_max, row_max = max(col_max,col), max(row_max,row)
            step = (col,row)
            data.append(step)
        if(col_max - col_min < self.board_range and row_max - row_min < self.board_range):
            for step in data:
                ret.append( (int(step[0]) - col_min + int((self.board_range- (col_max - col_min) )/2 ), (int(step[1]) - row_min + int((self.board_range -(row_max - row_min))/2)) ) )
            return ret
        else:
            return None
    
    def FormatStep(self, step):
        """input h8 -> return (8, 8)"""
        #raw date skipped 'i'
        if(ord(step[0]) - ord('a') >= ord('j') - ord('a')):
            return int(ord(step[0]) - ord('a'))-1 , int(step[1:])
        else:
            return int(ord(step[0]) - ord('a')), int(step[1:])
            

    def Shot(self):
        """output (x,y) in dataset[line,place]"""
        if(self.now_step_place == len(self.dataset[self.now_line])):
            self.now_line += 1
            self.now_step_place = 0
            return 0, 0

        if(self.now_line == len(self.dataset) ):
            print("Dataset has no more steps.")
            return -1, -1
        
        ret = self.dataset[self.now_line][self.now_step_place]

        self.now_step_place += 1
        return ret




if __name__ == '__main__':
    analyze = Analyze()
    while(True):
        x, y = analyze.Shot()
        if(x==0):
            input()
        elif(x==-1):
            break
        print("x:{}, y:{}".format(x, y))