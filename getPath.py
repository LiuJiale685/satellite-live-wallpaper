import sys
import os
import glob

all_path = os.path.abspath(sys.argv[0])  # 当前模块/脚本路径（框架下为 slw_frontend.py）
all_base_path = os.path.dirname(all_path)

def myReplace(path_str):
    return path_str.replace('/','\\')

def backgroundPath():
    return myReplace(all_base_path + '/background/bg.jpg')

def backgroundFolderPath():
    return myReplace(all_base_path + '/background/')

def backgroundList():
    '''所有背景图绝对路径列表（仅 jpg/jpeg），支持后续扩展任意文件名'''
    folder = all_base_path + '/background'
    return [myReplace(p) for p in sorted(glob.glob(os.path.join(folder, '*.jpg')) + glob.glob(os.path.join(folder, '*.jpeg')))]

def finalPath():
    return myReplace(all_base_path + '/pic/final.png')

def finalBmpPath():
    return myReplace(all_base_path + '/pic/final.bmp')

def downloadFolderPath():
    return myReplace(all_base_path + '/pic')

def earthPath():
    return myReplace(all_base_path + '/pic/earth.png')

def cacheWallPath():
    return myReplace(all_base_path + '/pic/cache_wallpaper.jpg')

def logFilePath():
    return myReplace(all_base_path + '/log/slw.ini')

def tkBgPath():
    return myReplace(all_base_path + '/tk_bg/tk_bg1.jpg')

if __name__ == '__main__':
    print(backgroundPath())
    print(finalPath())
    print(downloadFolderPath())
    print(earthPath())
    print(cacheWallPath())
    print(logFilePath())
    print(finalBmpPath())