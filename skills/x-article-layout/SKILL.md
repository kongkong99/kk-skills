---
name: x-article-layout
description: 用户丢来一段文字、想排成 X 长文（或公众号长文）时使用：按「每节一张图」的指南式排版分段、定动作小标题、标加粗、写清单，并默认用 Dan Koe 式黑白蚀刻版画风为封面和每节写隐喻生图提示词、生成配图、插到对应位置。
---
# X 长文排版（每节一图 · 黑白版画风配图）

参考的是 X 官方「creators 终极指南」那种排版：开头三步走、动作句小标题、每节结论先行、短清单、原话样例、硬数字、可抄样板、**每节一张配图**、结尾闭环加金句。

## 输入
用户给的一段文字（口述稿、草稿、语料都行）。可选：平台（默认 X 长文）、风格要求、是否要存进 X 草稿。

## 步骤

1. **只用原文里的事实。** 不编数字、案例、引语。原文没有硬数字或样板，就在交付时列出「建议补充」，问用户要，不要自己造。
2. **定标题。** 给 1 个主标题加 2 个备选。写法用「结果/身份 + 方法」，或者「我做了 X，发现 Y」。
3. **写开头（3 到 5 句）。**
   - 痛点：把麻烦拆成一串具体步骤或场景。
   - 承诺：这篇能帮读者省掉什么。
   - 信任：我自己真用过、用了多久、结果如何（只用原文里的）。
   - 转场：一句「下面按步骤说」。
4. **分节（通常 5 到 9 节）。** 每节：
   - 小标题是**动作句**（「把灵感变成选题」「让它当脚本教练」），光扫小标题就知道教什么。
   - 第一句就是这节的结论，加粗。
   - 正文 2 到 4 个短段，每段 1 到 3 句。
   - 能列的就列成清单，格式是「**标签**：一句解释」。
   - 有对话、反馈、报错的，直接引原话。
   - 节末标注 `【配图 N】`。
5. **加粗规则。** 每节最多加粗 2 处：结论句，加上一个关键数字或反常识点。不要整段加粗。
6. **硬数字和样板。** 全文至少保留 1 个硬数字（时间、钱、数量的前后对比），再加 1 个读者能照抄的拆解样板（例如「发生了什么 / 原因 / 教训」）。原文没有就列进「建议补充」。
7. **结尾。** 用一条流程链把全文串成闭环（A、B、C，然后重复），最后落一句能转发的金句。不要硬塞反问句，不放外链（X 正文外链会被限流）。
8. **配图提示词（每节一张，加封面一张）。** 默认画风是下面的「黑白蚀刻版画风」，全篇统一；用户指定别的风格时才换。
   - **先找隐喻，再写提示词。** 每节先写一句「这节观点 → 画面场景 → 为什么成立」，画面表现一个动作或关系，不是贴图标（别写「效率=钟表、认知=大脑」）。可选方向：
     - **未知、进入新阶段**：小人物面对巨大的森林入口或空旷空间。
     - **信息过载、理解**：人和庞大书库、知识空间的尺度对比。
     - **策略、选择**：棋局、岔路、局部和全局的对比。
     - **能动性、创作**：手和工具、独自工作的人。
     - **风险、不确定**：小船和漩涡、人站在深渊边。
     这些只是词汇库，全篇不要每张都是「小人+黑洞」，换着用工作台、棋盘、手部特写、长廊等。
   - **固定视觉语言**：纯黑白高反差，灰阶全靠排线、交叉排线和点描；19 世纪书籍插画、木口木刻或铜版蚀刻质感；大片纯黑负空间加精细亮部；细节集中在主体，缩到手机宽度轮廓仍清楚。
   - **规格**：单张、不拼接、16:9。正文配图不放字；封面默认也不放字，如需标题另外排版叠加。不出现真实 logo、真人肖像（除非用户给照片）、假数据或伪造的产品界面。
   - **需要讲清操作或证据的节**（步骤、后台数据、报错），在交付时建议用户改用真实截图或图解，AI 图作为备选，不要拿生成图冒充证据。
   - **通用模板**（填满槽位、去掉花括号后直接粘贴）：

     A 16:9 horizontal monochrome editorial illustration depicting {具体主体、位置与动作}. {主体与环境的关系，或一个超现实转换，用一个可见场景表达这节观点}. Composition: {视角、主体大小、视觉中心与负空间}. Nineteenth-century wood engraving and copperplate etching, precise pen-and-ink contours, dense cross-hatching and stippling, white ink-like highlights against deep pure-black shadows, tonal transitions made of engraved lines rather than smooth gradients. {光源及照亮的部位}. {情绪}. A clear silhouette at thumbnail size, selective intricate detail. No headline, no captions, no readable lettering, no logo, no watermark. No color, photography, 3D rendering, glossy surfaces, soft airbrush shading, neon glow, cartoon or anime.

   - **示例**（风险/不确定）：A 16:9 horizontal monochrome engraved illustration. A tiny human standing in a small rowboat on the left inner slope of a vast swirling ocean vortex. The water spirals diagonally into a huge off-center black abyss to the right. Dense white stippling and curved etched lines describe turbulent waves; the boat reads as a simple dark silhouette against a bright band of foam. Strong scale contrast, nineteenth-century book engraving, precarious but determined mood. No lettering, logos, watermark, color, photography, 3D, glow, soft airbrush or anime.
   - 这套画风是根据 Dan Koe 公开文章封面归纳的近似风格，不是他本人的原始提示词；不要复制他的原图构图，也不要对外声称「同款」。
9. **生成图片。** 用图像生成工具（16:9）逐张生成，文件名用 `cover.jpg`、`sec-01.jpg`… 对应编号。生成后检查，有错字、畸形、和内容对不上的就重做。按版画风纠偏：太像照片就加「all midtones constructed from engraved marks, no photographic texture」；太挤就删辅助物件、扩大纯黑负空间；太平就加尺度对比或前中后景；太恐怖就去掉骷髅、血腥。
10. **交付。**
    - 一个排好版的 Markdown 文件，`【配图 N】` 处写上对应图片文件名。
    - 按顺序发出封面和每节配图，每张注明插在哪一节后面。
    - 每张图的提示词附在文件末尾，方便自己重画。
    - 「建议补充」清单（缺的数字、样板、要核实的事实）。
    - 如需存进 X 长文草稿：小标题用 header-two，清单用 unordered-list-item，配图位置保留一行 `【配图 N：文件名】`；图片和封面需要在 X 编辑器里手动上传。只存草稿，绝不替用户发布。

## 自查清单
- 小标题都是动作句吗？
- 每节第一句是结论吗？
- 每节都有一张图吗？每张图都是一个隐喻场景，而不是重复同一个构图？
- 画风全篇统一（默认黑白蚀刻版画），没有彩色、照片感、3D 和图中文字？
- 有没有编造的数字或引语？
- 加粗是不是每节不超过 2 处？
- 结尾有闭环加金句，没有假反问、没有外链？
