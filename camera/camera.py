import cv2
import numpy as np
  

class camera():
    def __init__(self, url):
        super().__init__()
        # 開啟網路攝影機
        self.cam = cv2.VideoCapture(url)

        self.kernel_size = 5

        self.pict_size = 500
        self.w = 480
        self.h = 640
        self.border = 50  # resize border px
        self.M = None
        self.color_sensitive = 20
        

        self.point = []
        for i in range(1, 10):
            for j in range(1, 10):
                self.point.append((i*self.border, j*self.border))
               

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
        img = self.rotate(img, -90)
        #! camera 區域
        img = img[:, 100:-100]
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

        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        
        if len(contours) >=1:
            
            # find the biggest countour (c) by the area
            self.board_area = max(contours, key=cv2.contourArea)
            corner = cv2.approxPolyDP(
                self.board_area, 0.1*cv2.arcLength(self.board_area, True), True)

            corner = np.float32(corner.tolist())
            
            to = np.float32([[self.border, self.border], [self.border, self.pict_size-self.border], [
                            self.pict_size-self.border, self.pict_size-self.border], [self.pict_size-self.border, self.border]])

            if len(corner) == 4:
                # 取得變形公式
                self.M = cv2.getPerspectiveTransform(corner, to)
    
    def get_board(self, img):
        gray = img
        
        blur_gray = cv2.GaussianBlur(gray, (self.kernel_size, self.kernel_size), 0)
        edges = self.detect_border(blur_gray)
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(gray, contours, -1, (0, 0, 0), 2)
        
        cv2.imshow('b',gray)
        contours, hierarchy = cv2.findContours(gray,  cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        
        if len(contours) >=1:
            
            # find the biggest countour (c) by the area
            self.board_area = max(contours, key=cv2.contourArea)
            corner = cv2.approxPolyDP(
                self.board_area, 0.1*cv2.arcLength(self.board_area, True), True)

            corner = np.float32(corner.tolist())
            
            to = np.float32([[self.border, self.border], [self.border, self.pict_size-self.border], [
                            self.pict_size-self.border, self.pict_size-self.border], [self.pict_size-self.border, self.border]])

            if len(corner) > 4:
                # 取得變形公式
                self.M = cv2.getPerspectiveTransform(corner, to)
               
    def run(self):
        
        least, most = [], []
        for i in range(20):
            img = self.getImg()
            while self.M is None:
                self.resize(img)
            
            dst = cv2.warpPerspective(img, self.M, (self.pict_size, self.pict_size))
            blur = cv2.blur(dst, (64, 64))
            least.append(min(blur[0].tolist()))
            most.append(max(blur[0].tolist()))
            
            
        least = np.array(min(least))
        most = np.array(max(most))
        least[:] = least[:] - self.color_sensitive
        most[:] = most[:] + self.color_sensitive
        
        while True:
            img = self.getImg()
            mask = cv2.inRange(img, least, most)
            mask[:] = 255 - mask[:]
            
            try:
                self.get_board(mask)
                
                # 透視變形
                dst = cv2.warpPerspective(img, self.M, (self.pict_size, self.pict_size))
                
                """
                # draw points
                for point in [(3*self.border,3*self.border),(7*self.border,7*self.border),(3*self.border,7*self.border),(7*self.border,3*self.border),(5*self.border,5*self.border)]:
                    cv2.circle(dst, point, 8, (0, 255, 255), thickness=-1)
                for point in self.point:
                    cv2.circle(dst, point, 5, (0, 0, 255), thickness=-1)
                """

                cv2.drawContours(img, self.board_area, -1, (255, 0, 0), 3)
                
                cv2.imshow('result', img)
                cv2.imshow('resize', dst)
                
            except Exception as e:
                print(e)
        
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def getDst(self):
        img = self.getImg()
            
        self.resize(img)
        try:
            # 透視變形
            dst = cv2.warpPerspective(img, self.M, (self.pict_size, self.pict_size))
            
            cv2.drawContours(img, self.board_area, -1, (255, 0, 0), 3)
            return img, dst
        except:
            pass

if __name__ == "__main__":
    cam = camera(url='http://127.0.0.1:4747/mjpegfeed')
    cam.run()
    cam.close()
