import tkinter as tk  # 使用Tkinter前需要先导入
from tkinter import ttk, StringVar # 导入ttk模块，因为下拉菜单控件在ttk中
import tkinter.filedialog
import readWriteFile
import tkinter.messagebox #弹窗库
import os
import shutil
import _thread
import win32api, win32con
from PIL import ImageTk, Image
import random
import satelliteLiveWallpaper
import getPath

class showGUI:
    def ret_win(self):
        '''选择文件'''
        def choose_file(bg_path = getPath.backgroundPath()):
            select_file_name = tk.filedialog.askopenfilename(title='选择文件')  # 选择文件
            extension_name = os.path.splitext(select_file_name)[1]
            if extension_name == '.jpg' or extension_name == '.JPG':
                t_bg_t.set(select_file_name)
                shutil.copy(select_file_name, bg_path)
            else:
                tkinter.messagebox.showinfo('提示', '必须选择jpg图片')
                choose_file()

        # 点击保存事件
        def submit():
            path = getPath.logFilePath()
            text = t_w_t.get() + '\n' + t_h_t.get() + '\n' + str(cmb.current() + 1) + '\n' + t_bg_t.get()
            readWriteFile.write_file(path, text)
            _thread.start_new_thread(satelliteLiveWallpaper.myRun, ())  # 后台线程执行，避免界面卡顿
            tkinter.messagebox.showinfo('提示', '已保存，正在后台更换壁纸')

        # 点击随机事件
        def myRandom():
            bg_n = random.randint(1, 3)
            earth_n = random.randint(1, 3)
            earth_n = str(earth_n)
            bg = 'bg' + str(bg_n) + '.jpg'
            _thread.start_new_thread(satelliteLiveWallpaper.myRun, (earth_n, bg))  # 后台线程执行


        # 第1步，实例化object，建立窗口window
        window = tk.Tk()


        # 第2步，给窗口的可视化起名字
        window.title('SLW初始化')
        window.minsize(200, 180)  # 最小尺寸
        window.maxsize(200, 180)  # 最大尺寸

        # 背景, 第3步，设定窗口的大小(宽 * 长)
        canvas = tk.Canvas(window, width=200, height=180, bd=0, highlightthickness=0)
        imgpath = getPath.tkBgPath()
        img = Image.open(imgpath)
        photo = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, image=photo)
        canvas.pack()

        # 标签
        l_w = tk.Label(window, text="分辨率宽:", bg="#00F5FF")
        l_h = tk.Label(window, text="分辨率高:", bg="#00F5FF")
        l_e = tk.Label(window, text="地球尺寸:", bg="#00F5FF")

        # 输入框
        t_w_t = StringVar()
        t_h_t = StringVar()
        t_bg_t = StringVar()
        t_w = tk.Entry(window, width=16, textvariable = t_w_t)
        t_h = tk.Entry(window, width=16, textvariable = t_h_t)
        t_bg = tk.Entry(window,width=16, textvariable = t_bg_t)

        t_w_t.set(win32api.GetSystemMetrics(win32con.SM_CXSCREEN))
        t_h_t.set(win32api.GetSystemMetrics(win32con.SM_CYSCREEN))



        #下拉框
        cmb = ttk.Combobox(window, width=13)
        #设置下拉框内容
        cmb['value'] = ('大', '中', '小')
        # 设置默认值，即默认下拉框中的内容
        cmb.current(0)



        # 按钮
        b_bg = tk.Button(window, width=7, text="背景图", command=choose_file, bg="#00F5FF")
        b_save = tk.Button(window, text=" 保 存 ", command=submit, bg="#00F5FF")
        b_random = tk.Button(window, text="随机生成", command=myRandom, bg="#00F5FF")


        # 设定位置
        def point():
            l_w.place(x=5, y=10)
            t_w.place(x=70, y=10)
            l_h.place(x=5, y=40)
            t_h.place(x=70, y=40)
            l_e.place(x=5, y=70)
            cmb.place(x=70, y=70)
            b_bg.place(x=5, y=95)
            t_bg.place(x=70, y=100)
            b_random.place(x=5, y=140)
            b_save.place(x=140, y=140)

        point()

        # 初始化完成
        # 第6步，主窗口循环显示
        # 注意，loop因为是循环的意思，window.mainloop就会让window不断的刷新，如果没有mainloop,就是一个静态的window,传入进去的值就不会有循环，mainloop就相当于一个很大的while循环，有个while，每点击一次就会更新一次，所以我们必须要有循环
        # 所有的窗口文件都必须有类似的mainloop函数，mainloop是窗口文件的关键的关键。
        window.mainloop()

showGUI().ret_win()