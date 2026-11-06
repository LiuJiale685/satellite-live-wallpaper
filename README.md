# 卫星实时动态壁纸（Satellite Live Wallpaper）

将「风云四号」静止气象卫星 FY-4A 的实时全球云图下载到本地，**圆形裁剪**后叠加到自定义背景图上，并设置为 Windows 桌面壁纸。每次运行即可刷出最新云图。

## 功能特性

- **实时真值云图**：数据源为国家卫星气象中心（NSMC）FY-4A 静止卫星公开接口，非模拟数据
- **圆形抠图**：像素级距离判定裁出地球圆盘，并将半径收缩 17px 以清掉圆盘边缘白边
- **三档地球尺寸**：大（1.0x）/ 中（0.75x）/ 小（0.5x），相对屏幕**短边**计算，横竖屏均完整可见
- **自定义背景**：手动选择 JPG 背景，或随机从 4 张背景中抽取
- **分辨率自适应**：运行时动态读取当前屏幕分辨率，无需人工配置

## 环境要求

- Windows（依赖注册表与 Win32 API 设置壁纸）
- Python 3.x
- 依赖库：`requests`、`Pillow`、`numpy`、`pywin32`（`tkinter` 为标准库）

```bash
pip install requests pillow numpy pywin32
```

## 使用方式

### 1. GUI 配置（推荐）

```bash
python SLW_ini.pyw
```

- 选择地球尺寸（大 / 中 / 小）与背景图
- 点击「保存」→ 写入配置并立即更换壁纸
- 点击「随机生成」→ 随机挑选地球尺寸与背景并立即更换

### 2. 命令行直跑

```bash
python satelliteLiveWallpaper.pyw
```

按配置（背景 `bg.jpg`、地球尺寸由 `slw.ini` 决定，读取失败则默认「大」）执行一次完整流程：下载 → 合成 → 换壁纸。

### 3. 定时自动刷新（可选）

项目本身**不含**定时调度逻辑。如需定时刷新，可用 Windows 任务计划程序定时调用：

```
python satelliteLiveWallpaper.pyw
```

## 配置文件 `log/slw.ini`

共 4 行，由 GUI 写入：

| 行号 | 含义 | 取值 | 实际是否生效 |
| --- | --- | --- | --- |
| 1 | 分辨率宽 | 数字 | 否（运行时动态读取屏幕真实分辨率） |
| 2 | 分辨率高 | 数字 | 否（同上） |
| 3 | 地球尺寸 | 1 / 2 / 3 = 大 / 中 / 小 | **是（唯一生效项）** |
| 4 | 背景图路径 | 文件路径 | 仅「随机生成」分支参考 |

> 说明：GUI 中「选择背景图」的真实生效方式是**将所选 JPG 复制覆盖** `background/bg.jpg`，后续流程固定使用 `bg.jpg`。

## 目录结构

```
earth/
├── satelliteLiveWallpaper.pyw   # 主流程入口（无 GUI 直跑）
├── SLW_ini.pyw                  # Tkinter 配置界面入口
├── getPic.py                    # 下载卫星云图
├── changePic.py                 # 图像合成（抠圆 + 叠加背景）核心
├── setWallpaper.py              # 设置 Windows 壁纸
├── getPath.py                   # 统一路径管理（工具层）
├── readWriteFile.py             # 配置文件读写（工具层）
├── background/                  # 背景图：bg.jpg、bg1~bg4.jpg
├── tk_bg/                       # GUI 窗口背景图
├── pic/                         # 运行产物（缓存云图 / 地球 / 合成结果）
├── log/slw.ini                  # 运行时配置
└── README.md
```

## 一次壁纸刷新的完整流程

```
satelliteLiveWallpaper.myRun()
 ├──① getPic.crawlWallpaper()     下载 FY-4A 圆盘云图 → pic/cache_wallpaper.jpg
 ├──② changePic.changePic()
 │     ├── redraw_circle()        像素级圆形抠图 → pic/earth.png（去白边）
 │     └── redraw_left_right()    按屏幕尺寸叠加背景图 → pic/final.png
 └──③ setWallpaper.setWallPaper() 写注册表(WallpaperStyle=10, TileWallpaper=0)
                                   + SPI_SETDESKWALLPAPER 即时生效
```

## 已知问题与优化建议（TODO）

> 本项目为个人工具，以下按优先级列出，不影响当前主流程使用。

**已完成的迭代（2026-11）**

- [x] `SLW_ini.pyw` 补 `import win32api, win32con`，修复打开即 `NameError`
- [x] 抠图矢量化：`redraw_circle` 由逐像素双层循环改为 `numpy` 距离矩阵 + 圆形蒙版，单次抠图毫秒级
- [x] 网络健壮性：`getPic` 增加 15s timeout、状态码校验、3 次重试；10 分钟内缓存过则跳过重复下载
- [x] GUI 后台线程：保存 / 随机改为 `_thread` 后台执行，界面不再卡死；主流程加异常兜底
- [x] 资源清理：注册表句柄 `RegCloseKey` 关闭；配置读取异常区分 `FileNotFoundError` 与真实错误；删除废弃函数 `redraw_upper_left` / `redraw_bottom_right`
- [x] `getPath` 用脚本绝对路径定位，修复相对路径调用时产物误写到磁盘根目录的问题

**P3 — 可选扩展**

- [ ] `pyinstaller` 打包为 exe，免 Python 环境
- [ ] 数据源抽象为多源插件化（FY-4A / 葵花 8 等）
- [ ] 定时刷新做成内置功能或 Windows 服务
