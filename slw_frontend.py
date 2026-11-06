# -*- coding: utf-8 -*-
"""卫星壁纸设置前端 —— 本地 HTTP 服务

启动方式：双击 go.sh（或命令行 python slw_frontend.py），自动打开浏览器；
关闭窗口即停止服务，不常驻后台。
"""
import os
import re
import sys
import json
import time
import base64
import webbrowser
import threading
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import getPath
import readWriteFile
import satelliteLiveWallpaper

PORT = 7788
TASK_NAME = 'SLW_UpdateWallpaper'   # Windows 计划任务名
SCRIPT_NAME = 'satelliteLiveWallpaper.pyw'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EARTH_LABEL = {'1': '大', '2': '中', '3': '小'}


# ---------- 配置读写 ----------

def read_config():
    '''读取 slw.ini，返回 {w, h, earth, bg}'''
    try:
        lines = readWriteFile.read_file(getPath.logFilePath()).strip().split('\n')
        lines = [l for l in lines if l.strip()]
    except FileNotFoundError:
        lines = []
    earth = '1'
    bg = ''
    if len(lines) >= 3 and lines[2] in ('1', '2', '3'):
        earth = lines[2]
    if len(lines) >= 4:
        bg = getPath.myReplace(lines[3])
    return {'w': lines[0] if len(lines) > 0 else '', 'h': lines[1] if len(lines) > 1 else '',
            'earth': earth, 'bg': bg}


def write_config(earth, bg_path):
    '''写回 slw.ini（第 3 行地球尺寸、第 4 行背景路径）'''
    text = '0\n0\n{}\n{}'.format(earth, getPath.myReplace(bg_path))
    readWriteFile.write_file(getPath.logFilePath(), text)


# ---------- 背景图 ----------

def list_backgrounds():
    return getPath.backgroundList()


def save_uploaded_bg(name, data_b64):
    '''把前端 base64 上传的图片存为 background/bg_user_<时间戳>_<原名>.jpg，返回绝对路径'''
    folder = os.path.join(BASE_DIR, 'background')
    os.makedirs(folder, exist_ok=True)
    safe = re.sub(r'[^\w.\-\u4e00-\u9fa5]', '_', os.path.basename(name) or 'bg.jpg')
    final = os.path.join(folder, 'bg_user_{}_{}'.format(int(time.time()), safe))
    from PIL import Image
    import io
    raw = base64.b64decode(data_b64.split(',')[-1] if ',' in data_b64 else data_b64)
    img = Image.open(io.BytesIO(raw))
    if img.mode in ('RGBA', 'P', 'LA'):
        img = img.convert('RGB')
    img.save(final, 'JPEG', quality=92)
    return getPath.myReplace(final)


# ---------- 计划任务 ----------

def register_task(minutes):
    '''注册计划任务：每 N 分钟运行一次刷新脚本'''
    minutes = max(5, min(int(minutes), 720))
    py = sys.executable
    script = os.path.join(BASE_DIR, SCRIPT_NAME)
    tr = '"{}" "{}"'.format(py, script)
    args = ['schtasks', '/Create', '/F', '/TN', TASK_NAME, '/TR', tr,
            '/SC', 'MINUTE', '/MO', str(minutes), '/RL', 'LIMITED']
    try:
        ret = subprocess.run(args, capture_output=True, text=True, timeout=30)
        ok = ret.returncode == 0
        return ok, (ret.stdout + ret.stderr).strip() or ('成功' if ok else '失败')
    except Exception as e:
        return False, str(e)


def unregister_task():
    try:
        ret = subprocess.run(['schtasks', '/Delete', '/F', '/TN', TASK_NAME],
                             capture_output=True, text=True, timeout=30)
        err = (ret.stderr or '').lower()
        ok = ret.returncode == 0 or 'not found' in err or '没有' in err
        msg = (ret.stdout + ret.stderr).strip() or '已删除'
        return ok, msg
    except Exception as e:
        return False, str(e)


def query_task():
    '''查询计划任务详情，返回 key:value 字典；不存在返回 None'''
    try:
        ret = subprocess.run(['schtasks', '/Query', '/TN', TASK_NAME, '/FO', 'LIST', '/V'],
                             capture_output=True, text=True, timeout=30)
        if ret.returncode != 0:
            return None
        info = {}
        for line in (ret.stdout or '').splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                info[k.strip()] = v.strip()  # 重复键保留最后一个值
        # 补充：schtasks 的 "Repeat: Every:" 行会被拆成键 'Repeat'、值 'Every: ...'，单独补全
        for line in (ret.stdout or '').splitlines():
            if 'Repeat: Every:' in line:
                info['Repeat Every'] = line.split('Repeat: Every:', 1)[1].strip()
        return info or None
    except Exception:
        return None


def extract_period_minutes(task):
    '''从计划任务查询结果解析刷新周期（分钟），如 "0 Hour(s), 30 Minute(s)" → 30'''
    if not task:
        return None
    for k, v in task.items():
        if '复' in k or 'repeat' in k.lower() or k == 'Repeat Every':
            m_h = re.search(r'(\d+)\s*(?:小时|hour)', v, re.I)
            m_m = re.search(r'(\d+)\s*(?:分钟|min)', v, re.I)
            hours = int(m_h.group(1)) if m_h else 0
            minutes = int(m_m.group(1)) if m_m else 0
            if hours or minutes:
                return hours * 60 + minutes
            m2 = re.search(r'(\d+)', v)
            if m2 and ':' not in v:
                return int(m2.group(1))
    return None


# ---------- 刷新 ----------

def refresh_wallpaper(earth, bg):
    '''后台线程执行完整刷新流程，避免阻塞 HTTP 响应'''
    def _run():
        try:
            satelliteLiveWallpaper.myRun(earth_n=earth, bg=bg)
        except Exception as e:
            print('[slw_frontend] 刷新失败: {}'.format(e))
    threading.Thread(target=_run, daemon=True).start()


# ---------- HTTP ----------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, code, data, ctype=None):
        if isinstance(data, (dict, list)):
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            ctype = ctype or 'application/json; charset=utf-8'
        elif isinstance(data, str):
            body = data.encode('utf-8')
            ctype = ctype or 'text/plain; charset=utf-8'
        else:
            body = data
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def _serve_image(self, path, ctype='image/jpeg'):
        '''安全地发送一张图片；仅允许项目目录内文件'''
        norm = os.path.normpath(path)
        if (not os.path.abspath(norm).startswith(BASE_DIR)) or not os.path.isfile(norm):
            self._send(404, {'ok': False, 'error': 'file not found'})
            return
        with open(norm, 'rb') as f:
            self._send(200, f.read(), ctype)

    def _serve_file(self, rel):
        full = os.path.normpath(os.path.join(BASE_DIR, rel))
        if not full.startswith(BASE_DIR) or not os.path.isfile(full):
            self._send(404, {'ok': False, 'error': 'file not found'})
            return
        ext = os.path.splitext(full)[1].lower()
        types = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
                 '.css': 'text/css; charset=utf-8', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                 '.png': 'image/png', '.ico': 'image/x-icon'}
        with open(full, 'rb') as f:
            self._send(200, f.read(), types.get(ext, 'application/octet-stream'))

    def _read_json(self):
        try:
            raw = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            return json.loads(raw.decode('utf-8')) if raw else {}
        except Exception:
            return {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        if path in ('/', '/index.html'):
            self._serve_file('web/index.html')
        elif path.startswith('/web/'):
            self._serve_file(path.lstrip('/'))
        elif path == '/api/bg':
            p = query.get('path', [''])[0]
            self._serve_image(getPath.myReplace(p))
        elif path == '/api/preview':
            if os.path.exists(getPath.finalPath()):
                self._serve_image(getPath.finalPath(), 'image/png')
            else:
                self._send(404, {'ok': False, 'error': '尚未生成壁纸'})
        elif path == '/api/status':
            cfg = read_config()
            task = query_task()
            period = extract_period_minutes(task)
            self._send(200, {
                'ok': True,
                'earth': cfg['earth'],
                'bg': cfg['bg'],
                'backgrounds': list_backgrounds(),
                'taskExists': task is not None,
                'periodMin': period,
                'cacheOk': os.path.exists(getPath.cacheWallPath()),
                'finalOk': os.path.exists(getPath.finalPath()),
                'finalMtime': os.path.getmtime(getPath.finalPath()) if os.path.exists(getPath.finalPath()) else None,
            })
        else:
            self._send(404, {'ok': False, 'error': 'not found'})

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        data = self._read_json()
        if path == '/api/save':
            earth = data.get('earth', '1')
            if str(earth) not in ('1', '2', '3'):
                earth = '1'
            bg = getPath.myReplace(str(data.get('bg', '')))
            write_config(str(earth), bg)
            refresh_wallpaper(str(earth), os.path.basename(bg) or 'bg.jpg')
            self._send(200, {'ok': True, 'msg': '已保存，正在后台刷新壁纸'})
        elif path == '/api/refresh':
            cfg = read_config()
            bg = cfg['bg'] or getPath.backgroundPath()
            refresh_wallpaper(cfg['earth'], os.path.basename(bg) or 'bg.jpg')
            self._send(200, {'ok': True, 'msg': '正在刷新壁纸'})
        elif path == '/api/upload':
            name = data.get('name', 'bg.jpg')
            raw = data.get('data', '')
            try:
                new_path = save_uploaded_bg(name, raw)
            except Exception as e:
                self._send(400, {'ok': False, 'error': '图片解析失败: {}'.format(e)})
                return
            write_config(read_config()['earth'], new_path)
            refresh_wallpaper(read_config()['earth'], os.path.basename(new_path))
            self._send(200, {'ok': True, 'bg': new_path, 'msg': '已上传并应用'})
        elif path == '/api/task':
            minutes = int(data.get('minutes', 30))
            ok, msg = register_task(minutes)
            self._send(200, {'ok': ok, 'msg': msg})
        elif path == '/api/task_remove':
            ok, msg = unregister_task()
            self._send(200, {'ok': ok, 'msg': msg})
        else:
            self._send(404, {'ok': False, 'error': 'not found'})


def start():
    os.chdir(BASE_DIR)
    server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = 'http://127.0.0.1:{}/'.format(PORT)
    print('SLW 设置面板: ' + url + '  (关闭本窗口即停止服务)')
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == '__main__':
    start()
