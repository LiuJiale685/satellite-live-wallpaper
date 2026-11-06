import win32api, win32con, win32gui
import getPath

'''换壁纸'''
# def setWallPaper(imagepath=getPath.finalBmpPath(), i = '10', j = '0'):
def setWallPaper(imagepath=getPath.finalPath(), i = '10', j = '0'):
  print(imagepath)
  keyex = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
  win32api.RegSetValueEx(keyex, "WallpaperStyle", 0, win32con.REG_SZ, i)
  win32api.RegSetValueEx(keyex, "TileWallpaper", 0, win32con.REG_SZ, j)
  win32api.RegCloseKey(keyex)
  win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, imagepath, win32con.SPIF_SENDWININICHANGE)

if __name__ == '__main__':
  setWallPaper()