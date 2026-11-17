# 对应模板的样板样张与共用排版资料

本目录保存单页 PPT-layout 与图片改造两种模板模式下与模板对应的样板样张，以及图片排版共用的字体与字号规范。模板定义与可应用规则位于 `templates/`；执行说明位于 `workflows/`。

```text
references/
├── page_layouts/<id>/
│   ├── sample.json
│   └── preview.png
├── image_styles/<id>/
│   ├── sample.json
│   └── preview.<png|webp|jpeg|svg>
├── typography_index.json
└── type_hierarchy.json
```

有效样张的 `<id>` 与对应模板 ID 相同。`sample.json` 的 `template` 指向技能根目录相对的模板路径，`preview` 指向当前样张目录内的效果图；`source` 记录平台、作者、原帖与发布日期。

- 单页 PPT 样张采用已有 PowerPoint 实际渲染，演示文案与素材不绑定未来作品。
- 图片改造样张用于说明排版或视觉风格，按实际来源标注 `preview_kind`；独立生成的示例不称作同一原图的改造验证。
- 存在授权或署名文件时随对应样张保留，并在 `sample.json` 注明。
- SVG 样张内的摄影内容应嵌入或具有明确、有效的包内引用；不得依赖临时附件目录。

16 组图片改造样张均取自原作者公开帖，只用于说明风格；`sample.json` 记录来源，原帖未提供改造前原片的条目不标为对照。

执行说明位于 `workflows/`，来源记录位于技能根目录 `provenance.json`。本目录不再混放资源发现索引或执行流程说明。

## 字体与字号规范

`typography_index.json` 与 `type_hierarchy.json` 是图片排版的共用参考数据，没有对应模板或样张：

- 字体池：23 款。默认只读宋 / 黑 / 等宽，用户可点名其他字体；基础 11 款记录族名、回退链、气质、适用、禁区，扩展 12 款为本机安装字体，记录实测覆盖率、定位与用法限制。覆盖率来自原参考草稿的 111 字样本，交付目标机器需重新实排核对。
- 字号体系：4 级字阶（100 / 40 / 32 / 20）、1 档行高 1.3、弱对比覆盖（55 / 38 / 25）；没有 7 级 / 3 档 / 4 档。

使用方式见 [字体与字号规范](typography.md)。扩展字库不随包发布，运行时不依赖原机器字体目录。

## 共用配色样张

`color_palettes/<id>/sample.json` 对应同 ID 配色定义，`preview.svg` 展示其五个正式色值；`color_palettes/overview.svg` 展示全部 56 组。样张记录源图片文件名、SHA-256 与可见署名，预览仅重绘色块和色值，不复制原图插画，也不依赖 `drafts/` 或 `reference-drafts/`。定义入口为 `templates/color_palettes/color_palettes_index.json`；应用方式见 [配色说明](color_palettes/README.md)。
