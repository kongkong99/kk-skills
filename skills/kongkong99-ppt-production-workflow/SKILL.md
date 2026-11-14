---
name: kongkong99-ppt-production-workflow
version: "1.0.0"
display_name: "讲稿与 PPT 协同制作"
display_name_en: "Script and Slide Production"
description_zh: "为演讲、培训、汇报或路演协同制作讲稿与整套 PPT：分析模板容量，规划逐页内容，生成可编辑 Excel 工单，再制作并核对 PPTX。用户提到按模板做 PPT、讲稿配幻灯片、逐页工单或整套演示文稿时使用；不用于只改单页或单纯润色文字。"
description_en: "Create coordinated speaker scripts and slide decks for talks, training, reports, or pitches. Analyze template capacity, plan slide content, generate an editable Excel production sheet, and produce and check PPTX files. Use for template-based presentations, scripts paired with slides, or slide-by-slide production planning; not for isolated slide edits or text polishing."
description: 为演讲、培训、汇报或路演协同制作讲稿与整套 PPT：分析模板容量，规划逐页内容，生成可编辑 Excel 工单，再制作并核对 PPTX。用户提到按模板做 PPT、讲稿配幻灯片、逐页工单或整套演示文稿时使用；不用于只改单页或单纯润色文字。
---

# 讲稿与 PPT 协同制作

先理解版式能承载什么，再共同设计讲稿和页面，用一页一行的 Excel 工单连接内容与制作。模板约束呈现方式，不决定事实或替代证据；放不下时拆页、分层或补充版式，不能为了凑槽位删除必要信息。

## 从这里开始

可直接接受这些请求，不要求用户知道技能名称：

- “用这份模板做一套 20 分钟的培训 PPT，附讲稿。”
- “我有大纲，先整理成逐页 Excel 工单，暂时不用出 PPT。”
- “按已修改的工单生成 PPTX，讲稿放到备注栏。”

先查看已有主题、大纲、资料、模板和工单。已有工单就回读；只要规划就交付规划；要成品则完成授权范围内的制作与验证。

## 输入与可选设置

只询问会实质改变结果、且无法从材料判断的信息。已给的时长、模板或风格不再询问。

| 信息 | 处理方式 |
| --- | --- |
| 主题与受众 | 保留用户观点与事实；主题不明时询问。受众可推断时标明假设。 |
| 时长或页数 | 按明确目标规划；都没有时给出暂定范围。互动、演示、问答是否计入按实际需求。 |
| 模板 | 有 PPTX 时先读并渲染查看；没有时用本包的 9 种版式定义建立设计。这些定义不是预制 PPTX 文件。 |
| 内容密度 | 默认一页一个要点；可选提词型或会后阅读型。密度影响页数，不改变事实完整性。 |
| 语言、品牌、比例、字体 | 按用户要求；未指定时用可用字体、16:9 和中性配色，披露默认值。 |
| 交付范围 | 可选讲稿、工单或整套 PPTX，允许只做其中一阶段。 |
| 审阅方式 | 用户要先看角度、骨架或工单时，在该点等待；已授权完整制作且资料齐全时连续完成，不另设多轮审批。 |

姓名、客户数据、Logo、截图、二维码来自用户或可核验来源。未使用的个人信息字段填 `/`；只有成品确实需要但缺失的字段才标 `【待补】`，不要强行索要个人资料。

## 1. 分析版式与写作约束

读取 [模板约束](references/template-constraints.md)，为版式登记 ID、用途、字段、容量和文本上限。渲染看图判断真实空间，不只依赖字符计数。脚本只有三个正文块，四栏以上布局需拆页或使用当前字段能表达的设计，并说明差异。

需要推断语气或组织角度时，读 [文案简报](references/copy-brief.md)。模板示例文案、城市、品牌或吉祥物只作线索，不是本次任务事实。明确要求优先于风格推断。

放不下时先保留语义：区分上屏摘要与讲稿细节、拆页、换合适版式；可重新归类，但不能硬合并必要步骤或分类。缺图表版式时新增图表版式，不能把数据论证换成未经证实的故事。

## 2. 协同规划讲稿和页面

读取 [讲稿与页面约束](references/script-constraints.md)，形成逐页骨架：页码、论点、证据、版式、屏幕标题、预计时长、素材来源。每页回答一个主要问题；术语在讲稿和页面中保持一致。

按语言和实际演讲速度估字数，预留演示与互动时间；时长与页数是规划值，需朗读或演练校正。内容优先于固定页时长或章节数量。

用户要求审阅时交付骨架；否则说明关键假设后继续。屏幕文字可比口语精练，但不能改动数字、专有名词、结论或证据含义。

## 3. 生成可编辑工单

读 [工单结构](references/order-schema.md)，组织 `title`、`templates`、`global`、`pages`。逐页讲稿写在“演讲者备注”；未使用字段填 `/`，必要缺口用 `{"todo":"缺什么"}`。

在本技能目录执行，输入输出路径替换成项目实际位置：

```bash
python3 scripts/build_order_xlsx.py build order.json -o 工单.xlsx
python3 scripts/build_order_xlsx.py check 工单.xlsx --strict --out pages.json
```

- `build` 校验字段、字数和容量；失败后修正内容结构或映射再重跑。
- `check --strict` 返回 0 表示无错误和待补；1 表示结构错误；2 表示仍有待补。
- 连续同版式、节奏点占比只是提醒，按内容判断，不机械换版式。
- 需要补素材或用户要求审阅时交付工单；否则它作为中间产物，继续制作。
- 用户已允许占位时，可用不带 `--strict` 的 `check --out` 导出，并披露保留项。不能把待补当作事实。

一份工单使用一个工作簿；在线协作时导入同一文件。用户修改工单后重新回读，不从旧对话覆盖新内容。

## 4. 制作 PPTX 并校对

用宿主现有幻灯片工具生成 PPTX；本包脚本不生成最终幻灯片，也不渲染图片。

1. 以最新 `pages.json` 和模板目录为依据填写版式、图片与讲稿备注。要改词或结构时先同步工单再导出。
2. 分批或逐页检查实际布局，保护字号、留白、对齐和可读性；文本溢出时修订页面，不以压小字号掩盖。
3. 执行：
   ```bash
   python3 scripts/build_order_xlsx.py check 工单.xlsx --pptx 最终.pptx
   ```
4. 渲染并目检全部页面，检查图表口径、图片比例、遮挡、溢出与备注。脚本只比对页数、标题/页序、空白页等，不能证明所有文本、视觉或事实正确。
5. 交付请求范围内的 PPTX、讲稿、工单，说明页数、估计时长和未验证项。没有 PPTX 生成或渲染能力时完成可做的部分，明确缺失能力，不宣称成品完成。

## 运行条件与资源

工单工具需要 Python 3.9+ 和 `openpyxl`；`check --pptx` 及完整自测另需 `python-pptx`。使用已有环境，缺依赖时在项目隔离环境安装，不修改全局 Python。幻灯片生成与渲染由宿主环境提供。

```bash
python3 scripts/build_order_xlsx.py --help
python3 scripts/build_order_xlsx.py demo --outdir ./demo
python3 scripts/build_order_xlsx.py selftest
```

`demo` 的项目复盘用于展示工单格式，不是用户事实、固定风格或默认演讲主题。

