'use strict';

const TOKEN = document.querySelector('meta[name="gallery-token"]').content;
const KIND_LABEL = { 'ppt-layout': '版式', 'image-transform': '图片风格', 'color-palette': '配色' };
const VIEW_KIND = { layouts: 'ppt-layout', styles: 'image-transform', palettes: 'color-palette', projects: 'project' };
const VIEW_META = {
  layouts: { title: '版式', desc: '一页 PPT 的完整版式：结构规格、SVG 原型与可替换素材。' },
  styles: { title: '图片风格', desc: '以你的图片为起点，改造成不同视觉风格；样张只说明风格。' },
  palettes: { title: '配色', desc: '56 组五色配色，三种模式共用；选用后回到对话说明用途。' },
  projects: { title: '作品', desc: '已生成作品的预览与导出；修改仍在对话里进行。' },
};

const state = {
  catalog: { layouts: [], styles: [], palettes: [], projects: [], selected: null },
  view: 'layouts',
  detailKind: null,
  detailId: null,
  filter: '',
};

const grid = document.querySelector('#grid');
const empty = document.querySelector('#empty');
const detail = document.querySelector('#detail');
const backdrop = document.querySelector('#backdrop');
const search = document.querySelector('#search');
const toastNode = document.querySelector('#toast');
const copyButton = document.querySelector('#copy-selection');
const clearButton = document.querySelector('#clear-selection');

let toastTimer;

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === null || value === undefined || value === false) continue;
    if (key === 'class') node.className = value;
    else if (key === 'text') node.textContent = value;
    else if (key.startsWith('on') && typeof value === 'function') node.addEventListener(key.slice(2).toLowerCase(), value);
    else if (value === true) node.setAttribute(key, '');
    else node.setAttribute(key, value);
  }
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

const media = (path) => '/resource/' + String(path || '').split('/').map(encodeURIComponent).join('/');

async function api(path, options = {}) {
  const headers = { 'X-Gallery-Token': TOKEN };
  if (options.body) headers['Content-Type'] = 'application/json';
  const response = await fetch(path, { ...options, headers: { ...headers, ...(options.headers || {}) } });
  const isJson = (response.headers.get('content-type') || '').includes('json');
  const payload = isJson ? await response.json() : await response.text();
  if (!response.ok) throw new Error((payload && payload.error) || '请求失败。');
  return payload;
}

function poolFor(kind) {
  if (kind === 'ppt-layout') return state.catalog.layouts;
  if (kind === 'image-transform') return state.catalog.styles;
  if (kind === 'color-palette') return state.catalog.palettes;
  if (kind === 'project') return state.catalog.projects;
  return [];
}

function detailItem() {
  return poolFor(state.detailKind).find((item) => item.id === state.detailId) || null;
}

function isSelected(kind, id) {
  const selected = state.catalog.selected;
  return Boolean(selected && selected.kind === kind && selected.id === id);
}

function matches(item) {
  if (!state.filter) return true;
  const haystack = [
    item.id, item.name, item.summary, item.use_when, item.note, item.credit,
    ...(item.tags || []), ...(item.page_types || []), ...(item.colors || []),
  ].filter(Boolean).join(' ').toLowerCase();
  return haystack.includes(state.filter.toLowerCase());
}

function previewImage(src, alt) {
  const img = el('img', { src, alt: alt || '', loading: 'lazy' });
  img.addEventListener('error', () => img.classList.add('is-missing'), { once: true });
  return img;
}

function projectPreviewUrl(item) {
  return `/api/preview?id=${encodeURIComponent(item.id)}&key=${encodeURIComponent(TOKEN)}`;
}

function formatDate(value) {
  const stamp = value > 1e12 ? value : value * 1000;
  const date = new Date(stamp);
  if (Number.isNaN(date.getTime())) return '';
  const pad = (part) => String(part).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function toast(message) {
  toastNode.textContent = message;
  toastNode.dataset.show = 'true';
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toastNode.dataset.show = 'false'; }, 2400);
}

/* ---------- rendering ---------- */

function render() {
  document.querySelectorAll('.nav-item').forEach((button) => {
    button.setAttribute('aria-current', button.dataset.view === state.view ? 'true' : 'false');
  });
  document.querySelector('#count-layouts').textContent = state.catalog.layouts.length;
  document.querySelector('#count-styles').textContent = state.catalog.styles.length;
  document.querySelector('#count-palettes').textContent = state.catalog.palettes.length;
  document.querySelector('#count-projects').textContent = state.catalog.projects.length;
  const meta = VIEW_META[state.view];
  document.querySelector('#view-title').textContent = meta.title;
  document.querySelector('#view-desc').textContent = meta.desc;
  grid.dataset.view = state.view;
  renderGrid();
  renderDetail();
  renderSelection();
  syncDrawer();
}

function renderGrid() {
  grid.replaceChildren();
  const items = poolFor(VIEW_KIND[state.view]).filter(matches);
  empty.hidden = items.length > 0;
  if (!items.length) {
    empty.textContent = state.filter
      ? `没有匹配「${state.filter}」的条目。`
      : {
        layouts: '还没有版式模板。',
        styles: '还没有图片风格。',
        palettes: '还没有配色。',
        projects: '还没有可预览的作品。把 --workspace 指向已生成的工作目录，或回到对话继续制作。',
      }[state.view];
  }
  for (const item of items) {
    grid.append(state.view === 'projects' ? projectCard(item) : resourceCard(state.view, item));
  }
}

function resourceCard(viewName, item) {
  const kind = VIEW_KIND[viewName];
  const selected = isSelected(kind, item.id);
  const card = el('button', { type: 'button', class: 'card', 'data-view': viewName, 'aria-pressed': selected ? 'true' : 'false' });

  if (viewName === 'palettes') {
    card.append(el('div', { class: 'swatches' }, (item.colors || []).map((hex) => el('span', { style: `background:${hex}` }))));
    card.append(el('div', { class: 'palette-info' },
      el('span', { class: 'palette-id', text: item.id }),
      el('span', { class: 'palette-name', text: item.name })));
    if (item.credit) card.append(el('p', { class: 'palette-credit', text: `署名 ${item.credit}` }));
    if (selected) card.append(el('span', { class: 'card-flag', text: '已选' }));
  } else {
    const frame = el('div', { class: 'card-media' }, previewImage(media(item.preview), item.name));
    if (selected) frame.append(el('span', { class: 'card-flag', text: '已选' }));
    card.append(frame, el('p', { class: 'card-name', text: item.name }));
    const metaParts = viewName === 'layouts'
      ? [(item.page_types || []).join(' / '), item.canvas_format]
      : [item.aspect, ...(item.tags || []).slice(0, 2)];
    card.append(el('p', { class: 'card-meta' }, metaParts.filter(Boolean).map((part) => el('span', { text: part }))));
  }

  card.addEventListener('click', () => openDetail(kind, item.id));
  return card;
}

function projectCard(item) {
  const card = el('button', { type: 'button', class: 'card', 'data-view': 'projects' });
  card.append(el('div', { class: 'card-media' }, previewImage(projectPreviewUrl(item), item.name)));
  card.append(el('p', { class: 'card-name', text: item.name }));
  card.append(el('p', { class: 'card-meta' },
    el('span', { text: item.unavailable ? '工作目录不可用' : '单页作品' }),
    item.modified ? el('span', { text: formatDate(item.modified) }) : null));
  card.addEventListener('click', () => openDetail('project', item.id));
  return card;
}

function renderDetail() {
  const item = detailItem();
  detail.replaceChildren();
  if (!item) {
    detail.append(introPanel());
    return;
  }
  if (state.detailKind === 'project') renderProject(item);
  else renderResource(state.detailKind, item);
}

function introPanel() {
  return el('section', {},
    el('p', { class: 'intro-kicker', text: '怎么用' }),
    el('ol', { class: 'steps' },
      el('li', {}, el('b', { text: '浏览' }), '按类别看版式、图片风格和配色；点开卡片看大图与说明。'),
      el('li', {}, el('b', { text: '选用' }), '在详情里点「选用」，展厅会把选择写进本次任务。'),
      el('li', {}, el('b', { text: '回对话' }), '告诉技能用途、文案和修改要求；成品仍由技能生成。')),
    el('p', { class: 'intro-note', text: '浏览器不编辑内容，也不代替 PPT 流程里的确认节点。' }));
}

function renderResource(kind, item) {
  if (kind === 'color-palette') {
    detail.append(el('div', { class: 'swatch-list' }, (item.colors || []).map((hex) => el('div', { class: 'swatch-row' }, el('i', { style: `background:${hex}` }), hex))));
  } else {
    detail.append(el('div', { class: 'detail-preview', 'data-ratio': kind === 'image-transform' ? '4/5' : '16/9' },
      previewImage(media(item.preview), item.name)));
  }

  detail.append(el('h2', { text: item.name }));
  const lede = kind === 'image-transform' ? (item.use_when || item.preview_note) : (item.summary || item.note);
  if (lede) detail.append(el('p', { class: 'lede', text: lede }));

  if (kind === 'image-transform' && item.tags && item.tags.length) {
    detail.append(el('div', { class: 'tags' }, item.tags.map((tag) => el('span', { text: tag }))));
  }

  const dl = el('dl', { class: 'meta' });
  if (kind === 'ppt-layout') {
    addMeta(dl, '画布', item.canvas_format);
    addMeta(dl, '页面类型', (item.page_types || []).join(' / '));
    addMeta(dl, '模板', item.id);
  } else if (kind === 'image-transform') {
    addMeta(dl, '比例', item.aspect);
    if (item.source && (item.source.platform || item.source.author)) {
      addMeta(dl, '来源', [item.source.platform, item.source.author].filter(Boolean).join(' · '));
    }
    if (item.source && item.source.url) {
      addMeta(dl, '原帖', el('a', { class: 'source-link', href: item.source.url, target: '_blank', rel: 'noopener noreferrer', text: '打开原帖' }));
    }
    addMeta(dl, '说明', item.preview_note);
  } else {
    addMeta(dl, '编号', item.id);
    addMeta(dl, '署名', item.credit);
    addMeta(dl, '说明', item.note);
  }
  if (dl.children.length) detail.append(dl);

  detail.append(selectButton(kind, item));
  detail.append(el('p', { class: 'detail-note', text: '选用后展厅会把选择写进本次任务；内容生成与修改仍在对话里完成。' }));
}

function renderProject(item) {
  detail.append(el('div', { class: 'detail-preview' }, previewImage(projectPreviewUrl(item), item.name)));
  detail.append(el('h2', { text: item.name }));
  const dl = el('dl', { class: 'meta' });
  addMeta(dl, '版式', item.layout);
  addMeta(dl, '修改时间', item.modified ? formatDate(item.modified) : '');
  if (item.unavailable) addMeta(dl, '状态', '工作目录不可用');
  detail.append(dl);

  const status = el('p', { class: 'export-status' });
  const actions = el('div');
  const button = el('button', { type: 'button', class: 'primary', text: '导出这一页 PPTX' });
  button.addEventListener('click', () => startExport(item, button, status, actions));
  detail.append(button, status, actions);
  detail.append(el('p', { class: 'detail-note', text: '导出需要可用的 SVG 渲染器（CairoSVG）；正式 PPT 仍按原流程检查与导出。' }));
}

function addMeta(dl, label, value) {
  if (!value) return;
  dl.append(el('dt', { text: label }));
  const dd = el('dd');
  dd.append(value instanceof Node ? value : document.createTextNode(String(value)));
  dl.append(dd);
}

function selectButton(kind, item) {
  const selected = isSelected(kind, item.id);
  const label = selected ? '已选用'
    : kind === 'ppt-layout' ? '选用这个版式'
      : kind === 'image-transform' ? '选用这个风格'
        : '选用这组配色';
  const button = el('button', { type: 'button', class: 'primary', 'aria-pressed': selected ? 'true' : 'false', text: label });
  button.addEventListener('click', () => selectItem(kind, item));
  return button;
}

function renderSelection() {
  const body = document.querySelector('#selection-body');
  const selected = state.catalog.selected;
  body.replaceChildren();
  copyButton.disabled = !selected;
  clearButton.disabled = !selected;
  if (!selected) {
    body.append(el('span', { class: 'muted', text: '还没有选择' }));
    return;
  }
  body.append(el('p', { class: 'selection-kind', text: KIND_LABEL[selected.kind] || '资源' }));
  body.append(el('p', { class: 'selection-name', text: selected.name || selected.id }));
  if (selected.colors && selected.colors.length) {
    body.append(el('div', { class: 'selection-swatches' }, selected.colors.map((hex) => el('span', { style: `background:${hex}` }))));
  } else if (selected.preview) {
    body.append(previewImage(media(selected.preview), selected.name));
  }
}

/* ---------- actions ---------- */

function openDetail(kind, id) {
  state.detailKind = kind;
  state.detailId = id;
  renderDetail();
  syncDrawer();
}

function closeDetail() {
  state.detailKind = null;
  state.detailId = null;
  renderDetail();
  syncDrawer();
}

async function selectItem(kind, item) {
  try {
    const selected = await api('/api/select', { method: 'POST', body: JSON.stringify({ kind, id: item.id }) });
    state.catalog.selected = selected;
    render();
    toast(`已选用「${item.name}」`);
  } catch (error) {
    toast(error.message);
  }
}

async function clearSelection() {
  try {
    await api('/api/select', { method: 'POST', body: JSON.stringify({ kind: 'none' }) });
    state.catalog.selected = null;
    render();
    toast('已清除选择');
  } catch (error) {
    toast(error.message);
  }
}

async function copySelection() {
  const selected = state.catalog.selected;
  if (!selected) return;
  const text = JSON.stringify(selected, null, 2);
  try {
    await navigator.clipboard.writeText(text);
    toast('选择已复制');
  } catch (error) {
    const area = el('textarea', { style: 'position:fixed;left:-9999px;top:0' });
    area.value = text;
    document.body.append(area);
    area.select();
    try {
      document.execCommand('copy');
      toast('选择已复制');
    } catch (fallbackError) {
      toast('复制失败，请手动记录选择。');
    }
    area.remove();
  }
}

async function startExport(item, button, status, actions) {
  button.disabled = true;
  status.textContent = '正在导出…';
  try {
    const { job } = await api('/api/export', { method: 'POST', body: JSON.stringify({ project: item.id }) });
    const poll = async () => {
      try {
        const jobState = await api('/api/job?id=' + encodeURIComponent(job));
        if (jobState.status === 'running') {
          setTimeout(poll, 700);
          return;
        }
        if (jobState.status === 'error') {
          status.textContent = jobState.error || '导出失败。';
          button.disabled = false;
          return;
        }
        status.textContent = `导出完成：${jobState.filename}`;
        actions.replaceChildren(el('a', {
          class: 'download',
          href: `/api/download?id=${encodeURIComponent(item.id)}&key=${encodeURIComponent(TOKEN)}`,
          text: '下载 PPTX',
        }));
        button.textContent = '重新导出';
        button.disabled = false;
      } catch (error) {
        status.textContent = error.message;
        button.disabled = false;
      }
    };
    setTimeout(poll, 600);
  } catch (error) {
    status.textContent = error.message;
    button.disabled = false;
  }
}

function syncDrawer() {
  const narrow = window.matchMedia('(max-width: 1240px)').matches;
  const open = narrow && Boolean(state.detailId);
  detail.dataset.open = open ? 'true' : 'false';
  backdrop.hidden = !open;
  document.body.classList.toggle('drawer-open', open);
}

async function load() {
  try {
    state.catalog = await api('/api/catalog');
    if (state.detailId && !detailItem()) {
      state.detailKind = null;
      state.detailId = null;
    }
    render();
  } catch (error) {
    toast(error.message);
  }
}

/* ---------- boot ---------- */

document.querySelectorAll('.nav-item').forEach((button) => {
  button.addEventListener('click', () => {
    state.view = button.dataset.view;
    state.filter = '';
    search.value = '';
    state.detailKind = null;
    state.detailId = null;
    render();
  });
});

search.addEventListener('input', () => {
  state.filter = search.value.trim();
  renderGrid();
});

document.querySelector('#refresh').addEventListener('click', load);
copyButton.addEventListener('click', copySelection);
clearButton.addEventListener('click', clearSelection);
backdrop.addEventListener('click', closeDetail);

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && state.detailId) closeDetail();
});

window.addEventListener('resize', syncDrawer);

load();
