
class detect():
    def __init__(self, wpx=500, hpx=500, points=13):
        super().__init__()
        self.w = wpx
        self.h = hpx
        self.points = points

    def analyze(self, dst):
        """取得當前棋盤所有落子位置"""
        while True:
            dotList = self.getDot(img)
            dotChange, changed = self.getChange(dotList)
            if changed:
                return self.dotListToString(dotChange)


if __name__ == "__main__":
    from camera import camera
    import cv2
    cam = camera()
    img, dst = cam.getDst()
    cv2.imshow('result', dst)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
