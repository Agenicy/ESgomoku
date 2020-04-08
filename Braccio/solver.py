import numpy as np
from keras.models import Sequential, load_model
from keras.activations import relu
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
    def __init__(self):
        model_file = './model.h5'
        def my_loss(y_true, y_pred):
            loss = tf.constant(0.0)
            true = tf.unstack(y_true, num=self.batch_size)
            pred = tf.unstack(y_pred, num=self.batch_size)
            for i in range(len(true)):
                t = true[i]
                p = pred[i]
                x1, y1 = self.func(t[0],t[1],t[2])
                x2, y2 = self.func(p[0],p[1],p[2])
                loss = tf.math.add(loss, tf.math.pow(tf.math.subtract(x1, x2),2) + tf.math.pow(tf.math.subtract(y1, y2),2))
            return loss
        self.my_loss = my_loss
        self.batch = 10
        if os.path.exists(model_file):
            self.model = load_model(model_file) 
        else:
            self.CreateModel()
        
        self.batch_size = 16 # change value may cause error
                    
    def func(self, theta, omega, phi, A=125.0, B=125.0, C=195.0):
        if type(theta) is int:
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
            self.GenData()
            self.Train()
    
    def GenData(self):
        print('GenData')
        col = 10000
        
        self.input = []
        self.output = []
        for i in range(col):
            # ----------------
            theta = rd(15,165)
            omega = rd(0,180)
            phi = rd(0,180)
            # ----------------
            x, y = self.func(theta, omega, phi)
            
            self.input.append([float(int(x)),float(int(y))])
            self.output.append([theta/180, omega/180, phi/180])
            
        self.input = np.array(self.input)
        self.output = np.array(self.output)
            
    
    def CreateModel(self):
        print('Create Model')
        self.model = Sequential()
        self.model.add(Dense(units=64, activation='relu', input_dim=2))
        for i in range(10):
            self.model.add(Dense(units=128, activation='relu'))
        self.model.add(Dense(units=3, activation='sigmoid'))
        
    def Compile(self):
        print('Compile')
        self.model.compile(loss=self.my_loss,
              optimizer='adam')
    
    def Train(self):
        print('Train')
        self.model.fit(self.input, self.output, epochs=20, batch_size=self.batch_size)
        self.model.save('./model.h5')
        res = self.model.predict(np.array([[-200,-10]]), batch_size=1)[0]
        t = int(res[0]*180)
        o = int(res[1]*180)
        p = int(res[2]*180)
        print(f'{t},{o},{p}, loss = {(self.func(t,o,p)[0]+200)^2 + (self.func(t,o,p)[0]+10)^2 }')
    
s = solver()
s.run()