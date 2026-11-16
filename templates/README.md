# 可复用模板资源

本目录保存单页 PPT-layout 与图片改造两种模板模式的可复用、可选择、可应用资源。`references/` 中同 ID 的目录保存对应样板样张。图片排版没有整页模板，其字体与字号规范放在 `references/` 下，不占用模板目录。

| 模式 | 模板位置 | 发现索引 | 对应样张 |
|---|---|---|---|
| 单页 PPT-layout | `page_layouts/<id>/` | `page_layouts/page_layouts_index.json` | `references/page_layouts/<id>/` |
| 图片改造 | `image_styles/<id>/template.json` | `image_styles/image_styles_index.json` | `references/image_styles/<id>/` |

图片排版的字体池与字号体系不在本目录：读取 `references/typography_index.json` 与 `references/type_hierarchy.json`，使用方式见 [字体与字号规范](../workflows/image-layout/typography.md)。

表中的 `references/` 路径相对技能根目录。索引的 `template`、`reference`、`preview` 字段也均为技能根目录相对路径，不依赖技能安装位置。

## 单页 PPT-layout

保留原 `ppt-simplify` 的单页包结构：`templates/design_spec.md`、完整页面 SVG，以及按需携带的 `images/`、`icons/`。这些图片和图标是应用模板时需要的素材；整页预览属于样张，放入 `references/page_layouts/<id>/`。

索引保留原 `layout_scope: page`、画布与页面类型等字段，增加 `mode: ppt-layout`、模板根目录与样张入口。新增样张只用于浏览，不作为导出内容。

模板选择仍是原 PPT 生成流程的输入；本资源目录不另行定义精简生成路线。

## 图片改造

当前登记 16 个图片改造风格，入口为 `image_styles/image_styles_index.json`。图片改造以用户当前参考图和描述为依据；以下为新增风格时的资源合约。

每个 `template.json` 保存一种可以应用到用户图片的规则，包括适用用途、构图、材质、主体保留要求、文字处理和常见误差。

- `id` 与索引键、样张的 `template_id` 一致。
- `mode` 固定为 `image-transform`；`input` 为 `user-image-required`。
- `variant` 仅区分内部处理形式，例如 `poster-layout`、`image-restyle`，不把图片改造拆成新模式。图片排版是独立的第三种模式，由 `workflows/image-layout/README.md` 定义，字体资源放在 `references/`。
- `aspect`、`slots`、`tags` 记录画面比例、可替换槽位和筛选词，供组织提示词时参考。
- `source_prompt` 保存原始风格的完整提示词，`prompt_assembly` 说明如何把主体与槽位替换成当前任务。
- `reference` 指向同 ID 的 `references/image_styles/<id>/sample.json`。
- 实际任务提示词根据用户输入动态组织，直接输出到聊天框，不维护成品提示词 `.md`。

海报排版也以用户图片为内容来源。样张可以展示视觉语言，但不能代替用户原图，也不能据此转为仅凭主题从零生图。

新增模板与样张后，同时更新本模式索引。资源发现只读索引，读取选中条目后再载入其规则与样张。

## 各模式共用的配色

`color_palettes/color_palettes_index.json` 发现 56 组配色；每组定义位于 `color_palettes/<id>/palette.json`，对应样张位于技能根目录的 `references/color_palettes/<id>/`。每组保留五色顺序、HEX/RGB 以及原标注和采样记录，不预设颜色角色。按需读取 [配色应用说明](../workflows/color-palette.md)，与版式和图片风格独立组合。
