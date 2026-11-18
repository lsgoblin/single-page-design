"""索引一致性测试：条目数、资源路径与 id 对应关系。

三份索引（版式 / 图像风格 / 配色）是技能包对外暴露的资源清单，路径都相对
仓库根目录书写；这里直接读真实文件校验，不做任何 mock。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
LAYOUTS_INDEX = REPO_ROOT / 'templates/page_layouts/page_layouts_index.json'
STYLES_INDEX = REPO_ROOT / 'templates/image_styles/image_styles_index.json'
PALETTES_INDEX = REPO_ROOT / 'templates/color_palettes/color_palettes_index.json'

INDEX_FILES = [LAYOUTS_INDEX, STYLES_INDEX, PALETTES_INDEX]
EXPECTED_COUNTS = {LAYOUTS_INDEX: 5, STYLES_INDEX: 16, PALETTES_INDEX: 56}
COLOR_PATTERN = re.compile(r'^#[0-9A-Fa-f]{6}$')


def load_index(index_path):
    """读取一份索引 JSON，返回保持原始顺序的字典。"""
    return json.loads(index_path.read_text(encoding='utf-8'))


def index_id(index_path):
    """给 parametrize 生成可读的用例 id。"""
    return index_path.parent.name


@pytest.mark.parametrize('index_path', INDEX_FILES, ids=index_id)
def test_index_entry_count(index_path):
    """条目数与已确认的资源数量一致。"""
    actual = len(load_index(index_path))
    expected = EXPECTED_COUNTS[index_path]
    assert actual == expected, f'{index_path.name} 条目数应为 {expected}，实际 {actual}'


@pytest.mark.parametrize('index_path', INDEX_FILES, ids=index_id)
def test_index_paths_exist(index_path):
    """索引声明的 template / reference / preview 路径都真实存在。"""
    problems = []
    for key, entry in load_index(index_path).items():
        for field in ('template', 'reference'):
            if not entry.get(field):
                problems.append(f'{key}: 缺少 {field} 字段')
        for field in ('template', 'reference', 'preview'):
            relative = entry.get(field)
            if not relative:
                continue
            if not (REPO_ROOT / relative).exists():
                problems.append(f'{key}.{field} -> {relative} 不存在')
    assert not problems, '以下索引路径无效：\n' + '\n'.join(problems)


def test_image_style_ids_match_index():
    """风格模板的 id 与样本的 template_id 必须与索引键一致。"""
    problems = []
    for key, entry in load_index(STYLES_INDEX).items():
        recipe = json.loads((REPO_ROOT / entry['template']).read_text(encoding='utf-8'))
        sample = json.loads((REPO_ROOT / entry['reference']).read_text(encoding='utf-8'))
        if recipe.get('id') != key:
            problems.append(f'{key}: template.json id 为 {recipe.get("id")!r}')
        if sample.get('template_id') != key:
            problems.append(f'{key}: sample.json template_id 为 {sample.get("template_id")!r}')
    assert not problems, '风格 id 不一致：\n' + '\n'.join(problems)


def test_image_style_preview_exists():
    """样本声明的 preview 相对样本目录解析后存在。"""
    missing = []
    for key, entry in load_index(STYLES_INDEX).items():
        reference = REPO_ROOT / entry['reference']
        sample = json.loads(reference.read_text(encoding='utf-8'))
        preview = sample.get('preview')
        if not preview:
            missing.append(f'{key}: sample.json 缺少 preview')
        elif not (reference.parent / preview).is_file():
            missing.append(f'{key}: 预览图不存在 {preview}')
    assert not missing, '风格预览图缺失：\n' + '\n'.join(missing)


def test_palette_colors_are_five_hex_values():
    """每组配色恰好 5 个 #RRGGBB 颜色。"""
    problems = []
    for key, entry in load_index(PALETTES_INDEX).items():
        colors = entry.get('colors')
        if not isinstance(colors, list) or len(colors) != 5:
            problems.append(f'{key}: colors 应为 5 个，实际 {colors!r}')
            continue
        for color in colors:
            if not isinstance(color, str) or not COLOR_PATTERN.fullmatch(color):
                problems.append(f'{key}: 非法颜色 {color!r}')
    assert not problems, '配色格式不正确：\n' + '\n'.join(problems)
