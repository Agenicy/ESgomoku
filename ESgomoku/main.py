from PyQt5 import QtWidgets
from PyQt5.QtCore import  pyqtSignal
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow,QMessageBox

# img change to Qimg
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot ,QObject

from MainScreen import Ui_MainWindow
import sys
import os
import cv2

from time import sleep

sys.path.extend(['./serial', './Braccio','./camera'])
testMode = True
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
        self._timer.setInterval(1000/30) # FPS 30
        self._timer.start()
        
        self.show()
        
        # console
        self.console_old_text = []
        
        #重定向输出
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        
        # play
        self.play()
        
    def __del__(self):
        sys.stdout = sys.__stdout__
 
    def play(self):        
        import play_with_robot
        global testMode
        
        self.client = play_with_robot.Client(url = 'http://127.0.0.1:4747/mjpegfeed', debug = testMode)
        play_with_robot.run(self.client, testMode)
        
 
    def playMusic(self):
        txt = 'True' if self.actionMusic_On.isChecked() else 'False'
        print(f'Music: {txt}')
 
    def normalOutputWritten(self, text):          
        if text == '--Board--':
            self.label_Board_Output.setText('')
            sys.stdout = EmittingStream(textWritten=self.chessOutputWritten)
        else:
            self.console_output.appendPlainText(text.replace('\n',''))
        
    def chessOutputWritten(self, text):            
        if text[0:2] == '---':
            sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        else:
            self.label_Board_Output.setText(self.label_Board_Output.text() + text)
        
    def exit(self):
        raise Exception()
        self._timer.stop()
        sys.exit(app.exec_())
                
    @pyqtSlot()
    def _queryFrame(self):
        if not self.client is None:
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
