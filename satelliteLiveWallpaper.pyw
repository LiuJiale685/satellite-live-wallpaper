import getPic
import changePic
import setWallpaper
import getPath

#defute earth_n = '0', bg = 'bg.jpg'
def myRun(earth_n = '0', bg = 'bg.jpg'):
    try:
        getPic.crawlWallpaper()
        changePic.changePic(earth_n, bg)
        setWallpaper.setWallPaper(getPath.finalPath())
    except Exception as e:
        print('[myRun] 壁纸刷新失败: {}'.format(e))

if __name__ == '__main__':
    myRun()
