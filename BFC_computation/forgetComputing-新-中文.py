import math
import sys
import matplotlib.pyplot
import numpy as np
import tkinter as tk
import sys
from tkinter.filedialog import askdirectory
from tkinter.messagebox import *
from tkinter import filedialog
from tkinter import messagebox
import matplotlib.colors as mcolors



filds = ['文件保存路径', "待计算方程式", "遗忘百分比（*10%）", "遗忘矩阵大小", "单次功耗", "衰减时间常数", "噪声水平"]
forD = "n"
global time, powerCount, power, tau, noise
address = ""


def helpWin(info):
    win = tk.Toplevel()
    tk.Label(win, text="帮助：", font=('PingFang', 20), height=4).pack()
    row = tk.Frame(win)
    row.pack(fill=tk.X)
    info = info.split("\n")
    for i in info:
        row = tk.Frame(win)
        tk.Label(row, text=i).pack(side=tk.LEFT)
        row.pack(fill=tk.X)
    tk.Button(win, text='OK', command=win.destroy, cursor='hand2').pack()
    win.protocol('WM_DELETE_WINDOW', win.quit)
    win.focus_set()
    win.grab_set()
    win.mainloop()


def selectPath():
    path_ = askdirectory()
    path.set(path_)
    entry_text.set(path_)


def makeForm(root, fields):
    entries = []
    i = 0
    for field in fields:
        row = tk.Frame(root)
        labelQ = tk.Label(row, text=field)
        if i != 0:
            ent = tk.Entry(row)
        else:
            ent = tk.Entry(row, textvariable=entry_text)
        row.pack(fill=tk.X)
        labelQ.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries.append(ent)
        i += 1
    return entries


def fetch(entries):
    info = []
    for entry in entries:
        A = entry.get()
        info.append(A)
    return info


def show(errmsg):
    win = tk.Toplevel()
    tk.Label(win, text=errmsg).pack()
    tk.Button(win, text='OK', command=win.destroy, cursor='hand2').pack()
    win.protocol('WM_DELETE_WINDOW', win.quit)
    win.focus_set()
    win.grab_set()
    win.mainloop()


def callBack():
    if askyesno('Verify', 'Do you really want to quit?'):
        showwarning('Yes', '正在终止......', command=root.quit())
    else:
        showinfo('No', 'Quit has been cancelled')


def on_closing():
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()


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


# 定义一个函数，将文本表达式转换为计算机函数
def create_function(expression):
    def f(x):
        return eval(expression.replace('^', '**').replace('x', str(x)))

    return f


####################################################################################
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
    # print(matrix)  ####
    # 定义紫色到白色的颜色映射
    image_array = np.asarray(matrix).reshape(large, large)
    colors = [(1, 1, 1), (135/255, 28/255, 22/255)]  # 紫色到白色的渐变
    cmap = mcolors.LinearSegmentedColormap.from_list("CustomPurple", colors, N=256)
    norm = mcolors.Normalize(vmin=np.min(matrix), vmax=np.max(matrix))

    # 绘制图像
    matplotlib.pyplot.imshow(image_array, cmap=cmap, norm=norm, interpolation='None')
    # matplotlib.pyplot.show()
    addressIn = address + "/T=" + str(time) + ".png"
    matplotlib.pyplot.gca().invert_yaxis()
    matplotlib.pyplot.savefig(addressIn, dpi=600, format='png')


def f(x):
    return 0.5 * x * x


def f2(x):
    return -x + 10


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


def forgetTime(matrix, time):
    for i in range(0, time):
        matrix -= 0.1
    return matrix


def find(matrix):
    check(matrix)
    normalized_matrix = matrix / np.linalg.norm(matrix)
    # 矩阵元素限制在0和1之间
    scaled_matrix = np.clip(normalized_matrix, 0, 1)

    # 将最大和最小元素缩放为1和0，其余元素等比例缩放
    min_val = scaled_matrix.min()
    max_val = scaled_matrix.max()
    scaled_matrix = (scaled_matrix - min_val) / (max_val - min_val)

    answerBox = []
    for x in range(0, large):
        for y in range(0, large):
            if scaled_matrix[x][y] >= 0.5:
                answerBox.append([x, y])
    # print(scaled_matrix)
    outPosition(answerBox)


def calculate_discretization_error(function, large):
    """计算离散化误差"""
    quantization_errors = []
    for i in range(large):
        y_continuous = function(i)
        y_discrete = int(y_continuous + 0.5)
        quantization_error = abs(y_continuous - y_discrete)
        quantization_errors.append(quantization_error)
    
    # 计算RMS误差
    rms_error = math.sqrt(sum(e*e for e in quantization_errors) / len(quantization_errors))
    max_error = max(quantization_errors)
    
    # 计算相对误差
    y_values = [function(i) for i in range(large)]
    y_range = max(y_values) - min(y_values)
    relative_error = rms_error / y_range if y_range > 0 else 0
    
    return {
        'rms_error': rms_error,
        'max_error': max_error,
        'relative_error': relative_error
    }

def outPosition(box):
    out = "计算结果为：\n"
    for i in range(0, len(box)):
        out += "x = " + str(box[i][0]) + ", y = " + str(box[i][-1]) + "\n"
    
    # 添加误差分析
    if 'functionList' in globals():
        out += "\n离散化误差分析：\n"
        for idx, func in enumerate(functionList):
            error_stats = calculate_discretization_error(func, large)
            out += f"方程{idx+1}: RMS误差={error_stats['rms_error']:.4f}, "
            out += f"最大误差={error_stats['max_error']:.4f}, "
            out += f"相对误差={error_stats['relative_error']:.4f}\n"
    
    if tau2 == 0:
        f0 = 1
        target = f0 * noise
        def f(x):
            return math.exp(-x / tau)
        x = 0.0
        step = 0.001  # 步长，可以根据需要调整
        while f(x) > target:
            x += step
        countTime = x
        show(out+ "总功耗=" + f"{power*powerCount:.6f}" + "\n" + f"计算时长={countTime:.4f}")
    else:
        f0 = 2
        target = f0 * noise
        def f(x):
            return math.exp(-x / tau) + math.exp(-x / tau2)
        x = 0.0
        step = 0.001  # 步长，可以根据需要调整
        while f(x) > target:
            x += step
        countTime = x
        show(out+ "总功耗=" + f"{power*powerCount:.6f}" + "\n" + f"计算时长={countTime:.4f}")




def main(entries):
    global large, A, B, C, D, powerCount, power, tau, noise, tau2
    info = fetch(entries)
    address = info[0]
    questionList = info[1].split(";")
    talall = info[5].split(";")
    functionList = []
    for i in questionList:
        i = i.replace("log", "math.log").replace("sin", "math.sin").replace("cos", "math.cos").replace("e", "math.e")
        function = create_function(i)
        functionList.append(function)
    time = int(info[2])
    power = float(info[4])
    tau = float(talall[0])
    tau2 = 0
    if len(talall) > 1:
        tau2 = float(talall[1])
    noise = float(info[6])/100
    # 遗忘参数的录入与检验
    input_large = int(info[3])
    # if info[3] == "":
    #     line = True
    # else:
    #     line = False
    #     parameter = info[3].split(";")
    #     try:
    #         y_0 = float(parameter[0])
    #         c_1 = float(parameter[1])
    #         t_1 = float(parameter[2])
    #         decline = math.exp(-100/t_1)
    #     except ValueError:
    #         show("输入格式有误")
    #         sys.exit()
    #     except IndexError:
    #         show("参数缺失")
    #         sys.exit()
    powerCount = 0
    large = input_large
    # A = np.zeros([large, large])
    # B = np.eye(large)
    C = np.zeros([large, large])
    D = np.zeros([large, large])
    for f in functionList:
        C += plus(f)
    timeCount = 0
    for inTime in range(0, time):
        if forD == "y":
            draw(C, address, timeCount)
        timeCount += 1
        # if line:
        C -= 0.1
        # else:
        #     C *= decline
    draw(C, address, timeCount)
    # C = forgetTime(C + D, time)
    # draw(C, address)
    find(C)


root = tk.Tk()
entry_text = tk.StringVar()
var = tk.StringVar()
root.title("遗忘可视化计算软件")
labelTitle = tk.Label(text='遗忘可视化计算软件', font=('PingFang', 20), height=4).pack()
ents = makeForm(root, filds)
path = tk.StringVar()
tk.Button(root, text="数据文件路径选择", command=selectPath, relief=tk.RAISED, cursor='hand2').pack(padx=5)
tk.Button(text='运行', command=(lambda: main(ents)), padx=5, pady=5, relief=tk.RAISED, cursor='hand2',
          font='bold').pack()
labelCopyRight = tk.Label(text='Copyright © 2023 Smile Lab, Peking University. All rights reserved.', font=('PingFang', 12), height=2).pack(
    side=tk.BOTTOM)
menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='偏好设置', command=(lambda: Preference()), accelerator='Ctrl+I')
aboutmenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='About', menu=aboutmenu)
aboutmenu.add_command(label='关于我们', command=(lambda: show("Copyright © 2025 Smile Lab, Peking University. All rights reserved.")),
                      accelerator='Ctrl+A')
aboutmenu.add_command(label='帮助', command=(lambda: helpWin("计算参数输入\n用户可在此使用半角字符输入参与计算的函数表达式，如:\n"
                                                             "一次函数“x+1”、二次函数“2*x^2-3*x-4”、三角函数“sin(0.5*x+1)”、e指数函数“e^(0.1*x)”、对数函数“log(x+1)”等。\n"
                                                             "用户一次可输入多个函数，不同函数之间可使用“;”号分割。\n\n"
                                                             "遗忘时间\n"
                                                             "遗忘时间为使用<遗忘运算>方法计算的时间参数，应为整数。\n\n"
                                                             "运算过程\n在系统偏好设置中可以选择是否需要软件输出运算过程,系统默认选择为<不需要运算过程>。")),
                      accelerator='Ctrl+H')
root.config(menu=menubar)
root.protocol('WM_DELETE_WINDOW', on_closing)
root.mainloop()
