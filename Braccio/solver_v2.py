import numpy as np
from keras.models import Sequential, load_model
from keras.activations import relu
from keras.regularizers import l2
from keras.layers import Dense, Dropout
from random import randint as rd
from math import cos, sin, pi
import tensorflow as tf
import os
import matplotlib.pyplot as plt
import threading

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)

"""
    input [A, B, C, X, Y]
    output [theta, omega, phi]/180
    X <- A cos(theta) + B cos(theta + omega -90) + C cos(theta + omega + phi - 180)
    Y <- A sin(theta) + B sin(theta + omega -90) + C sin(theta + omega + phi - 180)
"""
class job(threading.Thread):
    def __init__(self, func):
        threading.Thread.__init__(self)
        self.run = func
    
class solver():
    def __init__(self):
        self.i = 0
        self.batch_size = 128
        model_file = ['./model_theta.h5','./model_omega.h5','./model_phi.h5']
        self.batch = 10
        if os.path.exists(model_file[0]) and os.path.exists(model_file[1]) and os.path.exists(model_file[2]):
            self.model_theta = load_model(model_file[0])
            self.model_omega = load_model(model_file[1])
            self.model_phi = load_model(model_file[2])
        else:
            self.CreateModel()
        
    def func(self, theta, omega, phi, A=125.0, B=125.0, C=195.0):
        if type(theta) is tf.Tensor:
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
        else:
            x = y = 0
            ang = theta
            angr = ang / 180 * pi
            x += A * cos(angr)
            y += A * sin(angr)
            ang += omega -90
            angr = ang / 180 * pi
            x += B * cos(angr)
            y += B * sin(angr)
            ang += phi -90
            angr = ang / 180 * pi
            x += C * cos(angr)
            y += C * sin(angr)
            return x, y
    
    def run(self):
        self.Compile()
        try:
            print(len(self.input))
        except AttributeError:
            self.GenData()
            
        for i in range(self.batch):
            print(f'i = {self.i}')
            self.Train()
            self.i += 1
        self.model_theta.save('./model_theta.h5')
        self.model_omega.save('./model_omega.h5')
        self.model_phi.save('./model_phi.h5')
        
        self.Calc(-150,-60)
        self.Calc(-200,-60)
        self.Calc(-250,-60)
        self.Calc(-350,-60)
        self.Calc(-380,-60)
    
    
    def GenData(self):
        print('GenData')
        def getPlate(i):
            temp = [0]*180
            temp[i] = 1
            return temp
        
        self.input = []
        self.theta = []
        self.omega = []
        self.phi = []
        self.plate = [0]*180
        for theta in range(45,165,5):
            for omega in range(90,180,5):
                for phi in range(90,180,5):
                    x, y = self.func(theta, omega, phi)
                    self.input.append([x,y])
                    self.theta.append(getPlate(theta))
                    self.omega.append(getPlate(omega))
                    self.phi.append(getPlate(phi))
                    
        self.input = np.array(self.input)
        self.theta = np.array(self.theta)
        self.omega = np.array(self.omega)
        self.phi = np.array(self.phi)
            
    
    def CreateModel(self):
        print('Create Model')
        def Basic_Model():
            model = Sequential()
            model.add(Dense(units=16, activation='relu', input_dim=2))
            model.add(Dense(units=180, activation='softmax'))
            return model
        
        self.model_theta = Basic_Model()
        self.model_omega = Basic_Model()
        self.model_phi = Basic_Model()
        
    def Compile(self):
        print('Compile')
        self.model_theta.compile(loss='categorical_crossentropy', optimizer='adam',metrics=['accuracy'])
        self.model_omega.compile(loss='categorical_crossentropy', optimizer='adam',metrics=['accuracy'])
        self.model_phi.compile(loss='categorical_crossentropy', optimizer='adam',metrics=['accuracy'])
    
    def Train(self):
        print('Train')
        job(self.model_theta.fit(self.input, self.theta, epochs=10, batch_size=self.batch_size, verbose=1))
        job(self.model_omega.fit(self.input, self.omega, epochs=10, batch_size=self.batch_size, verbose=1))
        job(self.model_phi.fit(self.input, self.phi, epochs=10, batch_size=self.batch_size, verbose=1))
        
                
    def Calc(self,x_in,y_in,show = True):
        
        t = np.argmax(self.model_theta.predict(np.array([[x_in,y_in]]), batch_size=1), axis=1)[0]
        o = np.argmax(self.model_omega.predict(np.array([[x_in,y_in]]), batch_size=1), axis=1)[0]
        p = np.argmax(self.model_phi.predict(np.array([[x_in,y_in]]), batch_size=1), axis=1)[0]
        
        x, y = self.func(t,o,p)
        if show:
            print(f'target x = {x_in}, target y = {y_in}, x = {x}, y = {y}\n    solution = {t},{o},{p},\n    loss = {pow((x-x_in),2) + pow((y-y_in),2) }')
        return t, o, p

if __name__ == "__main__":
    s = solver()
    while True:
        s.run()