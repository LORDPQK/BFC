# -*- coding: utf-8 -*-
import math
import sys
import matplotlib.pyplot
import numpy as np
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import tkinter as tk
import matplotlib.colors as mcolors
from openpyxl import Workbook
from PIL import Image, ImageTk

# ================== 全局配置 ==================
THEME_NAME = "litera"  # 可更换主题：cosmo/superhero/morph
FONT_FAMILY = ("Microsoft YaHei", 10)
TITLE_FONT = ("Microsoft YaHei", 14, "bold")

filds = ['文件保存路径', "待计算方程式", "遗忘百分比（*10%）", 
        "遗忘矩阵大小", "单次功耗", "遗忘曲线方程", "噪声水平"]
forD = "n"
global time, powerCount, power, tau, noise, forget_function 
address = ""

# ================== 现代化界面组件 ==================
class ModernWindow(ttk.Window):
    def __init__(self):
        super().__init__(themename=THEME_NAME)
        self.geometry("1000x800")
        self.title("遗忘可视化计算软件")
        self.init_ui()
        
    def init_ui(self):
        # 主容器
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # 标题区
        header = ttk.Frame(main_frame)
        ttk.Label(header, text="遗忘可视化计算软件", 
                 font=TITLE_FONT, bootstyle=PRIMARY).pack(pady=15)
        header.pack(fill=X)

        # 输入表单
        form_frame = ttk.Labelframe(main_frame, text="参数配置", bootstyle=INFO)
        form_frame.pack(padx=10, pady=10, fill=X)
        
        self.entries = []
        for idx, field in enumerate(filds):
            row = ttk.Frame(form_frame)
            row.pack(fill=X, pady=8)
            
            ttk.Label(row, text=f"{field}：", width=18, anchor=E).pack(side=LEFT)
            entry = ttk.Entry(row)
            entry.pack(side=RIGHT, fill=X, expand=True)
            self.entries.append(entry)

        # 功能按钮区
        btn_frame = ttk.Frame(main_frame)
        ttk.Button(btn_frame, text="路径选择", command=self.select_path,
                  bootstyle=(OUTLINE, SECONDARY)).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="开始计算", command=lambda: main(self.entries),
                  bootstyle=SUCCESS).pack(side=LEFT, padx=5)
        btn_frame.pack(pady=15)

        # 状态栏
        self.status = ttk.Label(main_frame, text="就绪", bootstyle=(INFO, INVERSE))
        self.status.pack(side=BOTTOM, fill=X)

    def select_path(self):
        path_ = filedialog.askdirectory()
        self.entries[0].delete(0, END)
        self.entries[0].insert(0, path_)

# ================== 功能模块保持不变 ==================
def helpWin(info):
    win = ttk.Toplevel(title="帮助文档")
    ttk.Label(win, text="帮助说明", font=TITLE_FONT).pack(pady=10)
    text = ttk.Text(win, width=80, height=20)
    text.insert(END, info)
    text.pack(padx=10)
    ttk.Button(win, text="关闭", command=win.destroy).pack(pady=10)


def Preference():
    preference = tk.Tk()
    preference.title("Preferences")
    preferenceTitle = tk.Label(preference, text='偏好设置', font=('PingFang', 20), height=4).pack()
    rowForD = tk.Frame(preference)
    lForD = tk.Label(rowForD, text='是否给出运算过程：').pack(side=tk.LEFT)
    rForD1 = tk.Radiobutton(rowForD, text='需要运算过程', variable=var, value='需要运算过程',
                            command=(lambda: ForD("y"))).pack(side=tk.LEFT)
    rForD2 = tk.Radiobutton(rowForD, text='不需要运算过程', variable=var, value='不需要运算过程',
                            command=(lambda: ForD("n"))).pack(side=tk.LEFT)
    rowForD.pack(fill=tk.X)
    tk.Button(preference, text='关闭', command=preference.destroy, padx=5, pady=5, relief=tk.RAISED, cursor='hand2',
              font='bold').pack(side=tk.BOTTOM)
    # tk.Button(win, text='OK', command=win.destroy, cursor='hand2').pack()
    # preference.protocol('WM_DELETE_WINDOW', preference.quit)
    preference.mainloop()

def ForD(x):
    global forD
    forD = x

# ================== 数学计算核心模块保持不变 ==================
def create_function(expression):
    def f(x): return eval(expression.replace('^', '**').replace('x', str(x)))
    return f

def check(matrix):
    for i_check in range(0, large):
        for k_check in range(0, large):
            if matrix[i_check][k_check] < 0:
                matrix[i_check][k_check] = 0
    return matrix

def flip(matrix):
    flipMatrix = np.zeros([large, large])
    for i in range(0, large):
        for k in range(0, large):
            flipMatrix[i][k] = matrix[k][large - 1 - i]
    return flipMatrix

def draw(matrix, address, time):
    matrix = flip(check(matrix))[::-1]
    image_array = np.asarray(matrix).reshape(large, large)
    colors = [(1, 1, 1), (135/255, 28/255, 22/255)]
    cmap = mcolors.LinearSegmentedColormap.from_list("CustomPurple", colors, N=256)
    norm = mcolors.Normalize(vmin=np.min(matrix), vmax=np.max(matrix))
    matplotlib.pyplot.imshow(image_array, cmap=cmap, norm=norm, interpolation='None')
    addressIn = address + "/T=" + str(time) + ".png"
    matplotlib.pyplot.gca().invert_yaxis()
    matplotlib.pyplot.savefig(addressIn, dpi=600, format='png')

def integer(ans):
    return int(ans + 1)

def plus(function):
    global powerCount
    D = np.zeros([large, large])
    for i in range(0, large):
        y = function(i)
        if i != 0:
            for Plus_morePositionWork in range(integer(min(y, Plus_yBefore)) - 1, integer(max(y, Plus_yBefore))):
                try:
                    if Plus_morePositionWork >= 0:
                        D[i][Plus_morePositionWork] = 1
                except IndexError:
                    break
        Plus_yBefore = y
        try:
            if y >= 0:
                D[i][y] = 1
        except IndexError:
            continue
    for i in range(0, large):
        for j in range(0, large):
            if D[i][j] == 1:
                powerCount += 1
    return D

def find(matrix,forget_function):
    check(matrix)
    normalized_matrix = matrix / np.linalg.norm(matrix)
    scaled_matrix = np.clip(normalized_matrix, 0, 1)
    min_val = scaled_matrix.min()
    max_val = scaled_matrix.max()
    scaled_matrix = (scaled_matrix - min_val) / (max_val - min_val)
    answerBox = []
    for x in range(0, large):
        for y in range(0, large):
            if scaled_matrix[x][y] >= 0.5:
                answerBox.append([x, y])
    outPosition(answerBox,forget_function)

# ================== 优化后的输出模块 ==================
def outPosition(box,forget_function):
    wb = Workbook()
    ws = wb.active
    ws.title = "计算结果"
    ws.append(["result ID", "X", "Y"])
    
    out = "计算结果为：\n"
    for i in range(len(box)):
        x_val = box[i][0]
        y_val = box[i][-1]
        out += f"x = {x_val}, y = {y_val}\n"
        ws.append([i+1, x_val, y_val])

 
    # 计算衰减时间
    single_spike = 1
    time = 0
    while single_spike > single_spike * noise:
        single_spike -= forget_function(time)
        time += 0.01

    # Excel美化输出
    ws.append([])
    ws.append(["总功耗", power * powerCount])
    ws.append(["计算时长", time])
    wb.save("计算结果.xlsx")
    
    messagebox.showinfo("计算结果", 
        # f"{out}总功耗={power*powerCount:.6f}\n结果已保存至计算结果.xlsx")
        f"{out}总功耗={power*powerCount:.6f}\n计算时长={time:.4f}\n结果已保存至计算结果.xlsx")

# ================== 主逻辑保持不变 ==================
def main(entries):
    global large, A, B, C, D, powerCount, power, tau, noise, tau2
    info = [e.get() for e in entries]
    address = info[0]
    questionList = info[1].split(";")
    
    forget_function = create_function(info[5])
    functionList = [create_function(i.replace("log", "math.log")
        .replace("sin", "math.sin")
        .replace("cos", "math.cos")
        .replace("e", "math.e")) for i in questionList]
    
    time = int(info[2])
    power = float(info[4])
    noise = float(info[6])/100
    input_large = int(info[3])
    
    powerCount = 0
    large = input_large
    C = np.zeros([large, large])
    D = np.zeros([large, large])
    
    for f in functionList:
        C += plus(f)
    
    timeCount = 0
    # 输出初始状态（T=0）
    draw(C, address, timeCount)
    
    # 按照衰减次数循环，每次衰减后都输出一张图
    for inTime in range(0, time):
        timeCount += 0.01
        loss = forget_function(timeCount-0.01) - forget_function(timeCount)
        # print(loss)
        C -= loss
        
        # 每次衰减后都输出图片
        draw(C, address, timeCount)
    find(C,forget_function)

# ================== 程序入口 ==================
if __name__ == "__main__":
    root = ModernWindow()
    var = ttk.StringVar(value='n')
    
    # 构建菜单
    menubar = ttk.Menu(root)
    config_menu = ttk.Menu(menubar, tearoff=0)
    config_menu.add_command(label="偏好设置", command=Preference)
    menubar.add_cascade(menu=config_menu, label="设置")
    
    help_menu = ttk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="使用帮助", command=lambda: helpWin(
        "计算参数输入说明：\n1. 文件保存路径：选择结果输出目录\n2. 方程式格式：使用Python数学表达式语法\n3. 遗忘曲线支持指数函数格式（如0.5*exp(-x/10)）"))
    help_menu.add_command(label="关于", command=lambda: messagebox.showinfo("关于", "PKU SmileLab 2025"))
    menubar.add_cascade(menu=help_menu, label="帮助")
    
    root.config(menu=menubar)
    root.mainloop()