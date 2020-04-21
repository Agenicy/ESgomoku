import numpy as np

from math import cos, sin, pi
import os
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
"""
    input [A, B, C, X, Y]
    output [theta, omega, phi]/180
    X <- A cos(theta) + B cos(theta + omega -90) + C cos(theta + omega + phi - 180)
    Y <- A sin(theta) + B sin(theta + omega -90) + C sin(theta + omega + phi - 180)
"""

class solver():
    
    def func(self, theta, omega, phi, A=125.0, B=125.0, C=195.0):
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
    
      
    def GenData(self):
        print('GenData')
        im = Image.new("RGBA", (1000, 1000), (0,0,0,0)) # x , y range
        draw = ImageDraw.Draw( im ) # painter color
        
        def DrawColor(x, y, R, G, B):
            x, y, R, G, B = int(x), int(y), int(R), int(G), int(B)
            draw.point([x,y],fill=(R, G, B, 255))
            draw.point([x+1,y],fill=(R, G, B, 255))
            draw.point([x-1,y],fill=(R, G, B, 255))
            draw.point([x,y+1],fill=(R, G, B, 255))
            draw.point([x,y-1],fill=(R, G, B, 255))
        
        for theta in range(15,165):
            for omega in range(90,180):
                for phi in range(90,180):
                    x, y = self.func(theta, omega, phi)
                    x = int(x+500)
                    y = int(y+500)
                    DrawColor(x, y, theta, omega, phi)
        DrawColor(500, 500, 0, 0, 0)
        DrawColor(505, 500, 255, 0, 0)
        DrawColor(500, 505, 0, 255, 0)
        
        im.save( "fileout.png")
        
                
    def Calc(self,x_in,y_in,show = True):
        im = Image.open("fileout.png")
        
        x = x_in + 500
        y = y_in + 500
        
        t, o, p, _ = im.getpixel((x,y))
        if _ == 0:
            print('No Solution')
            return 0, 0, 0
        x, y = self.func(t,o,p)
        
        if show:
            print(f'target x = {x_in}, target y = {y_in}, x = {x}, y = {y}\n    solution = {t},{o},{p},\n    loss = {pow((x-x_in),2) + pow((y-y_in),2) }')
        return t, o, p

if __name__ == "__main__":
    s = solver()
    select = input('input mode:')
    if select == '0':
        s.GenData()
    else:
        select = select.split(' ')
        s.Calc(-120, -100)
        s.Calc(-400, -100)