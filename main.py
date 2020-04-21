import sys
sys.path.extend(['./serial-port', './Braccio'])
from usb import usb
from solver import solver
from time import sleep

s = solver(model_file = './Braccio/model.h5')
def MakeData(x,y,z=0,catch=0,time=20):
    t, o, p = s.Calc(x, y)
    return [time, 90, t, o, p, 90, 40 + catch*30 ]

u = usb()
port = 'COM4'
u.AddClient(port, 9600, show = True)
u.Run()

while True:
    word = input(f'Enter Data, use dot(".") to seprate...').replace('\n','').split('.')
    u.UserSend(data = MakeData(int(word[0]),int(word[1])), port = port)