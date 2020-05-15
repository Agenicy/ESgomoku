import cv2
import time
import numpy as np

import cv2

class detect():
    def __init__(self, camera, points=9, outline = 3):
        super().__init__()
        
        unitW = 50
        unitH = 50
        self.color_black = [100,100,100]
        self.color_white = [180,220,230]
        
        self.vis = [[0]*points]*points
        self.count = 0 # numbers of chess now
        
        self.memory = [] # board-changed that founded
        self.confidence = 0.0 # confidence of board changed
        self.conf_trigger = 5 # trigger num of confdence
        
        self.cam = camera
        
        self.points = points
        self.pos = []
        for x in range(outline, points + outline):
            for y in range(outline, points + outline):
                self.pos.append([unitW * x, unitH * y])

    def getLoc(self):
        while True:
            im, d = self.cam.getDst()
            d = cv2.blur(d,(8, 8))
            color, loc = self.analyze(d)
            ims = cv2.resize(im,(320,320))
            ds = cv2.resize(d,(320,320))
            cv2.imshow('original', ims)
            cv2.imshow('result', ds)
            if not color is None:
                loc[0], loc[1] = loc[1], loc[0]
                return color, loc
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            nowTime = time.time()
            while time.time() - nowTime < 0.1:
                # block
                im, d = self.cam.getDst()
    
    def analyze(self, dst):
        """取得當前棋盤所有落子位置"""
        black, white, dotList = self.getDot(dst)
        dotChange, color = self.getChange(dotList)
        if color != 0:
            self.count += 1
            print(f'Step {self.count}: { {1:"black",2:"white"}.get(color) } {dotChange}')
            return color, dotChange
        else:
            return None, [-1,-1]
        
    def getDot(self, img):
        def isChess(color):
            def blackTest(i):
                if color[i] < self.color_black[i]:
                    return -1
                return 0
            
            def whiteTest(i):
                if color[i] > self.color_white[i]:
                    return 1
                return 0
            
            gate = 0
            for i in range(0,3):
                gate += blackTest(i)
                gate += whiteTest(i)
            
            if gate < -2:
                return 1, 0
            elif gate > 2:
                return 0, 1
            else:
                return 0, 0
        
        white = []
        black = []
        vis = []
        for x in range(9):
            line = [[],[],[]]
            for y in range(9):
                pos = self.pos[x*9 + y]
                color = np.array([img[int(pos[0]),int(pos[1])],
                                  img[int(pos[0])+5,int(pos[1])+5],
                                  img[int(pos[0])-5,int(pos[1])-5],
                                  img[int(pos[0])-5,int(pos[1])+5],
                                  img[int(pos[0])+5,int(pos[1])-5]])
                color = np.mean(color, axis=0).tolist()
                b, w = isChess(color)
                line[0].append(b)
                line[1].append(white)
                line[2].append(2*w+b)
                
            black.append(line[0])
            white.append(line[1])
            vis.append(line[2])
            
        return black, white, vis

    def getChange(self, dot = list):
        """return dotChange, changed"""
        find = [0,0]
        find_num = 0
        for x in range(self.points):
            for y in range(self.points):
                if dot[x][y] != self.vis[x][y]:
                    find[0] = x
                    find[1] = y
                    color = dot[x][y]
                    find_num += 1
                    
        if find_num != 1:
            return find, 0
        else:
            if self.memory == find:
                if self.confidence >= self.conf_trigger:
                    # very sure
                    self.vis = dot
                    return find, color
                else:
                    # more sure
                    self.confidence += 1
                    return find, 0
            else:
                # change my mind
                self.memory = find
                self.confidence = 0
                return find, 0

if __name__ == "__main__":
    from camera import camera
    import cv2
    cam = camera(url = 'http://192.168.137.41:4747/mjpegfeed', angle = -90)
    cam.start()
    det = detect(cam)
    time.sleep(1)
    while True:
        print(det.getLoc())
