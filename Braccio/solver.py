import numpy as np
from keras.models import Sequential, load_model
from keras.activations import relu
from keras.regularizers import l2
from keras.layers import Dense
from random import randint as rd
from math import cos, sin, pi
import tensorflow as tf
import os
"""
    input [A, B, C, X, Y]
    output [theta, omega, phi]/180
    X <- A cos(theta) + B cos(theta + omega -90) + C cos(theta + omega + phi - 180)
    Y <- A sin(theta) + B sin(theta + omega -90) + C sin(theta + omega + phi - 180)
"""
class solver():
    def my_loss(self, y_true, y_pred):
        loss = tf.constant(0.0)
        true = tf.unstack(y_true, num=self.batch_size)
        pred = tf.unstack(y_pred, num=self.batch_size)
        for i in range(len(true)):
            t = true[i]
            p = pred[i]
            x1, y1 = self.func(t[0],t[1],t[2])
            x2, y2 = self.func(p[0],p[1],p[2])
            loss = tf.add(loss, tf.math.abs(tf.math.subtract(x1, x2)) + tf.math.abs(tf.math.subtract(y1, y2)))
        return loss
        
    def __init__(self):
        self.i = 0
        self.batch_size = 16 # change value may cause error
        model_file = './model.h5'
        self.batch = 10
        if os.path.exists(model_file):
            self.model = load_model(model_file, custom_objects={'my_loss':self.my_loss}) 
        else:
            self.CreateModel()
        
                    
    def func(self, theta, omega, phi, A=125.0, B=125.0, C=195.0):
        if type(theta) is float or type(theta) is int:
            x = y = 0
            ang = theta
            angr = (ang/180)*pi
            x += A * cos(angr)
            y += A * sin(angr)
            ang += omega -90
            angr = (ang/180)*pi
            x += B * cos(angr)
            y += B * sin(angr)
            ang += phi -90
            angr = (ang/180)*pi
            x += C * cos(angr)
            y += C * sin(angr)
            return x, y
        elif type(theta) is tf.Tensor:
            x = y = tf.constant(0.0)
            ang = theta
            angr = (ang/tf.constant(180.0))*tf.constant(pi)
            x += tf.constant(A) * tf.math.cos(angr)
            y += tf.constant(A) * tf.math.sin(angr)
            ang += omega -tf.constant(90.0)
            angr = (ang/tf.constant(180.0))*tf.constant(pi)
            x += tf.constant(B) * tf.math.cos(angr)
            y += tf.constant(B) * tf.math.sin(angr)
            ang += phi -tf.constant(90.0)
            angr = (ang/tf.constant(180.0))*tf.constant(pi)
            x += tf.constant(C) * tf.math.cos(angr)
            y += tf.constant(C) * tf.math.sin(angr)
            return x, y
    
    def run(self):
        self.Compile()
        for i in range(self.batch):
            print(f'i = {self.i}')
            self.GenData()
            self.Train()
            self.i += 1
    
    def GenData(self):
        print('GenData')
        
        self.input = []
        self.output = []
        """
        col = 10000
        for i in range(col):
            # ----------------
            theta = float(rd(15,165))
            omega = float(rd(0,180))
            phi = float(rd(0,180))
            # ----------------
            x, y = self.func(theta, omega, phi)
            
            self.input.append([float(int(x)),float(int(y))])
            self.output.append([theta, omega, phi])
            """
        for theta in range(45,165,rd(5,9)):
            for omega in range(91,180,rd(5,9)):
                for phi in range(91,180,rd(5,9)):
                    x, y = self.func(theta, omega, phi)
                    self.input.append([float(int(x)),float(int(y))])
                    self.output.append([theta, omega, phi])
        self.input = np.array(self.input)
        self.output = np.array(self.output)
            
    
    def CreateModel(self):
        print('Create Model')
        self.model = Sequential()
        self.model.add(Dense(units=128, activation='relu', input_dim=2))
        for i in range(40):
            self.model.add(Dense(units=512, activation='relu'))
        self.model.add(Dense(units=3, activation='linear'))
        
    def Compile(self):
        print('Compile')
        self.model.compile(loss='mean_squared_error', optimizer='adam')
    
    def Train(self):
        print('Train')
        self.model.fit(self.input, self.output, epochs=5, batch_size=self.batch_size)
        self.model.save('./model.h5')
        self.Test(-200,-10)
        self.Test(-200,60)
        self.Test(-240,0)
        self.Test(-150,-70)
        
    
    def Test(self,x_in,y_in):
        res = self.model.predict(np.array([[x_in,y_in]]), batch_size=1)[0]
        t = float(int(res[0]))
        o = float(int(res[1]))
        p = float(int(res[2]))
        x, y = self.func(t,o,p)
        print(f'target x = {x_in}, target y = {y_in},\n    solution = {t},{o},{p}, x = {x}, y = {y}, \n    loss = {pow((x-x_in),2) + pow((y-y_in),2) }')
    
s = solver()
s.Test(-200,-10)
s.Test(-200,60)
s.Test(-240,0)
s.Test(-150,-70)