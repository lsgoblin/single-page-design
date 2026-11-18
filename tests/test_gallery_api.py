"""展厅 API 冒烟测试：起真实 HTTP 服务验证 token 鉴权、目录与选择写入。

服务用 `scripts/gallery.py --session <临时目录> --port <随机端口> --no-browser`
以子进程启动，测试结束在 fixture teardown 里可靠关闭，不留下进程。
"""
from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GALLERY = REPO_ROOT / 'scripts' / 'gallery.py'
TOKEN_PATTERN = re.compile(r'<meta name="gallery-token" content="([^"]+)">')


def free_port():
    """让系统分配一个空闲的 loopback 端口。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def request(url, token=None, payload=None, timeout=5):
    """发一个真实 HTTP 请求；payload 非空时用 POST + JSON。"""
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    if token is not None:
        headers['X-Gallery-Token'] = token
    method = 'POST' if data is not None else 'GET'
    return urllib.request.urlopen(
        urllib.request.Request(url, data=data, headers=headers, method=method),
        timeout=timeout,
    )


def wait_until_ready(process, base_url, timeout=30.0):
    """轮询首页直到服务就绪；进程提前退出则直接失败并带出日志。"""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            pytest.fail(f'展厅进程提前退出：\n{stdout}\n{stderr}')
        try:
            with urllib.request.urlopen(base_url + '/', timeout=1) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            time.sleep(0.1)
    pytest.fail(f'展厅服务在 {timeout} 秒内没有就绪')


def terminate(process):
    """确保子进程被关闭：先 terminate，超时再 kill。"""
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
    for stream in (process.stdout, process.stderr):
        if stream is not None:
            stream.close()


@pytest.fixture(scope='module')
def gallery_server(tmp_path_factory):
    """启动一次真实展厅服务，返回 (base_url, token, session 目录)。"""
    session = tmp_path_factory.mktemp('gallery-session')
    port = free_port()
    base_url = f'http://127.0.0.1:{port}'
    env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    process = subprocess.Popen(
        [sys.executable, '-X', 'utf8', str(GALLERY), '--session', str(session),
         '--port', str(port), '--no-browser'],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    try:
        wait_until_ready(process, base_url)
        with request(base_url + '/') as response:
            page = response.read().decode('utf-8')
        match = TOKEN_PATTERN.search(page)
        assert match, '展厅主页没有注入 token meta 标签'
        yield base_url, match.group(1), session
    finally:
        terminate(process)


def test_catalog_requires_token(gallery_server):
    """不带 token 访问 /api/catalog 返回 403。"""
    base_url, _, _ = gallery_server
    with pytest.raises(urllib.error.HTTPError) as excinfo:
        request(base_url + '/api/catalog')
    assert excinfo.value.code == 403
    excinfo.value.close()


def test_catalog_returns_all_resources(gallery_server):
    """带 token 访问 /api/catalog 返回 200，三类资源数量正确。"""
    base_url, token, _ = gallery_server
    with request(base_url + '/api/catalog', token=token) as response:
        assert response.status == 200
        catalog = json.loads(response.read().decode('utf-8'))
    assert len(catalog['layouts']) == 5, f"版式数量为 {len(catalog['layouts'])}"
    assert len(catalog['styles']) == 16, f"风格数量为 {len(catalog['styles'])}"
    assert len(catalog['palettes']) == 56, f"配色数量为 {len(catalog['palettes'])}"


def test_select_palette_writes_selection(gallery_server):
    """POST /api/select 选择配色返回 200，并写出 selection.json。"""
    base_url, token, session = gallery_server
    with request(base_url + '/api/select', token=token,
                 payload={'kind': 'color-palette', 'id': 'P01'}) as response:
        assert response.status == 200
        selected = json.loads(response.read().decode('utf-8'))
    assert selected['id'] == 'P01'
    assert selected['kind'] == 'color-palette'

    selection_path = session / 'selection.json'
    assert selection_path.is_file(), '未写出 selection.json'
    written = json.loads(selection_path.read_text(encoding='utf-8'))
    assert written['selected']['id'] == 'P01'
