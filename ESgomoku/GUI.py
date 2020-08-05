import tkinter as tk

from play_with_robot import run

# 自訂函數
def hello():
    run()

window = tk.Tk()
window.title('Hello World')
window.geometry("300x100+250+150")

# 建立按鈕
button = tk.Button(window,          # 按鈕所在視窗
                   text = 'Hello',  # 顯示文字
                   command = hello) # 按下按鈕所執行的函數

# 以預設方式排版按鈕
button.pack()

window.mainloop()