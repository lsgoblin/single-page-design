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

`<id>` 与对应模板 ID 相同。`sample.json` 的 `template` 指向技能根目录相对的模板路径，`preview` 指向当前样张目录内的效果图。

- 单页 PPT 样张采用已有 PowerPoint 实际渲染，演示文案与素材不绑定未来作品。
- 图片改造样张用于说明排版或视觉风格。已有金毛参考包含原图/结果对照；其余条目按实际情况标注为风格参考，不将独立生成的示例说成同一原图的改造验证。
- 存在授权/署名文件时随对应样张保留，例如 `minimal-zine/LICENSE.txt`。
- SVG 样张内的摄影内容应嵌入或具有明确、有效的包内引用；不得依赖临时附件目录。

当前图片改造样张并非每项都具有可单独读取的原图与结果；后续补齐真实对照时在 `sample.json` 明确记录。本轮只整理已有样张，不新增生图任务。

执行说明位于 `workflows/`，来源记录位于技能根目录 `provenance.json`。本目录不再混放资源发现索引或执行流程说明。
