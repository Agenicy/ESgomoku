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

class solver():
    def my_loss(self, y_true, y_pred):
        loss = tf.constant(0.0)
        x1, y1 = self.func(y_true[:][0],y_true[:][1],y_true[:][2])
        x2, y2 = self.func(y_pred[:][0],y_pred[:][1],y_pred[:][2])
        x_avg = tf.compat.v1.keras.backend.mean(x2)
        loss += tf.math.pow(tf.math.subtract(x1, x2),2) - tf.math.pow(tf.math.subtract(x2, x_avg),2) + tf.math.pow(tf.math.subtract(y1, y2),2)
        return loss
        
    def __init__(self):        
        model_file = ['./model_theta.h5','./model_omega.h5','./model_phi.h5']
        
        self.model_theta = load_model(model_file[0])
        self.model_omega = load_model(model_file[1])
        self.model_phi = load_model(model_file[2])
    
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
    
    
    def Varify(self):
        print('Varify.')
        loss_0 = [[],[]]
        loss_40 = [[],[]]
        loss_60 = [[],[]]
        loss_80 = [[],[]]
        loss_100 = [[],[]]
        loss_120 = [[],[]]
        x_range = range(-400,-120)
        hor = [[0]]*len(x_range)
            
        def count(y, x_loss, y_loss):
            for x in x_range:
                t = np.argmax(self.model_theta.predict(np.array([[x,y]]), batch_size=1), axis=1)[0]
                o = np.argmax(self.model_omega.predict(np.array([[x,y]]), batch_size=1), axis=1)[0]
                p = np.argmax(self.model_phi.predict(np.array([[x,y]]), batch_size=1), axis=1)[0]
                x_pre, y_pre = self.func(t,o,p)
                x_loss.append(x - x_pre)
                y_loss.append(y - y_pre)
        
        count(0, loss_0[0], loss_0[1])
        count(-40, loss_40[0], loss_40[1])
        count(-60, loss_60[0], loss_60[1])
        count(-80, loss_80[0], loss_80[1])
        count(-100, loss_100[0], loss_100[1])
        count(-120, loss_120[0], loss_120[1])
        
        plt.figure('error',figsize=(18,9))
        plt.xlabel("X")
        plt.ylabel("X error")
        plt.title("X Error")
        plt.subplot(1,2,1)
        
        plt.plot(x_range,hor,color="black",linewidth=1)
       
        plt.plot(x_range,loss_0[0],label='loss_0',color="orange",linewidth=1)
        plt.plot(x_range,loss_40[0],label='loss_40',color="red",linewidth=4)
        plt.plot(x_range,loss_60[0],label='loss_60',color="green",linewidth=3)
        plt.plot(x_range,loss_80[0],label='loss_80',color="blue",linewidth=2)
        plt.plot(x_range,loss_100[0],label='loss_100',color="purple",linewidth=1)
        plt.plot(x_range,loss_120[0],label='loss_120',color="black",linewidth=1)
        
        plt.ylim(-250,250)
        plt.legend()
        
        plt.subplot(1,2,2)
        plt.xlabel("X")
        plt.ylabel("Y error")
        plt.title("Y Error")
        plt.plot(x_range,hor,color="black",linewidth=1)
        plt.plot(x_range,loss_0[1],label='loss_0',color="orange",linewidth=2)
        plt.plot(x_range,loss_40[1],label='loss_40',color="red",linewidth=2)
        plt.plot(x_range,loss_60[1],label='loss_60',color="green",linewidth=2)
        plt.plot(x_range,loss_80[1],label='loss_80',color="blue",linewidth=2)
        plt.plot(x_range,loss_100[1],label='loss_100',color="purple",linewidth=2)
        plt.plot(x_range,loss_120[1],label='loss_120',color="black",linewidth=2)
        
        plt.ylim(-200,200)
        plt.legend()
        
        plt.show()

if __name__ == "__main__":
    s = solver()
    s.Varify()