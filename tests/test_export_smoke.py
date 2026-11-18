"""导出冒烟测试：init -> 替换 {{...}} 占位符 -> export。

导出依赖 cairo 渲染预览图；没有 cairo 的机器上，`single_page.py export`
会在渲染阶段失败。因此成功导出用例在缺少 cairo 时 skip，而「未替换占位符
必须失败」的用例不依赖渲染器，照常执行。
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SINGLE_PAGE = REPO_ROOT / 'scripts' / 'single_page.py'
LAYOUT = 'type_foreground_cover'
MARKER = re.compile(r'\{\{[A-Z][A-Z0-9_]*\}\}')


def renderer_available():
    """与 single_page.py 同一判定：cairosvg 或 svglib 任一可用就能导出。"""
    scripts = str(REPO_ROOT / 'scripts')
    sys.path.insert(0, scripts)
    try:
        from render_check import renderer_status
    finally:
        sys.path.remove(scripts)
    ok, _renderer, _detail = renderer_status()
    return ok


RENDERER_AVAILABLE = renderer_available()


def run_single_page(*args):
    """以子进程调用真实的 single_page.py，保留完整 stdout/stderr。"""
    env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    return subprocess.run(
        [sys.executable, '-X', 'utf8', str(SINGLE_PAGE), *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=300,
    )


def init_workspace(tmp_path):
    """复制一份模板到临时工作区。"""
    workspace = tmp_path / 'workspace'
    result = run_single_page('init', LAYOUT, str(workspace))
    assert result.returncode == 0, f'init 失败：\n{result.stdout}\n{result.stderr}'
    assert (workspace / 'templates').is_dir()
    return workspace


def replace_markers(workspace):
    """把模板 SVG 里的 {{...}} 占位符替换成可读示例文案。"""
    sources = sorted((workspace / 'templates').glob('*.svg'))
    assert len(sources) == 1, f'模板应只有一个 SVG，实际 {len(sources)} 个'
    source = sources[0]
    original = source.read_text(encoding='utf-8')
    replaced = MARKER.sub(lambda match: match.group(1).replace('_', ' ').title(), original)
    assert replaced != original, '模板里没有可替换的占位符'
    source.write_text(replaced, encoding='utf-8')
    return source


def test_export_rejects_unresolved_placeholders(tmp_path):
    """占位符未替换时，导出必须失败且不产出 pptx。"""
    workspace = init_workspace(tmp_path)
    output = tmp_path / 'out.pptx'
    result = run_single_page('export', str(workspace), '-o', str(output))
    combined = result.stdout + result.stderr
    assert result.returncode != 0, f'未替换占位符时导出不应成功：\n{combined}'
    assert 'Replace all text fields before export' in combined, combined
    assert not output.exists()


@pytest.mark.skipif(
    not RENDERER_AVAILABLE,
    reason='没有可用的 PNG 渲染器（cairosvg 与 svglib 都不可用），导出需要它生成预览图',
)
def test_export_produces_single_slide_pptx(tmp_path):
    """替换占位符后能导出可打开、恰好一页的 pptx。"""
    from pptx import Presentation

    workspace = init_workspace(tmp_path)
    replace_markers(workspace)
    output = tmp_path / 'export' / 'single-page.pptx'
    result = run_single_page('export', str(workspace), '-o', str(output))
    assert result.returncode == 0, f'export 失败：\n{result.stdout}\n{result.stderr}'
    assert output.is_file(), '未生成 pptx'
    assert output.with_suffix('.png').is_file(), '未生成预览 png'
    presentation = Presentation(str(output))
    assert len(presentation.slides) == 1, f'pptx 应恰好 1 页，实际 {len(presentation.slides)} 页'
