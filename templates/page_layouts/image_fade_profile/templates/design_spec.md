---
layout_id: image_fade_profile
kind: layout
layout_scope: page
category: general
summary: 图文渐隐信息页：右侧大图通过横向及底部遮罩融入信息区，左侧四项信息与下方说明独立编辑。
keywords: [image-text, directional-fade, four-metrics, editable]
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
canvas_viewbox: "0 0 1280 720"
source_canvas_width: 1280
source_canvas_height: 768
source_viewbox: "0 0 1280 768"
replication_mode: standard
native_structure_mode: structured
page_count: 1
page_types: [content]
placeholders:
  01_content: ["{{SECTION_NAME}}", "{{TITLE}}", "{{SUBTITLE}}", "{{KEY_MESSAGE}}", "{{TAGLINE}}", "{{CONTENT_AREA}}", "{{SOURCE}}", "{{LABEL_1}}", "{{VALUE_1}}", "{{NOTE_1}}", "{{LABEL_2}}", "{{VALUE_2}}", "{{NOTE_2}}", "{{LABEL_3}}", "{{VALUE_3}}", "{{NOTE_3}}", "{{LABEL_4}}", "{{VALUE_4}}", "{{NOTE_4}}"]
---

# 图文渐隐信息页 — Layout Design Specification

## IV. Signature Design Elements

- 图像从右侧进入画布，左侧留出标题与两列两行信息区，下方保留短说明。图像、横向渐隐和底部渐隐分别构造；不得把遮罩烘焙进示例照片。
- 两层渐隐属于图片与文本的衔接结构。遮罩先于文字、后于照片绘制；遮罩的实色端跟随下游页面底色，透明端露出照片，不把预览用中性色描述为品牌色。
- 四个 object 槽位分别包含图标、标签、值和短注释，采用 proxy 绑定保留可编辑子对象；可整体移动或替换内容，不把四项信息合成截图。
- 图片、遮罩、分隔线、文字按当前原型的层次关系保留在 Slide 上；遮罩不能下沉到照片之后。Master 仅提供公共底面。
- 信息槽按列分组，左上进入；下方短标签是短句焦点，允许水平居中，其余说明左对齐。标题层级与字段容量由槽位空间表达，预览字体、字号、字重与图标外观不构成身份约束。
- 配套照片是可替换的 AI 参考重建样图，不绑定城市、公司、品牌、数据或应用场景；图标是预览用可替换矢量资源。

## V. Page Roster

| SVG | Master | Layout / Picker | Content Shape | Slot Behavior |
|---|---|---|---|---|
| `01_content.svg` | `image_fade_profile_master` | `image_fade_profile_content` / 图文渐隐信息页 | 一张侧向主图、双层渐隐、四项并列信息、短说明 | 图片框 `(380,0,900,720)`；主标题框 `(78,116,560,82)`；四个信息槽为两列两行；原生文本与图片可替换，背景实色与遮罩实色需同步 |

## VII. Placeholder Overrides

`LABEL_1..4`、`VALUE_1..4`、`NOTE_1..4` 为四项信息的可替换字段；`TAGLINE` 是下方短标签。`SECTION_NAME`、`TITLE`、`SUBTITLE`、`KEY_MESSAGE`、`CONTENT_AREA`、`SOURCE` 保持各自文本角色。每项值宜为短数字或短词，过长内容回到排布处理，不向相邻列挤压。示例图片与示例图标随本包分发，引用均在本包内，不依赖测试目录。
