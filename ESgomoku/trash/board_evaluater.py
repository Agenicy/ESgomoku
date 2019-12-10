# discarded
"""train a model to evaluate the winning rate"""

import numpy as np
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D

import os
import glob

from game_engine import const
from raw_dataset.see_raw_data import Analyze

class TrainEvaler():
    npyPath = r'raw_dataset/data.npy'
    dataset = []
    x_train, y_train = []

    def __init__(self, init_model=None):
        self.CreateModel(32)
        self.TrainModel()
        
    def PrepareDataset(self):
        #read from npy files
        if not self.LoadDataset(self.npyPath):
            #no npy file, create one

            np.save(self.npyPath,self.dataset)

    def LoadDataset(self, path):
        if os.path.exists(path):
            #read
            return True
        else:
            return False
        

    def CreateModel(self,times):
        self.model = Sequential()
        self.model.add(Conv2D(filters = 32, kernel_size = (5,5) , activation='relu' , input_dim = (3, const.default_height , const.default_width)))
        self.model.add(Conv2D(filters = 64, kernel_size = (5,5) , activation='relu'))
        self.model.add(Conv2D(filters = 128, kernel_size = (5,5) , activation='relu'))
        self.model.add(Dropout(0.25))

        self.model.add(Flatten())
        self.model.add(Dense(256, activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(2, activation='softmax')) # winning rate

        self.model.compile(optimizer='Adam', loss='mean_squared_error', metrics=['accuracy'])


    def TrainModel(self):
        self.model.fit(self.x_train, self.y_train, epochs=20, batch_size=128)
        self.score = self.model.evaluate(self.x_test, self.y_test, batch_size=128)

   