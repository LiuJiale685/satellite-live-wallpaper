import requests
import os
import time
import getPath

'''判断路径是否存在'''
def checkDir(download_path):
  mkdirlambda = lambda x: os.makedirs(x) if not os.path.exists(x) else True  # 目录是否存在,不存在则创建
  mkdirlambda(download_path)

'''云图下载源'''
PICTURE_URL = 'http://img.nsmc.org.cn/CLOUDIMAGE/FY4A/MTCC/FY4A_DISK.JPG'
# 缓存新鲜度阈值（秒）：该时间段内已下载过则直接复用，避免重复全量拉取
CACHE_FRESH_SECONDS = 600

'''爬取壁纸'''
def crawlWallpaper(download_path = getPath.downloadFolderPath()):
  checkDir(download_path)
  cache_path = getPath.cacheWallPath()
  # 缓存较新（如最近 10 分钟内下载过）则跳过下载
  if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) < CACHE_FRESH_SECONDS:
    print('[getPic] 缓存较新，跳过下载')
    return True
  for attempt in range(3):  # 最多重试 3 次
    try:
      res = requests.get(PICTURE_URL, timeout=15)  # 连接/读取各 15s
      res.raise_for_status()  # 4xx/5xx 抛异常
      with open(cache_path, 'wb') as f:
        f.write(res.content)
      print('[getPic] 云图下载成功')
      return True
    except (requests.RequestException, OSError) as e:
      print('[getPic] 下载失败(第{}次): {}'.format(attempt + 1, e))
      if attempt < 2:
        time.sleep(3)
  raise RuntimeError('卫星云图下载失败')

if __name__ == '__main__':
  crawlWallpaper()
