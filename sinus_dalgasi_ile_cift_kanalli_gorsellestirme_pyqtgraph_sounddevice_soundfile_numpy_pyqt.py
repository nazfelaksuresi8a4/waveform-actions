from PyQt5.QtCore import*
from PyQt5.QtGui import*
from PyQt5.QtWidgets import*
import sys as _s 
import sounddevice as sd
import soundfile as sf 
import pyqtgraph as pg 
import numpy as np 
import wave

current_matrix_1 = None
current_matrix_2 = None

class MainThread(QObject):
    def __init__(self,matrix,frame,samplerate,channels):
        super().__init__()
        self.matrix = matrix
        self.framesize = frame
        self.channels = channels
        self.samplerate = samplerate

        self.start = 0
        self.end = 0
        self.length = len(matrix)

        self.flag = True
    
    def runf(self):
        pass

    def callback(self,outdata,status,time,frames):
        global current_matrix_1,current_matrix_2
        if self.flag == True:
            if status:
                pass

            if self.end == self.length - 1:
                self.flag = False

            else:
                self.end = self.start + self.framesize

                outdata[:] = self.matrix[self.start:self.end]
                current_matrix_1 = outdata[:,0]
                current_matrix_2 = outdata[:,1]

                self.start = self.end
        else:
            pass


    def finished_callback(self):
        pass
    
    def start_stream(self):
        with sd.OutputStream(samplerate=self.samplerate,
                             blocksize=self.framesize,
                             channels=self.channels,
                             callback=self.callback,
                             finished_callback=self.finished_callback) as self.SdOutputStream:
            self.SdOutputStream.start()
            while self.flag:
                #print(current_matrix)
                print()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        #data-science
        self.matrix,self.samplerate = sf.read(r"C:\Users\alper\Downloads\MAXILLA (SLOWED)-slowedandreverbstudio.wav")
        self.sound_channels = wave.open(r"C:\Users\alper\Downloads\MAXILLA (SLOWED)-slowedandreverbstudio.wav").getnchannels()

        #variables
        self.flag = True
        self.samplerate = self.samplerate
        self.channels = self.sound_channels 
        self.framesize = 480
        self.nframes = wave.open(r"C:\Users\alper\Downloads\MAXILLA (SLOWED)-slowedandreverbstudio.wav").getnframes()
        self.t = 0

        #widgets
        button = QPushButton('Başlat')
        self.plotWidget = pg.PlotWidget(background='black')
        self.line1 = self.plotWidget.plot(pen='g')
        self.line2 = self.plotWidget.plot(pen='b')

        main_layout.addWidget(self.plotWidget)
        main_layout.addWidget(button)

        #signal-slot
        button.clicked.connect(self.ThreadHandler)
        
        self.setCentralWidget(main_widget) 

    def ThreadHandler(self):
        self.Thread = QThread(self)
        self.ThradClass = MainThread(self.matrix,self.framesize,self.samplerate,self.channels)
        self.ThradClass.moveToThread(self.Thread)

        self.Thread.started.connect(self.ThradClass.runf)

        self.callbackTimer = QTimer(self)
        self.callbackTimer.timeout.connect(self.plotFunction)
        self.callbackTimer.start(50)

        self.Thread.started.connect(self.ThradClass.start_stream)
        self.Thread.start()
    
    def plotFunction(self):
        if current_matrix_2 is not None and current_matrix_1 is not None:
            if self.flag == True:

                self.line1.setData(np.sin(np.linspace(-2,24,len(current_matrix_1))+np.abs(current_matrix_1)+self.t))
                self.line2.setData(np.sin(np.linspace(-2,24,len(current_matrix_2))+np.abs(current_matrix_2)+self.t))
                self.t += 1
                
            else:
                self.callbackTimer.stop()
                

if __name__ == "__main__":
    sp = QApplication(_s.argv)
    sw = MainWindow()
    sw.show()
    _s.exit(sp.exec_())

