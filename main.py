import sys
sys.path.extend(['./serial', './Braccio'])
from usb import usb
from solver import solver
from time import sleep
from math import sqrt, atan, pi

# 常數修正項 ------------------------------------------------------
port = 'COM5'
x_offset = 150 # 棋盤中點偏差值 (絕對值)
y_offset = 0 # 棋盤高度偏差值 (向上為正)
block_length = 23.7 # 棋盤格子長度
block_width = 23
waiting_action = [30, 90, 64, 178, 179, 85, 40] # 落子後的待機位置
waiting_action_chess = [30, 90, 64, 178, 179, 85, 65] # 落子後的待機位置
y_150 = 100 # 150.0時相對於基準面的高度
y_400 = 145 # 400.0時相對於基準面的高度
y_board = -93 # 落子的高度
y_board_chess = -40 # 夾棋子的高度

def y_function(x, y):
    return y - (x - (-150)) * (y_400 - y_150) / ((-400) - (-150)) # Δy - Δx * 修正函數

def MakeData(x, y,ang = 90,catch=0,time=20, vert = 85):
    """將距離xy轉換為指令"""
    y = y_function(x, y)
    t, o, p = s.Calc(x, y)
    if t != 0:
        return [time, ang, t, o, p, vert, 40 + catch*25 ]
    else:
        return False

def LocToRec(loc = list):
    """
    ### 將座標點轉換為機械手臂指令
    
    - 手臂的左下方為[0, 0] 右下方為[0, 9]，前方為x pos
    """
    x, y = loc[0], loc[1]
    x = -(x - 5) # 以中央為 0
    x , y = int(x * block_width), int(y * block_length) # 轉換為mm
    y = x_offset + y # 轉換為距離x偏移量 + loc y 位移 
    
    r = sqrt(pow(x,2)+pow(y,2)) # 平面半徑
    if x == 0:
        ang = 90
    else:
        ang = atan(y/x)*180/pi
        if ang < 0:
            ang += 180
    
    return r, ang # 弳度轉弧度
    

# -----------------------------------------------------------------

s = solver()
u = usb()
u.AddClient(port, 9600, show = True)
u.Run()


u.UserSend(data = waiting_action, port = port)
while True:
    # 夾棋子 --------------------------------------------------------------------
    prepare = MakeData(x = -150, y= y_board_chess ,ang = 90, catch = 0)
    u.UserSend(data = prepare, port = port)
    u.Wait(port=port)
    sleep(1)
    prepare[0], prepare[6] = 10, 65
    u.UserSend(data = prepare, port = port)
    u.Wait(port=port)
    prepare[0], prepare[3]= 30, 145
    u.UserSend(data = prepare, port = port)
    u.Wait(port=port)
    u.UserSend(data = MakeData(x = -150, y= 0 ,ang = 90, catch = 1), port = port)
    u.Wait(port=port)
    # --------------------------------------------------------------------------
    
    word = input(f'Enter Data, use dot(".") to seprate...').replace('\n','').split('.')
    pos = [int(word[1]),int(word[0])]
    print(pos)
    r, ang = LocToRec(pos)
    print(r)
    print(ang)
    
    serial = MakeData(x = -r, y= y_board ,ang = ang, catch = 1)
    serial2 = MakeData(x = -r, y= y_board ,ang = ang, catch = 0)
    end_action = MakeData(x = -r, y= 0 ,ang = ang, catch = 0)
        
    if serial != False:
        u.UserSend(data = serial, port = port)
        u.Wait(port=port)
        u.UserSend(data = serial2, port = port)
        u.Wait(port=port)
        u.UserSend(data = end_action, port = port)
        u.Wait(port=port)
    u.UserSend(data = waiting_action, port = port)