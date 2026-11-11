# 可复用模板资源

本目录保存两种模式下可复用、可选择、可应用的模板资源。`references/` 中同 ID 的目录保存对应样板样张。

| 模式 | 模板位置 | 发现索引 | 对应样张 |
|---|---|---|---|
| 单页 PPT-layout | `page_layouts/<id>/` | `page_layouts/page_layouts_index.json` | `references/page_layouts/<id>/` |
| 图片改造 | `image_styles/<id>/template.json` | `image_styles/image_styles_index.json` | `references/image_styles/<id>/` |

表中的 `references/` 路径相对技能根目录。索引的 `template`、`reference`、`preview` 字段也均为技能根目录相对路径，不依赖技能安装位置。

## 单页 PPT-layout

保留原 `ppt-simplify` 的单页包结构：`templates/design_spec.md`、完整页面 SVG，以及按需携带的 `images/`、`icons/`。这些图片和图标是应用模板时需要的素材；整页预览属于样张，放入 `references/page_layouts/<id>/`。

索引保留原 `layout_scope: page`、画布与页面类型等字段，增加 `mode: ppt-layout`、模板根目录与样张入口。新增样张只用于浏览，不作为导出内容。

模板选择仍是原 PPT 生成流程的输入；本资源目录不另行定义精简生成路线。

## 图片改造

每个 `template.json` 保存一种可以应用到用户图片的规则，包括适用用途、构图、材质、主体保留要求、文字处理和常见误差。

- `id` 与索引键、样张的 `template_id` 一致。
- `mode` 固定为 `image-transform`；`input` 为 `user-image-required`。
- `variant` 仅区分内部处理形式，例如 `poster-layout`、`image-restyle`，不增加第三种模式。
- `reference` 指向同 ID 的 `references/image_styles/<id>/sample.json`。
- 实际任务提示词根据用户输入动态组织，直接输出到聊天框，不维护成品提示词 `.md`。

海报排版也以用户图片为内容来源。样张可以展示视觉语言，但不能代替用户原图，也不能据此转为仅凭主题从零生图。

新增模板与样张后，同时更新本模式索引。资源发现只读索引，读取选中条目后再载入其规则与样张。
