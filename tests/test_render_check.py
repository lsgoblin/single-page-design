"""渲染器探测：缺 cairo 但存在 svglib 回退时，导出不能被拦下。

这条守的是一个真实回归：早期版本无条件按 Cairo 判定，会把装有 svglib
但没有原生 cairo 的环境直接挡在导出之前，而那条路径本来是可用的。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / 'scripts'


@pytest.fixture()
def render_check():
    sys.path.insert(0, str(SCRIPTS))
    try:
        import render_check as module
        yield module
    finally:
        sys.path.remove(str(SCRIPTS))


@pytest.fixture()
def media():
    sys.path.insert(0, str(SCRIPTS))
    try:
        import svg_to_pptx.pptx_package.media as module
        yield module
    finally:
        sys.path.remove(str(SCRIPTS))


def test_cairo_status_reports_failure_detail(render_check):
    """cairo 不可用时必须给出非空原因，可用时原因为空。"""
    ok, detail = render_check.cairo_status()
    assert isinstance(ok, bool)
    assert isinstance(detail, str)
    if not ok:
        assert detail, '探测失败时必须给出可读原因'


def test_svglib_fallback_is_not_blocked(render_check, media, monkeypatch):
    """media 选择 svglib 回退时，renderer_status 必须放行。"""
    monkeypatch.setattr(media, 'PNG_RENDERER', 'svglib')
    ok, renderer, detail = render_check.renderer_status()
    assert ok is True
    assert renderer == 'svglib'
    assert detail == ''


def test_no_renderer_blocks_export(render_check, media, monkeypatch):
    """两种渲染器都不可用时必须拦下，并带出原因。"""
    monkeypatch.setattr(media, 'PNG_RENDERER', None)
    monkeypatch.setattr(render_check, 'cairo_status', lambda: (False, 'probe failed'))
    ok, renderer, detail = render_check.renderer_status()
    assert ok is False
    assert renderer is None
    assert detail == 'probe failed'


def test_message_mentions_svglib_alternative(render_check):
    """提示必须给出纯 Python 回退方案，否则用户只剩装原生库一条路。"""
    message = render_check.render_unavailable_message('boom')
    assert 'svglib' in message
    assert 'boom' in message
    assert '退出码 1' in message
