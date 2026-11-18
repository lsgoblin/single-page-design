#!/usr/bin/env python3
"""Diagnose the SVG-to-PNG renderer that the export preview depends on.

CairoSVG is preferred; svglib + reportlab is a supported fallback. A missing
native Cairo library therefore must not block export on its own.
"""
from __future__ import annotations

import importlib
import sys

IS_WINDOWS = sys.platform.startswith('win')
WINDOWS_LIBRARY = 'libcairo-2.dll'
LINUX_LIBRARY = 'libcairo.so.2'
PROBE_MODULES = ('cairocffi', 'cairosvg')


def _one_line(text):
    """Collapse a multi-line loader error into one readable line."""
    for line in str(text).splitlines():
        line = line.strip()
        if line:
            return line
    return str(text).strip()


def cairo_status():
    """Return (ok, detail) for the native Cairo library.

    ok is True when cairocffi or cairosvg can actually load the native library.
    detail is one readable line describing the failure, or '' when it works.
    """
    problems = []
    for name in PROBE_MODULES:
        try:
            module = importlib.import_module(name)
            if name == 'cairocffi':
                module.cairo_version_string()
            return True, ''
        except (ImportError, OSError) as exc:
            problems.append(f'{name}: {_one_line(exc)}')
    return False, ' | '.join(dict.fromkeys(problems)) or 'cairocffi / cairosvg are not importable'


def renderer_status():
    """Return (ok, renderer, detail) for the renderer the export path will use.

    svglib counts as available, so a machine without Cairo can still export.
    detail carries the Cairo failure only when nothing can render at all.
    """
    try:
        from svg_to_pptx.pptx_package.media import get_png_renderer_info
        renderer, _status, _hint = get_png_renderer_info()
    except (ImportError, OSError):
        ok, detail = cairo_status()
        return ok, ('cairosvg' if ok else None), detail
    if renderer:
        return True, renderer, ''
    return False, None, cairo_status()[1]


def render_unavailable_message(detail=''):
    """Return a multi-line Chinese explanation for a missing PNG renderer."""
    if IS_WINDOWS:
        library = f'{WINDOWS_LIBRARY}（Linux 上对应 {LINUX_LIBRARY}）'
        conda_hint = r'conda install -c conda-forge cairo'
        path_hint = (r'set PATH=%CONDA_PREFIX%\Library\bin;%PATH%'
                     '  或把任意含 cairo-2.dll 的目录加到 PATH 前部')
    else:
        library = f'{LINUX_LIBRARY}（Windows 上对应 {WINDOWS_LIBRARY}）'
        conda_hint = 'conda install -c conda-forge cairo'
        path_hint = ('export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH'
                     '  或安装系统包 libcairo2')
    lines = [
        '导出前要先把 SVG 渲染成 PNG 预览，当前环境没有任何可用的渲染器。',
        f'首选渲染器 CairoSVG 需要原生库 {library}，加载不到它。',
    ]
    if detail:
        lines.append(f'探测结果：{detail}')
    lines += [
        '',
        '修复方式（任选一条，装好后重跑导出命令）：',
        '  a) 先装原生库再装 Python 外壳：',
        f'       {conda_hint}',
        '       pip install cairosvg',
        '  b) 已有原生库时，把它所在目录加进库搜索路径：',
        f'       {path_hint}',
        '  c) 改用纯 Python 回退渲染器（部分渐变与滤镜会丢失，但能导出）：',
        '       pip install svglib reportlab',
        '',
        '这是环境问题，不是代码问题：检查发生在渲染之前，命令以退出码 1 结束，',
        '不会写出缺页或内容不全的 PPTX。',
        '查看当前探测结果：python scripts/render_check.py',
    ]
    return '\n'.join(lines)


if __name__ == '__main__':
    ok, renderer, detail = renderer_status()
    print(f'renderer: {renderer or "none"}')
    print(f'cairo ok: {cairo_status()[0]}')
    if not ok:
        if detail:
            print(detail)
        print()
        print(render_unavailable_message(detail))
