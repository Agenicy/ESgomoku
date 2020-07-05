import cv2
import numpy as np
import time
import threading

class camera(threading.Thread):
    def __init__(self, url='http://127.0.0.1:4747/mjpegfeed', angle = -90):
        super().__init__()
        # 開啟網路攝影機
        self.cam = cv2.VideoCapture(url)
        
        self.angle = angle

        self.kernel_size = 5
        
        self.pict_size = 700
        self.w = 480
        self.h = 640
        self.border = 50  # resize border px
        self.BoardArea = 0 # founded board area

        self.point = []
        for i in range(3, 12):
            for j in range(3, 12):
                self.point.append((i*self.border, j*self.border))
        self.M = None
        self.pict = []

    # 定义旋转rotate函数
    def rotate(self, img, angle, center=None, scale=1.0):
        # 获取图像尺寸
        (h, w) = img.shape[:2]

        # 若未指定旋转中心，则将图像中心设为旋转中心
        if center is None:
            center = (w / 2, h / 2)

        # 执行旋转
        M = cv2.getRotationMatrix2D(center, angle, scale)
        rotated = cv2.warpAffine(img, M, (w, h))

        # 返回旋转后的图像
        return rotated

    def close(self):
        """ 關閉視窗"""
        self.cam.release()
        cv2.destroyAllWindows()

    def getImg(self):
        """ 從攝影機取得圖片"""
        ret, img = self.cam.read()
        img = self.rotate(img, self.angle)
        #! camera 區域
        img = img[:, 80:-80]
        img = cv2.resize(img, (self.pict_size, self.pict_size))
        return img

    def detect_border(self, blur_gray):
        """ 給定圖片，回傳邊緣偵測後的版本"""
        low_threshold = 50
        high_threshold = 150
        edges = cv2.Canny(blur_gray, low_threshold, high_threshold)
        return edges

    def resize(self, img):
        # 將圖片轉為灰階
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur_gray = cv2.GaussianBlur(
            gray, (self.kernel_size, self.kernel_size), 0)
        try:
            edges = self.detect_border(blur_gray)
        except:
            pass

        contours, hierarchy = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if len(contours) != 0:
            try:
                # draw in blue the contours that were founded
                #cv2.drawContours(img, contours, -1, 255, 3)

                # find the biggest countour (c) by the area
                self.board_area = max(contours, key=cv2.contourArea)
                corner = cv2.approxPolyDP(
                    self.board_area, 0.1*cv2.arcLength(self.board_area, True), True)

                corner = np.float32(corner.tolist())
                to = np.float32([[self.border, self.border], [self.border, self.pict_size-self.border], [
                                self.pict_size-self.border, self.pict_size-self.border], [self.pict_size-self.border, self.border]])

                if self.BoardArea*0.9 <= cv2.contourArea(corner):
                    # 取得變形公式
                    self.M = cv2.getPerspectiveTransform(corner, to)
                    self.BoardArea = cv2.contourArea(corner)
                    self.board_corner = self.board_area
            except:
                pass

    def run(self):
        while True:
            try:
                img = self.getImg()

                #cv2.imshow('result', img)
                
                self.resize(img)
                
                while self.M is None:
                    img = self.getImg()

                    cv2.imshow('result', img)
                    self.resize(img)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                # 透視變形
                dst = cv2.warpPerspective(
                    img, self.M, (self.pict_size, self.pict_size))
                """
                # draw points
                for point in [(5*self.border, 5*self.border), (9*self.border, 9*self.border), (5*self.border, 9*self.border), (9*self.border, 5*self.border), (7*self.border, 7*self.border)]:
                    cv2.circle(dst, point, 8, (0, 255, 255), thickness=-1)
                for point in self.point:
                    cv2.circle(dst, point, 5, (0, 0, 255), thickness=-1)
                """

                cv2.drawContours(img, self.board_area, -1, (255, 0, 0), 3)
                try:
                    cv2.drawContours(img, self.board_corner, -1, (0, 255, 0), 3)
                except:
                    pass
                #cv2.imshow('result', img)
                #cv2.imshow('resize', dst)
                
                self.pict = [img, dst]

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except Exception as e:
                print(e)

    def getDst(self):
        return self.pict[0], self.pict[1]
        

if __name__ == "__main__":
    cam = camera(url = 'http://192.168.137.41:4747/mjpegfeed', angle = 0)
    cam.start()