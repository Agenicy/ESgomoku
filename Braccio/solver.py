import numpy as np
from keras.models import Sequential, load_model
from keras.activations import relu
from keras.regularizers import l2
from keras.layers import Dense
from random import randint as rd
from math import cos, sin, pi
import tensorflow as tf
import os
import matplotlib.pyplot as plt

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)

"""
    input [A, B, C, X, Y]
    output [theta, omega, phi]/180
    X <- A cos(theta) + B cos(theta + omega -90) + C cos(theta + omega + phi - 180)
    Y <- A sin(theta) + B sin(theta + omega -90) + C sin(theta + omega + phi - 180)
"""
class solver():
    """def my_loss(self, y_true, y_pred):
        loss = tf.constant(0.0)
        true = tf.unstack(y_true, num=self.batch_size)
        pred = tf.unstack(y_pred, num=self.batch_size)
        for i in range(len(true)):
            t = true[i]
            p = pred[i]
            x1, y1 = self.func(t[0],t[1],t[2])
            x2, y2 = self.func(p[0],p[1],p[2])
            loss = tf.add(loss, tf.math.abs(tf.math.subtract(x1, x2)) + tf.math.abs(tf.math.subtract(y1, y2)))
        return loss"""
        
    def __init__(self):
        self.i = 0
        self.batch_size = 1024
        model_file = './model.h5'
        self.batch = 10
        if os.path.exists(model_file):
            self.model = load_model(model_file) # , custom_objects={'my_loss':self.my_loss}
        else:
            self.CreateModel()
    
    def cos(self,angle):
        """range: 0 < angle < 180"""
        angle = float(angle)
        if angle > 90:
            angle = 180 - angle
            return -1*(32400-4*pow(angle,2))/(32400+pow(angle,2))
        else:
            return (32400-4*pow(angle,2))/(32400+pow(angle,2))
    
    def sin(self, angle):
        """range: 0 < angle < 180"""
        angle = float(angle)
        return 4*angle*(180-angle)/(40500-angle*(180-angle))
    
    def func(self, theta, omega, phi, A=125.0, B=125.0, C=195.0):
        x = y = 0
        ang = theta
        x += A * self.cos(ang)
        y += A * self.sin(ang)
        ang += omega -90
        x += B * self.cos(ang)
        y += B * self.sin(ang)
        ang += phi -90
        x += C * self.cos(ang)
        y += C * self.sin(ang)
        return x, y
    
    def run(self):
        self.Compile()
        if self.input is None:
            self.GenData()
        for i in range(self.batch):
            print(f'i = {self.i}', end=' ')
            self.Train()
            self.i += 1
        self.Calc(-150,-60)
        self.Calc(-200,-60)
        self.Calc(-250,-60)
        self.Calc(-350,-60)
        self.Calc(-380,-60)
    
    
    def GenData(self):
        print('GenData')
        
        self.input = []
        self.output = []
        for theta in range(45,165,2):
            for omega in range(90,180,2):
                for phi in range(90,180,2):
                    x, y = self.func(theta, omega, phi)
                    self.input.append([x, y])
                    self.output.append([theta/180, omega/180, phi/180])
        self.input = np.array(self.input)
        self.output = np.array(self.output)
            
    
    def CreateModel(self):
        print('Create Model')
        self.model = Sequential()
        self.model.add(Dense(units=128, activation='relu', input_dim=2))
        self.model.add(Dense(units=256, activation='relu'))
        self.model.add(Dense(units=512, activation='tanh'))
        self.model.add(Dense(units=3, activation='sigmoid'))
        
    def Compile(self):
        print('Compile')
        self.model.compile(loss='mean_squared_error', optimizer='adam')
    
    def Train(self):
        print('Train')
        self.model.fit(self.input, self.output, epochs=20, batch_size=self.batch_size, verbose=0)
        self.model.save('./model.h5')
        
    def Calc(self,x_in,y_in,show = True):
        res = self.model.predict(np.array([[x_in,y_in]]), batch_size=1)[0]
        t = res[0]*180
        o = res[1]*180
        p = res[2]*180
        x, y = self.func(t,o,p)
        if show:
            print(f'target x = {x_in}, target y = {y_in}, x = {x}, y = {y}\n    solution = {t},{o},{p},\n    loss = {pow((x-x_in),2) + pow((y-y_in),2) }')
        return t, o, p

    def Varify(self):
        print('Varify.')
        loss_40 = [[],[]]
        loss_60 = [[],[]]
        loss_80 = [[],[]]
        hor = [[0]]*56
        x_range = range(-400,-120,5)
        
        def count(y, x_loss, y_loss):
            for x in x_range:
                res = self.model.predict(np.array([[x,y]]), batch_size=1)[0]
                t = res[0]*180
                o = res[1]*180
                p = res[2]*180
                x_pre, y_pre = self.func(t,o,p)
                x_loss.append(x - x_pre)
                y_loss.append(y - y_pre)
        
        count(-40, loss_40[0], loss_40[1])
        count(-60, loss_60[0], loss_60[1])
        count(-80, loss_80[0], loss_80[1])
        
        plt.plot(x_range,hor,color="black",linewidth=1)
        plt.plot(x_range,loss_40[0],label='loss_40',color="red",linewidth=2)
        plt.plot(x_range,loss_60[0],label='loss_60',color="green",linewidth=2)
        plt.plot(x_range,loss_80[0],label='loss_80',color="blue",linewidth=2)
        plt.xlabel("X")
        plt.ylabel("X error")
        plt.title("X Error")
        plt.ylim(-10,10)
        plt.legend()
        plt.show()
        
        plt.plot(x_range,hor,color="black",linewidth=1)
        plt.plot(x_range,loss_40[1],label='loss_40',color="red",linewidth=2)
        plt.plot(x_range,loss_60[1],label='loss_60',color="green",linewidth=2)
        plt.plot(x_range,loss_80[1],label='loss_80',color="blue",linewidth=2)
        plt.xlabel("X")
        plt.ylabel("Y error")
        plt.title("Y Error")
        plt.ylim(-10,10)
        plt.legend()
        plt.show()

if __name__ == "__main__":
    s = solver()
    while True:
        s.run()