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
        
        self.setupUi(self)
        self.actionExit_2.triggered.connect(self.exit)
        self.actionNewGame_2.triggered.connect(self.play)
        self.actionMusic_On.triggered.connect(self.playMusic)
        
        self.show()
        
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._queryFrame)
        self._timer.setInterval(1000/30) # FPS 30
        self._timer.start()
        
        self.console_old_text = []
        
        #重定向输出
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        
        self.c = None
         
    def __del__(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
 
    def play(self):        
        import play_with_robot
        global testMode
        
        self.c = play_with_robot.Client(url = 'http://127.0.0.1:4747/mjpegfeed', debug = testMode)
        play_with_robot.run(c, testMode)
        
 
    def playMusic(self):
        txt = 'True' if self.actionMusic_On.isChecked() else 'False'
        print(f'Music: {txt}')
 
    def normalOutputWritten(self, text):
        '''header = "<html><head/><body><p style='line-height:0px'>"
        end = '</p></body></html>'
        self.console_old_text.append(text)
        if len(self.console_old_text) > 35:
            self.console_old_text = self.console_old_text[1:len(self.console_old_text)]
        sb = ""
        for var in self.console_old_text:
            sb +=  var + "<br/>"'''
            
        self.console_output.appendPlainText(text.replace('\n',''))
        
    def exit(self):
        raise Exception()
        self._timer.stop()
        sys.exit(app.exec_())
                
    @pyqtSlot()
    def _queryFrame(self):
        if not self.c is None:
            img, dst = self.c.cam.getDst()
            image = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
            self.label_img_pict.setPixmap(QtGui.QPixmap.fromImage(image))
            
            image2 = QtGui.QImage(dst.data, dst.shape[1], dst.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
            self.label_dst_pict.setPixmap(QtGui.QPixmap.fromImage(image2))
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                pass
        else:
            pass
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = PyMainWindow()
    ui.show()
        
    from braccio_player import init
    
    #! port setting is at braccio_player.Global
    init(testMode = testMode) # braccio init
    
    sys.exit(app.exec_())
