# 单页 PPT-layout 模式

本模式完整继承 PPT Simplify 的生成流程，仅限定交付为一页。用户在展厅选择的 layout 是原 Stage 1 的候选输入，不替代确认、安装或策划。

## 载入与路由

以根 `SKILL.md` 提供的技能根目录作为 `SKILL_DIR`；本文件和 `pptx/entry.md` 所在目录都不是技能根目录。工作项目放在技能包外，初始化时传入绝对 `--dir`；迁入代码已移除原仓库层级的项目路径假设。

1. 读取 [原入口纪律](pptx/entry.md)，保留原角色切换、术语、串行执行和确认规则。
2. 读取 [原路由](pptx/routing.md)，依请求选择对应的 Generate PPTX 运行时。单页 layout 加内容属于普通生成，读取 [Default Generate](pptx/generate-pptx.md)。不能因为页数、速度或已选 layout 自动进入 Quick；特殊来源仅在满足原 profile 前提时依原路由处理。
3. 只读取所选运行时及其明确触发的依赖，不同时加载其他顶层路线。迁入的上游其他流程文件仅用于保持依赖完整，不构成新的展厅模式。

## 模板与页数

当前可选单页模板的唯一发现索引是 `templates/page_layouts/page_layouts_index.json`，其 `template` 和 `reference` 指向原结构模板与对应样张。原 Confirm UI、注册和安装工具均已对接该目录；流程内部的其他模板种类保留空索引以保持原协议，未复制原整套演示模板集合。

保留原候选准备时机：按原步骤先形成沟通建议，再准备/展示模板候选；不要因样张已存在而提前制定具体页面方案。展厅选择的模板作为候选传入，仍由用户在 Stage 1 确认，安装成功后才进入 Stage 2。项目的最终页数与 §IX roster 均为 1，不自行加封面、目录或结束页；用户改要多页时说明当前技能范围。

## 原执行顺序

材料处理与必要研究 → 项目初始化 → 模板候选准备 → Stage 1 沟通及模板确认 → 模板安装 → Stage 2 方案与制作安排确认 → 完整 Design Spec / Lock 与原质量门 → 按需准备图片及图标 → Executor 与原 Live Preview → final SVG 质量门 → 后处理 → 原生 PPTX 导出及 postflight。

详细步骤以所选原运行时为准，不能把本段当作可跳步的简化脚本。单页依原规则不触发 P05 的早期 gate，仍必须执行 final gate。修改轮次沿用原 Revision Round，修正拥有该问题的源文件后重新检查、导出；不自动重启策划。

原 Confirm UI 的两阶段确认及用户回执真实性要求保留。浏览器未打开、用户明确要求聊天确认或明确委托时，依原 confirm-surface 分支处理；不得伪造真实用户回执。开发验证中的隔离 fixture 不作为实际作品的确认记录。

## 运行资源与输出

原规则位于 `workflows/pptx/guides/`，原技术资源位于 `workflows/pptx/resources/`；其相对链接及工具读取位置已同步。`references/` 保存两类模板及共用配色的样张。使用原项目管理、模板安装、素材准备、质量检查、finalize 与 svg_to_pptx 工具，不以 `single_page.py` 或展厅原型取代运行时。

依赖安装入口是根 `requirements.txt`。按该文件原有说明区分实际使用路径的依赖；图片 API、联网检索、语音等分支需要其对应凭据/服务，迁入不等于已配置外部服务。不得因缺少某分支依赖而跳过原失败恢复规则。

生成时按原步骤自动启动已迁入的 Live Preview，并报告实际 URL；保留对话驱动的内容修改。用户确认作品后交付一页可编辑 PPTX 与对应预览，披露实际生效的导出警告。尚未完成的样式展厅前端不影响使用原确认界面及实时预览完成 PPT 流程。


## 可选配色

需要从色卡库选色时，读取 [共用配色说明](color-palette.md)，从 `templates/color_palettes/color_palettes_index.json` 选择配色。保留配色编号与实际色值，按当前模式应用；用户既有品牌色、原片保留要求及原确认流程优先。
