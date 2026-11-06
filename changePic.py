from PIL import Image
import os
import numpy as np
import win32api, win32con
import readWriteFile
import getPath

'''按屏幕尺寸叠加背景图'''
def redraw_left_right(path = getPath.earthPath(), bg_path = getPath.backgroundPath(), screen_w = 1920, screen_h = 1080, earth = 1080):
    # size
    try:
        image1 = Image.open(bg_path)
        image1 = image1.resize((screen_w, screen_h), )
    except:
        image1 = Image.new("RGBA", (screen_w, screen_h))

    image2 = Image.open(path)
    image2 = image2.resize((earth, earth), )

    # image.thumbnail(size)
    bw, bh = image1.size
    lw, lh = image2.size
    # 在将小图片合并到大图片是用paste方法时要制定mask参数。这样才可以保证png图片的半透明。
    image1.paste(image2, (int((bw - lw) / 2), int((bh - lh) / 2)), mask = image2)

    newpath = getPath.finalPath()
    image1.save(newpath, "PNG")
    return newpath

def redraw_circle(path):
    ima = Image.open(path).convert("RGBA")
    # 因为是要圆形，所以需要正方形的图片
    r2 = min(ima.size)
    if ima.size[0] != ima.size[1]:
        ima = ima.resize((r2, r2), Image.ANTIALIAS)

    # 最后生成圆的半径（收缩 17px 清掉圆盘边缘白边，语义与原算法一致）
    r3 = int(r2 / 2) - 17
    r = r2 / 2  # 圆心坐标

    # numpy 矢量生成圆形蒙版：圈外 Alpha 置 0，再裁剪出 r3×r3 中心区域
    array = np.array(ima)
    yy, xx = np.ogrid[:r2, :r2]
    mask = (xx - r) ** 2 + (yy - r) ** 2 < r3 ** 2
    array[~mask] = 0
    crop = int(r - r3)
    array = array[crop:crop + r3 * 2, crop:crop + r3 * 2]

    imb = Image.fromarray(array, 'RGBA')
    new_path = getPath.earthPath()
    imb.save(new_path)
    return new_path

def changePic(earth_n = '0', bg = 'bg.jpg'):
    path = getPath.cacheWallPath()
    bg_path = getPath.backgroundFolderPath() + bg
    file_path = getPath.logFilePath()
    size = {'1': 1, '2': 0.75, '3': 0.5}
    try:
        if earth_n == '0':
            flag = readWriteFile.loadDataSet(file_path, 3)
        else:
            flag = earth_n
    except FileNotFoundError:
        flag = '1'
    except Exception as e:
        print('[changePic] 读取配置失败，回退默认「大」: {}'.format(e))
        flag = '1'
    w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    min = h if h < w else w
    max = w + h - min
    earth = int(min * size[flag])
    new_path = redraw_circle(path)
    redraw_left_right(new_path, bg_path, max, min, earth)
    # redrawBmpPaper(getPath.finalPath())

def redrawBmpPaper(imagePath):
    bmpImage = Image.open(imagePath)
    bmpImage.save(getPath.finalBmpPath(), "BMP")
    return getPath.finalBmpPath()

if __name__ == '__main__':
    changePic()