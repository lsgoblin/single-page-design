---
layout_id: torn_paper_diagonal
kind: layout
layout_scope: page
category: general
summary: 双纸层斜向开窗：左上标题与右下短说明分别位于独立撕纸上，中央斜向通道露出可替换场景。
keywords: [torn-paper, diagonal-window, layered-image, editable]
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
canvas_viewbox: "0 0 1280 720"
source_canvas_width: 1280
source_canvas_height: 720
source_viewbox: "0 0 1280 720"
replication_mode: standard
native_structure_mode: structured
page_count: 1
page_types: [content]
placeholders:
  01_content: ["{{TITLE}}", "{{SUBTITLE}}", "{{CONTENT_AREA}}"]
---

# 双纸层斜向开窗 — Layout Design Specification

## IV. Signature Design Elements

- 完整场景铺底，两张独立的撕纸分别占据左上与右下，沿左下至右上的方向留下宽窄变化的开口。撕口不通过裁切正文或标题形成，文字必须位于完整纸面内。
- 场景、左上纸、右下纸各为一个独立 picture 槽位；三个图片框同坐标、同尺寸、同映射。场景可以单独替换，纸层继续保留位置与透明通道，不要求为每张场景重新抠图。
- 调整或更换纸层轮廓时，重新核对标题、短副题与正文的纸面承托关系；不得裁掉纸层透明边界后仍沿用原始框，否则开口和安全区会改变。
- 图片槽的绘制顺序为场景、左上纸、右下纸，其后是文字槽。需要压住场景的纸层保留为 Slide 上的内容，不能下沉到场景之后的固定母版图层。两张纸各自持有原生外阴影，方向统一。
- 标题框位于左上完整纸面，容纳短标题的多行排布；副题在标题上方；正文在右下纸面，左对齐、从框的左上进入。三个文字角色均为独立原生文本框。
- 包内田野与纸张纹理为 AI 参考重建的预览资源，不绑定题材、地名、文案、绿色身份或字体；预览字形、字重、字号与颜色不构成下游身份锁。纸芯、纤维和纹理属于可替换透明图片，文字与投影分别可编辑。

## V. Page Roster

| SVG | Master | Layout / Picker | Content Shape | Slot Behavior |
|---|---|---|---|---|
| `01_content.svg` | `torn_paper_diagonal_master` | `torn_paper_diagonal_main` / 双纸层斜向开窗 | 斜向场景通道、两张独立纸层、左上短标题与右下短说明 | 3个图片槽均 `(0,0,1280,720)`；标题 `(50,84,490,224)`；副题 `(56,42,440,34)`；正文 `(842,540,392,148)`；共6个原生槽位，纸层位于场景之后、文字之前 |
