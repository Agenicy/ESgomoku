from PyQt5 import QtWidgets
from PyQt5.QtCore import  pyqtSignal
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow,QMessageBox
import sys

# img change to Qimg
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot ,QObject

from MainScreen import Ui_MainWindow
import os
import cv2


from pygame import mixer

import threading

mixer.init()
mixer.music.set_volume(1.0)

sys.path.extend(['./serial', './Braccio','./camera'])
testMode = False
#from camera import camera
#cam = camera(url = 'http://127.0.0.1:4747/mjpegfeed', angle = 0, debug = True)
#cam.start()

class Path():
    @staticmethod
    def PicturePath(filename):
        return './GUI/Resources/Picture/' + str(filename)

class EmittingStream(QObject):
        textWritten = pyqtSignal(str)
        def write(self, text):
            self.textWritten.emit(str(text))

class BGM(threading.Thread):
    def __init__(self):
        super().__init__()
        pass
    
    def run(self):
        try:
            while not mixer.music.get_busy():
                mixer.music.load('./Resources/Music/start.mp3')
                mixer.music.play()
        except Exception:
            pass

bgm = BGM()

class PyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(PyMainWindow, self).__init__()
        
        # init
        self.client = None
        
        # ui
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('./GUI/Resources/Picture/icon.png'))
        self.actionExit_2.triggered.connect(self.exit)
        self.actionNewGame_2.triggered.connect(self.play)
        self.actionMusic_On.triggered.connect(self.playMusic)
        
        # camera
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._queryFrame)
        self._timer.setInterval(10)
        self._timer.start()
        
        self.show()
        
        # console
        self.console_old_text = []
        
        #重定向输出
        self.switch = False # 切換輸出欄位
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        
        # play
        self.threads = None
        print("Press NewGame...")
        # self.play()
        
        bgm.start()
        
    def playMusic(self):
        pass
        
    def __del__(self):
        sys.stdout = sys.__stdout__
 
    def play(self):        
        import play_with_robot
        global testMode
        
        if not testMode:
            client = play_with_robot.Client(url = 'http://192.168.137.236:4747/mjpegfeed', angle = 0, debug = testMode)
            #! threading
            # play_with_robot.run(self.client, testMode)
            self.threads = play_with_robot.Play_With_Robot(client, testMode = testMode)
            self.client = self.threads.client
            
            self.threads.start()
            
            # music
            while mixer.music.get_busy():
                pass
            if self.actionMusic_On.isChecked():
                mixer.music.load('./Resources/Music/start.m4a')
                mixer.music.play()
        else:
            self.client = play_with_robot.Human()
        
    def normalOutputWritten(self, text):         
        if not self.switch:
            if text.replace('\n','') == '--Board--':
                self.switch = True
                self.label_Board_Output.setText('')
            else:
                if text[0:8] == '[Detect]' or True:
                    self.console_output.appendPlainText(text.replace('\n',''))
        else:   
            # board     
            if text.replace('\n','') == '---':
                self.switch = False
            else:
                self.label_Board_Output.setText(self.label_Board_Output.text() + text)
        
    def exit(self):
        raise Exception()
        self._timer.stop()
        
        #! thread
        self.threads.join()
        
        sys.exit(app.exec_())
                
    @pyqtSlot()
    def _queryFrame(self):
        if not self.client is None:
            if not self.client.det.imsLock:
                img, dst = self.client.det.getDst()
                img = cv2.resize(img, (int(self.label_img_pict.width()), int(self.label_img_pict.height())))
                image = QtGui.QImage(img.data, img.shape[1], img.shape[0], 3* img.shape[1], QtGui.QImage.Format_RGB888).rgbSwapped()
                self.label_img_pict.setPixmap(QtGui.QPixmap.fromImage(image))
                
                dst = cv2.resize(dst, (int(self.label_dst_pict.width()), int(self.label_dst_pict.height())))
                image2 = QtGui.QImage(dst.data, dst.shape[1], dst.shape[0], 3* img.shape[1], QtGui.QImage.Format_RGB888).rgbSwapped()
                self.label_dst_pict.setPixmap(QtGui.QPixmap.fromImage(image2))
                    
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    pass
        else:
            self.label_img_pict.setText("<font color='black'>No Camera.</font>")
            pass
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = PyMainWindow()
    ui.show()
        
    from braccio_player import init
    
    #! port setting is at braccio_player.Global
    # init(testMode = testMode) # braccio init
    
    sys.exit(app.exec_())
