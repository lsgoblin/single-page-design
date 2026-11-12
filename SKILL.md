---
name: single-page-design
description: >
  Select reusable single-page PPT layouts or transform a user-supplied image
  into a styled image composition. Use for single-page PPT design, photo
  restyling, collage, photo-based poster layouts, and photo-plus-artwork
  compositions. Browse paired template samples locally, take content and
  revision requests in chat, and update result previews. PPT generation must
  preserve the corresponding PPT Simplify workflow. Topic-only poster
  generation and full multi-slide deck production are outside this scope.
metadata:
  version: "0.4.0"
  copyright: "Copyright (c) 2025-2026 Hugo He"
  license: "MIT"
  official_repository: "https://github.com/hugohe3/ppt-master"
  sponsors:
    - "SPONSORS.md"
    - "SPONSORS_CN.md"
---

# Single Page Design

本技能只有两种模式：单页 PPT-layout、图片改造。用户在本机展厅浏览并选择模板，在对话中提供内容与修改要求，查看浏览器更新后的预览，再确认导出。

本包从 PPT Simplify / PPT Master v6.7.2 提取单页模板及导出依赖，是独立衍生技能；上游版权与 MIT 许可保留。`official_repository` 表示上游来源，不表示本衍生包由上游官方发布。运行不依赖原仓库、其他技能包或安装目录。

## 使用入口

以宿主提供的本文件绝对路径确定 `SKILL_DIR`。命令中的占位符须替换成该绝对目录，工作文件保存在用户的任务目录，不写回技能包。Python 命令示例用 `python`；宿主只有 `python3` 时使用等价命令。

调用提取的 PPT 工具前执行 `python3 "${SKILL_DIR}/scripts/attribution_guard.py"`。该检查保留上游署名、许可证与工具完整性；失败则报告，不绕过。

根据交付物只读取对应模式的说明和选中的模板、样张：

| 用户需要 | 读取 | 主要资源 |
|---|---|---|
| 单页 PPT-layout | [workflows/single-page.md](workflows/single-page.md) | `templates/page_layouts/page_layouts_index.json` |
| 用户图片改造与排版 | [workflows/image-transform.md](workflows/image-transform.md) | `templates/image_styles/image_styles_index.json` |

`templates/` 保存可复用、可选择、可应用的模板；`references/` 保存对应的样板样张及样张说明。同一模式下模板与样张使用相同 ID。执行说明放在 `workflows/`；来源记录在根目录 `provenance.json`。具体资源合约见 [templates/README.md](templates/README.md) 与 [references/README.md](references/README.md)。

已有素材和用户指定样式优先。海报、杂志等是图片改造内部的排版形式，必须以用户输入图片为内容来源，不单独开设主题生图模式。浏览器负责浏览、选择、结果预览，修改通过对话驱动。

## 共用配色资源

两种模式均可按需组合 [配色资源库](workflows/color-palette.md)。从 `templates/color_palettes/color_palettes_index.json` 发现 P01–P56 共 56 组五色配色，再读取选中条目的定义和样张；整体预览为 `references/color_palettes/overview.svg`。用户指定配色、品牌色和原片保留要求优先，具体映射与检查按配色说明执行。配色沿用原策划/确认节点，不增加制作模式。

## PPT 流程边界

单页 PPT 生成完全按照 `ppt-simplify` 对应流程执行，保留其路由、角色、策划确认、模板安装、素材准备、页面制作、检查和导出要求。只有一页或已选择 layout，均不构成进入 Quick 或跳过原步骤的依据。

当前包完成了模板资源和样张的目录对齐，尚未完整迁入原生成流程及其依赖。正式生成前必须完成该迁移；不要以现有 `single_page.py init/export` 或未完成的展厅原型替代完整生成流程。它们目前仅是底层工具或历史原型，不代表新的生成路线。

## 共同设计判断

- 先明确这页/这张图要让人看到什么、记住什么；用一个主要视觉焦点组织内容。
- 已提供的用途、比例、文案、原图与品牌要求直接沿用；只问影响结果且无法推断的信息。PPT 画布依原流程确认；图片比例按发布用途、输入图片和用户要求确定。
- 单页保持足够字号、清楚的层级和可解释的留白。复杂材质用于图片，准确文案优先用原生文本承载。
- 模板决定结构，图片风格决定画面表现。选择某种图片风格，不代表必须改变整个 PPT 的字体、底色或版式。
- 参考图用于识别构图、材质与保真要求，不将参考中的主体、文案、尺寸或上下对照形式绑定到以后所有任务。
- 不编造用户数据或将样张当成用户素材。图片改造缺少用户图片时，先取得图片；不得用库内样张冒充输入。PPT 演示素材的选用遵循原生成流程。

## 交付约定

- 要 PPT：一页 `.pptx` 和预览图；标题、正文、形状与可替换图片独立保留。说明哪些纹理或绘画细节为位图。
- 只要提示词：直接在聊天框输出可以使用的完整提示词，不创建提示词 `.md` 文件。
- 要生成/编辑图片：用当前宿主可用的图像工具执行，并展示成图；无可用工具时明确交付到提示词，不虚报已生成图片。
- 要组合结果：先生成适合页面比例与文字安全区的图片，再完成单页排版。准确标题优先在 PPT 中排，避免文字重复。
- 交付前检查实际渲染。修正遮挡、裁切、缺字、未替换字段和图层顺序；SVG 预览只能代表源画面，不能宣称等同于 PowerPoint 实际渲染。

## 包内资源维护

新增单页模板放在 `templates/page_layouts/<id>/`，包含结构规格、完整页面 SVG 和实际应用所需素材；样板样张放在 `references/page_layouts/<id>/`。更新单页索引中的模板与样张引用，保持相对引用和可编辑槽位。

新增图片改造模板放在 `templates/image_styles/<id>/template.json`，记录应用规则和用户图片要求；样板样张放在 `references/image_styles/<id>/`。在 `templates/image_styles/image_styles_index.json` 登记二者，不将样张作为实际制作输入。具体任务的成品提示词仍在聊天框动态组织。

`scripts/` 中包括提取的上游依赖和本项目工具/未完成原型。工具私有的 `scripts/assets/` 不属于展厅模板库。Sponsor 文件仅保留上游归属信息，不在正常设计中主动推介。模板发现使用 `templates/` 的两份模式索引；可选配色另读 `templates/color_palettes/color_palettes_index.json`，不回退到旧路径。
