#!/usr/bin/env python3
"""Inspect resources or export an already-authored slide; not a generation workflow."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

SKILL = Path(__file__).resolve().parent.parent
LIBRARY = SKILL / 'templates' / 'page_layouts'
MARKER = re.compile(r'\{\{[A-Z][A-Z0-9_]*\}\}')


def catalog():
    return json.loads((LIBRARY / 'page_layouts_index.json').read_text(encoding='utf-8'))


def image_styles():
    index = json.loads((SKILL / 'templates/image_styles/image_styles_index.json').read_text(encoding='utf-8'))
    styles = []
    for key, entry in index.items():
        recipe = json.loads((SKILL / entry['template']).read_text(encoding='utf-8'))
        sample = json.loads((SKILL / entry['reference']).read_text(encoding='utf-8'))
        if recipe['id'] != key or sample['template_id'] != key:
            raise ValueError(f'Template and sample ids do not match: {key}')
        preview = (Path(entry['reference']).parent / sample['preview']).as_posix()
        styles.append(dict(recipe, preview=preview, preview_note=sample.get('note', ''),
                           preview_kind=sample.get('preview_kind', ''),
                           source=sample.get('source', {})))
    return styles


def outside_skill(path):
    resolved = path.expanduser().resolve()
    if resolved == SKILL or SKILL in resolved.parents:
        raise ValueError('Workspaces and exports must be outside the skill package.')
    return resolved


def slide_source(workspace):
    sources = sorted((workspace / 'templates').glob('*.svg'))
    if len(sources) != 1:
        raise ValueError(f'Expected exactly one slide SVG; found {len(sources)}.')
    source = sources[0]
    root = ET.parse(source).getroot()
    unresolved = sorted(set(MARKER.findall(''.join(root.itertext()))))
    if unresolved:
        raise ValueError('Replace all text fields before export: ' + ', '.join(unresolved))
    for element in root.iter():
        if element.tag.rsplit('}', 1)[-1] != 'image':
            continue
        href = element.get('href') or element.get('{http://www.w3.org/1999/xlink}href', '')
        if href.startswith('data:'):
            continue
        parsed = urlsplit(href)
        if not href or parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
            raise ValueError(f'Use a local relative image reference: {href!r}')
        image = (source.parent / unquote(parsed.path)).resolve()
        if workspace not in image.parents or not image.is_file():
            raise ValueError(f'Image must exist inside the workspace: {href!r}')
    return source


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list', help='List layouts and image styles.')
    init = commands.add_parser('init', help='Copy one layout to a new workspace.')
    init.add_argument('layout')
    init.add_argument('workspace', type=Path)
    export = commands.add_parser('export', help='Export an already-authored page; not a substitute for the PPT workflow.')
    export.add_argument('workspace', type=Path)
    export.add_argument('-o', '--output', type=Path, required=True)
    export.add_argument('--force', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'list':
            print(json.dumps({'layouts': catalog(), 'image_styles': image_styles()},
                ensure_ascii=False, indent=2))
            return 0
        workspace = outside_skill(args.workspace)
        if args.command == 'init':
            if args.layout not in catalog():
                raise ValueError(f'Unknown layout: {args.layout}')
            if workspace.exists():
                raise ValueError(f'Workspace already exists: {workspace}')
            shutil.copytree(LIBRARY / args.layout, workspace,
                            ignore=shutil.ignore_patterns('preview.png', '__pycache__'))
            print(workspace)
            return 0

        source = slide_source(workspace)
        output = outside_skill(args.output)
        if output.suffix.lower() != '.pptx':
            raise ValueError('Output must have a .pptx extension.')
        png = output.with_suffix('.png')
        for target in (output, png):
            if target.exists() and not args.force:
                raise ValueError(f'Output already exists: {target}; use --force to replace.')
        from attribution_guard import require_skill_integrity
        require_skill_integrity()
        from svg_to_pptx.pptx_package.media import convert_svg_to_png
        from svg_to_pptx.use_expander import expand_use_data_icons, expand_local_use_references
        output.parent.mkdir(parents=True, exist_ok=True)
        # Render first: do not report complete delivery without a usable preview.
        tree = ET.parse(source)
        expand_use_data_icons(tree.getroot(), workspace / 'icons')
        expand_local_use_references(tree.getroot())
        # Keep relative image references anchored beside the source SVG.
        with tempfile.NamedTemporaryFile(suffix='.svg', dir=source.parent, delete=False) as handle:
            preview_source = Path(handle.name)
        try:
            tree.write(preview_source, encoding='utf-8', xml_declaration=True)
            if not convert_svg_to_png(preview_source, png, width=1920, height=1080):
                raise RuntimeError('SVG preview unavailable; install a working CairoSVG/Cairo renderer.')
        finally:
            preview_source.unlink(missing_ok=True)
        command = [sys.executable, str(SKILL / 'scripts' / 'template_preview_pptx.py'),
                   str(workspace), '-o', str(output)]
        if args.force:
            command.append('--force')
        result = subprocess.run(command, check=False)
        if result.returncode:
            return result.returncode
        from pptx import Presentation
        if len(Presentation(str(output)).slides) != 1:
            raise RuntimeError('Exported PPTX did not contain exactly one slide.')
        print(f'PPTX: {output}\nSVG source preview (not a PowerPoint render): {png}')
        return 0
    except (OSError, ValueError, RuntimeError, ET.ParseError, ImportError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    raise SystemExit(main())
