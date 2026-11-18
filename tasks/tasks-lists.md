# Single Page Design 改进任务清单

- 更新日期：2026-11-18（Asia/Shanghai）。
- 维护角色：评估 agent；文档状态：改进清单草案，范围与优先级待用户确认。
- 依据：2026-11-18 完成度评估，全部条目均有实测证据，见各任务“依据”列与 [§6 评估依据摘要](#evidence)。
- 编号规则：`IMP-<域>-NN`；域为 VCS（版本）/ BLD（导出）/ ENG（工程化）/ ARC（架构）/ PERF（性能体积）/ CONTENT（内容覆盖）/ DOC（文档规范）/ UX（展厅交互）/ CLEAN（清理）。
- 台账性质：本文件是过程记录，不随技能包发布；打包时按 [README.md](../README.md) 的排除清单剔除。
- 任务台账：日常执行与状态见 [20261118-tasks.md](20261118-tasks.md)；本清单只维护改进项定义，进度以台账为准。

## 1. 阅读与维护口径

本清单把评估结论转成可验收的改进项，不重复描述产品定位。产品定位、目录分工与三种模式见 [README.md](../README.md) 与 [SKILL.md](../SKILL.md)。

“本轮是否需要完成”指本次重构第一轮；标“否”的条目保留编号，不删除。优先级只表达阻塞关系，不表达工作量：

| 优先级 | 含义 |
| --- | --- |
| P0 | 不解决就无法安全重构，或核心交付不可用 |
| P1 | 不阻塞开工，但决定重构方案的形状 |
| P2 | 内容覆盖与一致性，可与重构并行 |
| P3 | 清理与优化，可在重构收尾后处理 |

状态沿用任务台账口径：待开始 / 进行中 / 待审核 / 已完成 / 阻塞 / 顺延 / 取消。本文件初版全部为“待开始”。

<a id="p0"></a>

## 2. 改进任务清单

### 2.1 阻断项（P0）

| 编号 | 任务 | 问题与目标 | 本轮是否需要完成 | 类型 | 状态 | 依据（实测） | 验收要点 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-VCS-01 | 提交展厅前端与配置模板，清理工作树 | 展厅三类浏览的重写只存在于工作树：`gallery/`（`index.html`、`app.js`、`styles.css`，共 33KB）完全未跟踪，`.env.example` 未跟踪，5 个文件已改未提交。目标是让重构有可回滚的已知好状态。 | 是 | 版本管理 | 待开始 | `git status` 实测：`?? gallery/`、`?? .env.example`、`M README.md`、`M SKILL.md`、`M references/color_palettes/README.md`、`M scripts/gallery.py`、`M scripts/single_page.py`；`HEAD == origin/feat/image-layout-mode`。 | `git status` 只剩忽略项；`gallery/` 与 `.env.example` 进版本库；提交前 `python scripts/attribution_guard.py` 仍 exit 0；提交后 `git log` 能定位到“展厅支持版式/配色”这一次变更。 |
| IMP-BLD-01 | 导出依赖缺失时给出可诊断降级 | 默认 `python` 缺 `libcairo-2.dll`，`import cairosvg` 抛 `OSError: no library called "cairo-2"`，导致展厅「导出这一页 PPTX」与 `single_page.py export` 同时报 `SVG preview unavailable`。目标是让缺失可被用户和测试识别，而不是玄学失败。 | 是 | 缺陷 | 待开始 | `cairosvg` 导入 traceback；`requirements.txt:114` 只锁 `CairoSVG>=2.7.0`，无原生库说明；实测把 `D:\anaconda3\envs\xishi\Library\bin` 前置到 PATH 后导出立即成功（exit 0，产出 1 页 16:9 PPTX）。 | 缺 cairo 时，启动与导出各给一条中文提示，写明缺什么库、怎么装；导出相关测试在缺库时 `skip` 而非 `fail`；补上 cairo 后 `init → 填字段 → export` 一次通过。 |
| IMP-ENG-01 | 建立最小测试与 CI | 244 个 py 文件、0 个测试文件、无 CI，任何重构都无法判断是否改坏。目标不是覆盖率，而是三条冒烟线。 | 是 | 测试 | 待开始 | `git ls-files` 无 `test_*` / `*_test.py` / `conftest.py`；无 `.github/`、无 `pyproject.toml`、无 pre-commit 配置。 | 三类测试落地并通过：①索引一致性（版式/风格/配色条目与磁盘逐一对应）；②`init → 填字段 → export` 冒烟（缺 cairo 时 skip）；③`/api/catalog` 与 `/api/select` 契约。CI 跑通，失败输出能定位到具体条目。 |
| IMP-BLD-02 | 明确导出产物语义 | 导出器自述是 “structured review deck”，产出带 12 个 full-frame placeholder，是模板复核脚手架；但 README 交付约定写的是“一页可编辑 PPT 与预览图”。两种承诺混用，用户会拿到不符合预期的文件。 | 是 | 决策 + 文档 | 待开始 | `scripts/template_preview_pptx.py:5`、`:261` 自述 review deck；`:385` 使用 full placeholder frames；实测导出 PPTX 18 个形状中 12 个为 `PLACEHOLDER`；[README.md](../README.md) 第 84–104 行按“成品页”描述交付。 | 二选一并写进 [README.md](../README.md) 与 [SKILL.md](../SKILL.md)：①把展厅导出定位为“复核脚手架”，成品页明确走完整 PPT 流程；②补一条真正的成品页导出路径。文档中不再同时出现两种承诺。 |

### 2.2 结构性重构（P1）

| 编号 | 任务 | 问题与目标 | 本轮是否需要完成 | 类型 | 状态 | 依据（实测） | 验收要点 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-ARC-01 | 拆分可选 PPT 生产线 | 单页技能背了整套演示文稿生产引擎：`workflows/` 12,293 个文件中 12,091 个是 vendored 图标，占跟踪文件 94%、17.9MB。目标是核心包轻装，完整流程按需挂载。 | 是（方向确认后） | 重构 | 待开始 | 依赖闭包实测：展厅+CLI 直接闭包 6/244 个 py，含导出子进程 76/244，其余 168 个只服务完整迁移流程（image_backends 17、pptx_to_svg 21、native_objects 17、source_to_md 8、tts_backends 7 等）。图标分布：tabler-outline 5,138 / simple-icons 3,675 / phosphor-duotone 1,518 / tabler-filled 1,055 / chunk-filled 641。 | 核心包（三模式 + 5 版式 + 16 风格 + 56 配色 + 展厅）可独立安装并跑通 IMP-ENG-01 全部测试；完整生产线以可选方式挂载且能力不减；核心包文件数与体积下降 ≥80%；`routing.md` 的“单页不得走 Quick”约束不被破坏。 |
| IMP-ARC-02 | 图片排版模式补最小实现或明确不可复现 | 第三种模式（一图一句）没有任何脚本、模板或校验器；字体数据无人读取，只能靠模型即兴执行，无法验证、无法回归。 | 待 OPEN-02 | 重构 / 文档 | 待开始 | 全库检索 `typography_index` 与 `type_hierarchy`：仅 6 个 md 引用（README、SKILL、references/README、references/typography.md、templates/README、workflows/image-layout.md），**无任何 .py/.js 读取**；`workflows/image-layout.md` 共 71 行纯说明。 | 二选一：①补最小脚本（读两份 JSON → 按版式排 SVG → 出图），纳入测试；②在 [SKILL.md](../SKILL.md) 与 [README.md](../README.md) 明示“对话内即兴执行、不承诺可复现”，并从可验证能力清单中移除。不允许维持现状。 |
| IMP-PERF-01 | 展厅预览改直出图片，去掉 base64 内联 | `/api/preview` 每次请求把 7 张图内联成 base64 重新编码，单次响应 19.9MB，切换作品明显卡顿且占内存。 | 是 | 性能 | 待开始 | `scripts/gallery.py:193-212` 的 `svg()` 内联逻辑；实测 `arc_perspective_cards` 预览响应 19,895,309 字节，其中 base64 载荷 19,889,128 字节，`data:image/*;base64,` 出现 7 次。 | 同一作品预览响应 <1MB；图片走 `/resource/` 直出并保留现有路径白名单；展厅切换版式/作品无可感知卡顿。 |
| IMP-PERF-02 | 导出开放图片优化开关 | 图片优化被硬编码关闭，无 CLI 开关，单页 PPTX 达 14.9MB，不便交付与传输。 | 是 | 性能 | 待开始 | `scripts/template_preview_pptx.py:382` `image_optimize=False` 硬编码；实测 `out.pptx` 14,903,382 字节（7 张原始图片字节全量内嵌）。 | 增加优化开关并接入 `single_page.py export`；开启后单页 ≤3MB，附优化前后对比图证明无可见劣化；默认行为在文档写明。 |
| IMP-ENG-02 | 补打包与运行说明 | 无打包配置；`requirements.txt` 7.7KB / 80 段注释，混合全部可选依赖，新环境无法判断“最少要装什么”。 | 否（可与 ARC-01 合并） | 工程化 | 待开始 | 无 `pyproject.toml` / `setup.py` / 安装脚本；`requirements.txt` 含 CairoSVG、fonttools、python-pptx 及大量可选后端依赖。 | 有“最小可运行依赖集”与安装说明，Windows 原生库要求单独成段；[README.md](../README.md) 安装章节与之一致。 |

### 2.3 内容与覆盖（P2）

| 编号 | 任务 | 问题与目标 | 本轮是否需要完成 | 类型 | 状态 | 依据（实测） | 验收要点 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-CONTENT-01 | 版式覆盖 3/9 页面类型 | 注册版式只覆盖 cover×1、toc×1、content×3；参考池按 9 类页面组织，章节、金句、数据、对比、流程、人物团队 6 类无模板。展厅只有 5 个可选项，用户要“数据页”就没有。 | 待 OPEN-03 | 内容 | 待开始 | `templates/page_layouts/page_layouts_index.json` 的 `page_types` 实测；本机草稿 `drafts/单页layout/README.md` 记录 49 张参考图按 9 类组织（未入版本库）。 | 二选一：①补 6 类各 1 个版式（含 `design_spec.md` + SVG + 样张 + 索引登记 + 通过 IMP-ENG-01 索引测试）；②在 [README.md](../README.md) 与展厅明确标注当前覆盖 3 类，措辞不再暗示版式库完整。 |
| IMP-DOC-01 | 清上游残留 | `.env.example` 与 `agents/openai.yaml` 仍指向 `ppt-master`，与本包名不符，新用户按它配环境会找错路径。 | 是（低成本） | 文档 | 待开始 | `.env.example` 查找顺序段写 `~/.ppt-master/.env`、`~/.agents/skills/ppt-master/.env`；`agents/openai.yaml`（159B）同源。 | 路径与包名对齐 `single-page-design`；全库不再出现 `ppt-master` 的**路径**（`LICENSE`、`provenance.json`、`attribution_guard.py` 中的**版权与来源声明**保留）。 |
| IMP-UX-01 | 展厅交互小缺陷 | `preview_kind` 后端已取但前端未用；“导出”轮询无超时，任务卡住时界面无限等待；鉴权失败只有通用提示。 | 否 | 交互 | 待开始 | `scripts/single_page.py:34-36` 新增 `preview_kind` 字段；`gallery/app.js:365-400` 的 `startExport` 轮询无上限；`scripts/gallery.py:314-315` 403 统一文案。 | 轮询超时给出明确失败与重试；`preview_kind` 用于区分“风格样张/原片对照”展示；鉴权失败提示可操作（如“请从展厅主页重新打开”）。 |

### 2.4 清理（P3）

| 编号 | 任务 | 问题与目标 | 本轮是否需要完成 | 类型 | 状态 | 依据（实测） | 验收要点 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-CLEAN-01 | 本地草稿 212MB 治理 | 本机工作目录 325MB，其中 `drafts/` 115.3MB、`reference-drafts/` 71.9MB、`output/` 24.7MB。三者均被 git 忽略，不影响发布，但影响重构期间的磁盘与备份。 | 否 | 清理 | 待开始 | `drafts/` 含 `got/` 51.2MB（含 node_modules 链接）、`单页layout/` 25.1MB、`city-wheel/` 13.2MB、`humanism-preview-profile/` 7.1MB（Chrome 扩展副本）；`reference-drafts/` 71.9MB。 | 先列“需长期保留 / 可删”清单并经用户确认再动；确认可删的部分删除后，正式模板与配色不依赖这些目录（[README.md](../README.md) 第 76–82 行已声明该边界）。 |
| IMP-CLEAN-02 | 复核 20MB 样张 pptx | 两个样张 pptx 占 20.5MB，是仓库里最大的两个跟踪文件。 | 否 | 清理 | 待开始 | `references/page_layouts/arc_perspective_cards/sample.pptx` 14.22MB、`city_wheel/sample.pptx` 6.31MB；被 `provenance.json`、`references/README.md`、两份 `sample.json` 与两份 `design_spec.md` 引用。 | 确认两文件在流程中的实际用途；若仅作存档，考虑移出包外或压缩后保留，并同步更新引用。 |

## 3. 待确认决策

以下四项决定 IMP-ARC-01、IMP-ARC-02、IMP-CONTENT-01 的方向，需要用户裁决后才能排期。

| 编号 | 事项 | 关联任务 | 需要确定的内容 | 影响 |
| --- | --- | --- | --- | --- |
| OPEN-01 | 单页是否保留完整 PPT 生产线 | IMP-ARC-01、IMP-ENG-02 | 保留则按“拆成可选子包”执行；不保留则直接裁剪 `workflows/pptx/` 与 168 个仅服务完整流程的脚本。 | 决定重构主线是“拆包”还是“裁剪”，也决定核心包体积目标。 |
| OPEN-02 | 图片排版是否补实现 | IMP-ARC-02 | 补最小脚本纳入测试，或明确其为对话内即兴能力、不承诺可复现。 | 决定第三种模式是否可验收。 |
| OPEN-03 | 版式补 6 类还是收敛措辞 | IMP-CONTENT-01 | 补模板（每类含规格+SVG+样张+登记）或调整 README 与展厅措辞。 | 决定内容工作量与用户预期。 |
| OPEN-04 | 是否建立 `tasks/` 台账目录 | 本文件后续维护 | 若要对齐 RailFlow 的 `/tasks` 体系（`tasks/README.md` + `tasks/YYYYMMDD-tasks.md`），需在 `D:\test` 下新建目录，须用户明确授权；否则沿用本单文件台账。 | 决定后续过程记录的落点与粒度。 |

## 4. 不纳入范围

| 编号 | 内容 | 边界 | 依据 |
| --- | --- | --- | --- |
| OUT-01 | 重写 `svg_to_pptx` 渲染层 | 本轮不替换上游渲染实现，只在其上补开关与诊断。 | IMP-PERF-02 的验收边界 |
| OUT-02 | 替换或剥离上游 PPT Master 流程 | 迁移流程与署名是包的既定前提，重构不改变来源与许可关系。 | [provenance.json](../provenance.json)、`scripts/attribution_guard.py` |
| OUT-03 | 展厅内文本编辑、拖拽排版 | 已在产品范围外确认。 | [README.md](../README.md) 第 46 行 |
| OUT-04 | 新增单页以外的交付模式 | 本轮只改进现有三模式与工程化，不扩产品面。 | [SKILL.md](../SKILL.md) 使用入口 |

## 5. 建议执行顺序

| 批次 | 任务 | 退出条件 |
| --- | --- | --- |
| A 止血 | IMP-VCS-01、IMP-BLD-01、IMP-ENG-01 | 工作树干净；缺 cairo 可诊断；三条冒烟线绿。此后任何改动都能回滚与验证。 |
| B 可用 | IMP-BLD-02、IMP-PERF-01、IMP-PERF-02、IMP-DOC-01 | 导出语义单一且文档一致；预览 <1MB；单页 ≤3MB；无上游路径残留。 |
| C 收缩 | IMP-ARC-01、IMP-ARC-02（待 OPEN-01/02） | 核心包可独立安装并通过批次 A 全部测试；第三种模式可验收或已如实降级。 |
| D 收尾 | IMP-CONTENT-01（待 OPEN-03）、IMP-UX-01、IMP-CLEAN-01/02、IMP-ENG-02 | 覆盖范围与文档一致；展厅缺陷清零；本地目录按确认清单治理。 |

批次 A 不完成，不建议开始批次 C——拆包过程会大量移动文件，没有测试和干净工作树无法判断搬坏了什么。

<a id="evidence"></a>

## 6. 评估依据摘要

2026-11-18 实测结论，供核对本清单的依据列：

| 项目 | 实测值 | 状态 |
| --- | --- | --- |
| 跟踪文件 / 工作树体积 / `.git` | 12,884 / 325MB / 112.7MB | 已核 |
| 版式 / 图片风格 / 配色 | 5 / 16 / 56 组×5 色=280 色位 | 全部解析成功，0 断链 |
| 字体 / 字阶 | 23 款（core 11 + extended 12）/ 4 级 | 一致 |
| 文档 | 207 个 md，0 个断链 | 已核 |
| 署名完整性 | `attribution_guard.py` exit 0 | 通过 |
| 展厅端到端 | catalog(5/16/56) → create → preview → save → export job | 除导出外全部通过 |
| 导出链路 | 补 cairo 后产出 1 页 16:9、18 形状、文字可编辑 | 代码正确，依赖缺失 |
| 测试 / CI / 打包 | 0 / 无 / 无 | 缺失 |
| 依赖闭包 | 展厅+CLI 6、含导出 76、其余 168 | 共 244 个 py |
| 预览响应 / 导出体积 | 19.9MB / 14.9MB | 偏大 |
| 安装状态 | `~/.dsh/skills/single-page-design` 为指向本仓库的 junction | 未提交改动已生效 |

**总体判断**：资源与内容层接近完成，工程化与验证层缺失。改进重点不是补功能，而是补可验证性、收缩体量、把导出的两种承诺收敛成一种。
