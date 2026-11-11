---
layout_id: type_foreground_cover
kind: layout
layout_scope: page
category: general
summary: 大字与前景穿插封面：成对背景和透明前景夹住可编辑标题，利用遮挡建立空间层次。
keywords: [layered-image, oversized-title, foreground, editable]
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
page_types: [cover]
placeholders:
  01_cover: ["{{TITLE}}", "{{SUBTITLE}}"]
---

# 大字与前景穿插封面 — Layout Design Specification

## IV. Signature Design Elements

- 后景、可编辑大字、透明前景形成明确的三层遮挡关系；标题不能被烘焙到任何图片中，前景不能下沉到母版或标题之后。
- 两个 picture 槽位使用相同的整页坐标、尺寸和映射。更换场景时同步准备成对素材，背景去除要独立呈现的主体，前景以未裁边的透明画布保留主体原始位置；只换其中一张会破坏注册关系。
- 主标题使用单个原生 title 槽位，短语居中跨越画面，竖向透明渐变使文字与后景过渡；字段居中是短标题的空间例外，不套用到长段正文。实际字体与字号由下游身份和内容长度决定，预览字体仅显示槽位容量。
- 上方 subtitle 槽位承担短副题，小分隔线位于其下；图像主体与大标题为主要视觉关系，不添加数据、公司或城市的内容要求。
- 本包两张样图为同源 AI 参考重建的配对素材，仅用于展示图层关系，不绑定地名、年份或题材。它们随包保存，不能依赖测试目录。图层、渐变和文字分别保持可编辑，不附带动画。

## V. Page Roster

| SVG | Master | Layout / Picker | Content Shape | Slot Behavior |
|---|---|---|---|---|
| `01_cover.svg` | `type_foreground_cover_master` | `type_foreground_cover_main` / 大字与前景穿插封面 | 成对图片、中央短大字、上方副题 | 背景与前景槽均 `(0,0,1280,720)`；标题框 `(0,132,1280,390)` 居中；副题框 `(220,48,840,64)`；前景按原型顺序位于标题之后 |
