import cv2
import time
import numpy as np
class detect():
    def __init__(self, points=9, outline = 3):
        super().__init__()
        
        unitW = 50
        unitH = 50
        self.color_black = [100,100,100]
        self.color_white = [180,220,230]
        
        self.points = points
        self.pos = []
        for x in range(outline, points + outline):
            for y in range(outline, points + outline):
                self.pos.append([unitW * x, unitH * y])

    def analyze(self, dst):
        """取得當前棋盤所有落子位置"""
        black, white, dotList = self.getDot(dst)
        dotChange, changed = self.getChange(dotList)
        """
        if changed:
            return self.dotListToString(dotChange)
        """
        print(np.array(dotList))
        
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

    def getChange(self, dot):
        

if __name__ == "__main__":
    from camera import camera
    import cv2
    cam = camera()
    det = detect()
    while True:
        im, d = cam.getDst()
        d = cv2.blur(d,(8, 8))
        cv2.imshow('result', d)
        det.analyze(d)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        nowTime = time.time()
        
        while time.time() - nowTime < 0.1:
            im, d = cam.getDst()
        
    cv2.destroyAllWindows()
