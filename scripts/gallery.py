#!/usr/bin/env python3
"""Local skill gallery. python gallery.py --session <external-work-directory>"""
from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit
from xml.etree import ElementTree as ET

from single_page import SKILL, LIBRARY, catalog, image_styles, outside_skill, slide_source

UI = SKILL / 'gallery'
NAMES = {'image_fade_profile': '图文渐隐信息页', 'type_foreground_cover': '大字与前景穿插',
         'torn_paper_diagonal': '双纸层斜向开窗'}
DEFAULTS = dict(TITLE='看见留白', SUBTITLE='A quieter way to see', SECTION_NAME='FIELD NOTES',
                KEY_MESSAGE='少一点，更清楚。', TAGLINE='Less, with intention.',
                CONTENT_AREA='让画面聚焦，让每一处留白都有意义。', SOURCE='预览使用包内演示素材')
for i, label in enumerate(['焦点', '光线', '空间', '节奏'], 1):
    DEFAULTS.update({f'LABEL_{i}': label, f'VALUE_{i}': f'0{i}', f'NOTE_{i}': '从细节开始'})


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


def text_nodes(root):
    return [node for node in root.iter() if node.tag.rsplit('}', 1)[-1] == 'text']


class ConflictError(ValueError):
    pass


class Gallery:
    def __init__(self, session, workspace=None):
        self.session = outside_skill(session)
        self.session.mkdir(parents=True, exist_ok=True)
        self.state_path = self.session / 'gallery_state.json'
        self.state = read_json(self.state_path) if self.state_path.exists() else {'selected': None, 'projects': []}
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.RLock()
        self.jobs = {}
        if workspace:
            workspace = outside_skill(workspace)
            slide_source(workspace)
            if not any(p['path'] == str(workspace) for p in self.state['projects']):
                self.state['projects'].append({'id': uuid.uuid4().hex[:12], 'layout': 'custom',
                                               'name': workspace.name, 'path': str(workspace)})
                self.save()

    def save(self):
        write_json(self.state_path, self.state)

    def project(self, key):
        project = next((p for p in self.state['projects'] if p['id'] == key), None)
        if project is None:
            raise ValueError('作品不存在，请返回展厅重新选择。')
        workspace = outside_skill(Path(project['path']))
        return project, workspace, slide_source(workspace)

    def project_view(self, key):
        project, workspace, source = self.project(key)
        root = ET.parse(source).getroot()
        fields = [{'id': str(i), 'label': node.get('id', '') or f'文本 {i + 1}',
                   'value': ''.join(node.itertext())} for i, node in enumerate(text_nodes(root))]
        modified = max([source.stat().st_mtime_ns] + [p.stat().st_mtime_ns for folder in ['images', 'icons']
                       for p in (workspace / folder).rglob('*') if p.is_file()])
        return dict(project, fields=fields, revision=str(source.stat().st_mtime_ns),
                    preview_revision=str(modified), modified=source.stat().st_mtime)

    def contents(self):
        layouts = [dict(value, id=key, kind='ppt-layout', name=NAMES.get(key, key))
                   for key, value in catalog().items()]
        styles = [dict(s, kind='image-transform', summary=s['use_when']) for s in image_styles()]
        projects = []
        for item in self.state['projects']:
            try:
                view = self.project_view(item['id'])
                projects.append({k: view[k] for k in ['id', 'name', 'layout', 'modified', 'preview_revision']})
            except (OSError, ValueError, ET.ParseError):
                projects.append(dict(item, unavailable=True))
        return dict(layouts=layouts, styles=styles, projects=projects, selected=self.state['selected'])

    def create(self, layout):
        if layout not in catalog():
            raise ValueError('未找到这个单页模板。')
        key = uuid.uuid4().hex[:12]
        workspace = self.session / 'workspaces' / key
        shutil.copytree(LIBRARY / layout, workspace,
                        ignore=shutil.ignore_patterns('preview.png', '__pycache__'))
        source = next((workspace / 'templates').glob('*.svg'))
        tree = ET.parse(source)
        for node in text_nodes(tree.getroot()):
            if node.text:
                node.text = re.sub(r'\{\{([A-Z][A-Z0-9_]*)\}\}', lambda m: DEFAULTS.get(m[1], m[1]), node.text)
                if layout == 'type_foreground_cover' and node.get('id') == 'hero-title-carrier':
                    node.text = 'FLOW'
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        tree.write(source, encoding='utf-8', xml_declaration=True)
        project = dict(id=key, layout=layout, name=NAMES.get(layout, layout), path=str(workspace))
        self.state['projects'].append(project)
        self.state['selected'] = dict(kind='ppt-layout', id=layout, project=key)
        self.save()
        return self.project_view(key)

    def update(self, data):
        project, workspace, source = self.project(data['project'])
        if str(source.stat().st_mtime_ns) != data.get('revision'):
            raise ConflictError('作品已在其他位置修改。请先重新载入，再提交本次文案。')
        tree = ET.parse(source)
        nodes = text_nodes(tree.getroot())
        fields = data.get('fields')
        if not isinstance(fields, dict):
            raise ValueError('文案格式不正确。')
        for index, value in fields.items():
            if not index.isdigit() or int(index) >= len(nodes) or not isinstance(value, str) or len(value) > 2000:
                raise ValueError('文案字段无效或过长。')
            node = nodes[int(index)]
            if value != ''.join(node.itertext()):
                if '\n' in value or '\r' in value:
                    raise ValueError('当前文案编辑支持单行；复杂换行请交给设计技能调整。')
                for child in list(node):
                    node.remove(child)
                node.text = value
        temporary = source.with_suffix('.svg.tmp')
        tree.write(temporary, encoding='utf-8', xml_declaration=True)
        temporary.replace(source)
        self.save()
        return self.project_view(project['id'])

    def svg(self, key):
        _, workspace, source = self.project(key)
        from svg_to_pptx.use_expander import expand_use_data_icons, expand_local_use_references
        tree = ET.parse(source)
        root = tree.getroot()
        expand_use_data_icons(root, workspace / 'icons')
        expand_local_use_references(root)
        for node in root.iter():
            if node.tag.rsplit('}', 1)[-1] != 'image':
                continue
            href = node.get('href') or node.get('{http://www.w3.org/1999/xlink}href', '')
            if href.startswith('data:'):
                continue
            path = (source.parent / unquote(href)).resolve()
            if workspace not in path.parents or not path.is_file():
                raise ValueError('图片资源缺失或不属于当前作品。')
            mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
            node.set('href', f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode())
            node.attrib.pop('{http://www.w3.org/1999/xlink}href', None)
        return ET.tostring(root, encoding='utf-8', xml_declaration=True)

    def export(self, key):
        project, workspace, _ = self.project(key)
        job_id = uuid.uuid4().hex[:12]
        output = workspace / 'exports' / f'single-page-{job_id}.pptx'
        self.jobs[job_id] = dict(status='running', project=key)

        def build():
            try:
                with self.lock:
                    result = subprocess.run([sys.executable, '-X', 'utf8', str(SKILL / 'scripts/single_page.py'),
                                             'export', str(workspace), '-o', str(output)],
                                            cwd=workspace, env=dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1'),
                                            capture_output=True, text=True, encoding='utf-8', timeout=180)
                    (workspace / 'export.log').write_text(result.stdout + result.stderr, encoding='utf-8')
                    if result.returncode:
                        raise ValueError('导出未完成。请检查作品素材或查看 export.log。')
                    project['latest_export'] = output.name
                    self.save()
                    self.jobs[job_id].update(status='done', filename=output.name)
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                self.jobs[job_id].update(status='error', error=str(exc))
        threading.Thread(target=build, daemon=True).start()
        return dict(job=job_id)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    @property
    def app(self):
        return self.server.app

    def send(self, content, mime='application/json; charset=utf-8', status=200, download=None):
        if not isinstance(content, bytes):
            content = json.dumps(content, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; object-src 'none'")
        if download:
            self.send_header('Content-Disposition', f'attachment; filename="{download}"')
        self.end_headers()
        self.wfile.write(content)

    def check_host(self):
        port = self.server.server_address[1]
        if self.headers.get('Host') not in {f'127.0.0.1:{port}', f'localhost:{port}'}:
            raise PermissionError('Local access only.')

    def authenticated(self, query):
        supplied = self.headers.get('X-Gallery-Token') or query.get('key', [''])[0]
        if not secrets.compare_digest(supplied, self.app.token):
            raise PermissionError('请从展厅主页重新打开。')

    def do_GET(self):
        try:
            self.check_host()
            url = urlsplit(self.path)
            query = parse_qs(url.query)
            path = unquote(url.path)
            if path == '/':
                page = (UI / 'index.html').read_text(encoding='utf-8').replace('__TOKEN__', html.escape(self.app.token))
                return self.send(page.encode('utf-8'), 'text/html; charset=utf-8')
            if path in ['/app.js', '/styles.css']:
                target = UI / path[1:]
                return self.send(target.read_bytes(), mimetypes.guess_type(target.name)[0] + '; charset=utf-8')
            if path.startswith('/resource/'):
                target = (SKILL / path[len('/resource/'):]).resolve()
                roots = [(SKILL / x).resolve() for x in ['references', 'templates/page_layouts']]
                if not any(root in target.parents for root in roots) or target.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp', '.svg'}:
                    raise PermissionError('Resource unavailable.')
                return self.send(target.read_bytes(), mimetypes.guess_type(target.name)[0])
            if path.startswith('/api/'):
                self.authenticated(query)
                if path == '/api/catalog':
                    with self.app.lock:
                        return self.send(self.app.contents())
                if path == '/api/project':
                    with self.app.lock:
                        return self.send(self.app.project_view(query['id'][0]))
                if path == '/api/preview':
                    with self.app.lock:
                        return self.send(self.app.svg(query['id'][0]), 'image/svg+xml')
                if path == '/api/job':
                    return self.send(self.app.jobs[query['id'][0]])
                if path == '/api/download':
                    project, workspace, _ = self.app.project(query['id'][0])
                    name = project.get('latest_export', '')
                    if not name or Path(name).name != name:
                        raise ValueError('还没有可下载的导出文件。')
                    return self.send((workspace / 'exports' / name).read_bytes(),
                                     'application/vnd.openxmlformats-officedocument.presentationml.presentation', download=name)
            self.send({'error': '未找到该资源。'}, status=404)
        except PermissionError as exc:
            self.send({'error': str(exc)}, status=403)
        except (OSError, ValueError, KeyError, ET.ParseError) as exc:
            self.send({'error': str(exc)}, status=400)

    def do_POST(self):
        try:
            self.check_host()
            self.authenticated({})
            origin = self.headers.get('Origin')
            if origin and origin != 'http://' + self.headers['Host']:
                raise PermissionError('Cross-origin requests are not supported.')
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 262144:
                raise ValueError('请求内容过大或为空。')
            data = json.loads(self.rfile.read(length))
            with self.app.lock:
                if self.path == '/api/create':
                    return self.send(self.app.create(data['layout']))
                if self.path == '/api/save':
                    return self.send(self.app.update(data))
                if self.path == '/api/select':
                    choices = self.app.contents()['styles']
                    choice = next((s for s in choices if s['id'] == data['id']), None)
                    if choice is None:
                        raise ValueError('未找到该风格。')
                    self.app.state['selected'] = dict(kind=choice['kind'], id=choice['id'], name=choice['name'])
                    self.app.save()
                    write_json(self.app.session / 'selection.json', self.app.state['selected'])
                    return self.send(self.app.state['selected'])
                if self.path == '/api/export':
                    return self.send(self.app.export(data['project']))
            self.send({'error': '未找到该操作。'}, status=404)
        except PermissionError as exc:
            self.send({'error': str(exc)}, status=403)
        except ConflictError as exc:
            self.send({'error': str(exc)}, status=409)
        except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as exc:
            self.send({'error': str(exc)}, status=400)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session', type=Path, required=True, help='External directory for choices and workspaces.')
    parser.add_argument('--workspace', type=Path, help='Also preview an existing authored single-page workspace.')
    parser.add_argument('--port', type=int, default=0, help='Default: select a free loopback port.')
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    app = Gallery(args.session, args.workspace)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    server.app = app
    url = f'http://127.0.0.1:{server.server_address[1]}/'
    print(f'Single Page Design Gallery: {url}', flush=True)
    print(f'Workspace: {app.session}', flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    main()
