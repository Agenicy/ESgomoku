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
import copy
import play_with_robot
        
mixer.init()
mixer.music.set_volume(1.0)

sys.path.extend(['./serial', './Braccio','./camera'])
testMode = False

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
        mixer.Channel(0).set_volume(0.1)
        mixer.Channel(0).play(mixer.Sound('./Resources/Music/start.ogg'), -1)

mixer.init()
bgm = BGM()

#TODO init here
url = 'http://192.168.137.178:4747/mjpegfeed'

class PyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(PyMainWindow, self).__init__()
        
            
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
        
        # console
        self.console_old_text = []
        
        if not testMode:
            self.client = play_with_robot.Client(url = url, angle = 0, debug = testMode, init = True) 
            self.client.det.create()
        
        from time import sleep
        sleep(2) 
        # play
        self.threads = None
        print("Press NewGame...")
        
        self.actionMusic_On.setChecked(True)
        bgm.start()
        mixer.Channel(1).play(mixer.Sound('./Resources/ROBOT_SE/ready.ogg'))
        
        self.show()
        
        #重定向输出
        self.switch = False # 切換輸出板
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        
        
    def playMusic(self):
        if self.actionMusic_On.isChecked():
            self.play_se('music_on')
        else:
            self.play_se('music_off')
            
    def play_se(self, filename):
        if self.actionMusic_On.isChecked():
            mixer.Channel(1).play(mixer.Sound(f'./Resources/ROBOT_SE/{filename}.ogg'))
        
    def __del__(self):
        sys.stdout = sys.__stdout__
 
    def play(self):        
        self.play_se('game_start')
        global testMode
        
        if not testMode:
                  
            #! threading
            # play_with_robot.run(self.client, testMode)
            who_first = 1
            #* BGM
            if who_first == 1:
                self.play_se('ai_first')
            elif who_first == 0:
                self.play_se('human_first')
            
            self.threads = play_with_robot.Play_With_Robot(parent = self, who_first = who_first, client = self.client , testMode = testMode)
            
            
            self.threads.start()
            
        else:
            self.client = play_with_robot.Human()
        
    def normalOutputWritten(self, text):         
        if not self.switch:
            if text.replace('\n','') == '--Board--':
                self.switch = True
                self.label_Board_Output.setText('')
            else:
                self.console_output.appendPlainText(text.replace('\n',''))
                #if text[0:8] == '[Detect]':
                #    self.console_output.appendPlainText(text.replace('\n',''))
        else:   
            # board     
            if text.replace('\n','') == '---':
                self.switch = False
            else:
                self.label_Board_Output.setText(self.label_Board_Output.text() + text)
    
    def end_game(self, winner):
        print('game end')
        sys.stdout = sys.__stdout__
        
        self.threads.join()        
        #* BGM
        if self.threads.winner == 0:
            self.play_se('win')
        elif self.threads.winner == 1:
            self.play_se('lose')
        elif self.threads.winner == -1:
            self.play_se('even')
        self.threads = None
    
    def exit(self):
        self._timer.stop()
        
        try:
            self.client.cam.close()
        except AttributeError as e:
            print(e)
        
        #! thread
        if not self.threads is None:
            self.threads.join()
        
        self.close()
                
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
