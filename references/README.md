# 对应模板的样板样张

本目录保存两种模式下与模板对应的样板样张及必要说明。模板定义与可应用规则位于 `templates/`；执行说明位于 `workflows/`。

```text
references/
├── page_layouts/<id>/
│   ├── sample.json
│   └── preview.png
└── image_styles/<id>/
    ├── sample.json
    └── preview.<png|webp|jpeg|svg>
```

有效样张的 `<id>` 与对应模板 ID 相同。`sample.json` 的 `template` 指向技能根目录相对的模板路径，`preview` 指向当前样张目录内的效果图；`source` 记录平台、作者、原帖与发布日期。

- 单页 PPT 样张采用已有 PowerPoint 实际渲染，演示文案与素材不绑定未来作品。
- 图片改造样张用于说明排版或视觉风格，按实际来源标注 `preview_kind`；独立生成的示例不称作同一原图的改造验证。
- 存在授权或署名文件时随对应样张保留，并在 `sample.json` 注明。
- SVG 样张内的摄影内容应嵌入或具有明确、有效的包内引用；不得依赖临时附件目录。

16 组图片改造样张均取自原作者公开帖，只用于说明风格；`sample.json` 记录来源，原帖未提供改造前原片的条目不标为对照。

执行说明位于 `workflows/`，来源记录位于技能根目录 `provenance.json`。本目录不再混放资源发现索引或执行流程说明。

## 共用配色样张

`color_palettes/<id>/sample.json` 对应同 ID 配色定义，`preview.svg` 展示其五个正式色值；`color_palettes/overview.svg` 展示全部 56 组。样张记录源图片文件名、SHA-256 与可见署名，预览仅重绘色块和色值，不复制原图插画，也不依赖 `drafts/` 或 `reference-drafts/`。定义入口为 `templates/color_palettes/color_palettes_index.json`；应用方式见 [配色说明](../workflows/color-palette.md)。
