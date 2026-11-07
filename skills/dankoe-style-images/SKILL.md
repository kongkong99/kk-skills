---
name: dankoe-style-images
description: 给长文按 Dan Koe 风格配图：提炼观点和视觉隐喻，生成黑白蚀刻版画封面提示词，并判断正文哪里需要图解或真实截图。
---
# 长文配图：黑白版画封面 × 有用的正文图

## 边界
这是根据公开作品归纳的视觉方法，不是 Dan Koe 本人公开的原始提示词。不要声称还原了他的工具、模型、参数或完整制作流程。只借鉴通用视觉语言，不复制原图构图、署名或人物肖像。用户只要提示词时，不自动生成图片；用户明确要求图片后才调用生图工具。

## 1. 先读文章，别先挑画风
输出四项：核心观点一句话；核心冲突；情绪（探索、专注、未知、突破、反思）；读者看完该做什么。没有正文时请提供标题和核心观点即可，不编造文章事实。

## 2. 分开处理封面与正文
- 封面：一张完整的概念场景，负责气氛与主题。默认横版 16:9，无标题、无署名。并非必须所有场景都有超现实变形：专注工作的真实场景也成立。
- 正文：不执行“每节必须一张 AI 图”。概念关系复杂用图解，操作与证据用真实截图，抽象转折确有帮助时才加隐喻图。没有信息增益就不加。
- 图解放在相关定义/解释之后；操作截图紧跟对应步骤；证据图跟随被证明的断言。不要拿生成图伪装数据、产品界面或实证。
- 图解和截图允许文字与其他比例，不强制版画化。准确文字和连线优先用 SVG、排版软件或代码，不交给生图模型猜。
- 同一张封面可能再次出现在文末推荐卡片中；去重后统计，不把它当另一张正文创作。

## 3. 给观点找一个能看懂的隐喻
先给三个方案，每个写“观点 → 场景 → 为什么成立”。优先选一个主要关系，而非堆主题符号：
- 未知/进入新阶段 → 小人物面对巨大森林入口或空间。
- 信息过载/理解 → 人与庞大知识空间的尺度关系。
- 策略/选择 → 棋局、路径或局部与全局的对比。
- 能动性/创作 → 手与工具、独自工作的人。
- 风险/不确定性 → 船与漩涡、人物与深渊。
这些是可选词汇，不是每篇必备图标。画面要表现动词和关系，不能只是“效率=钟表，认知=大脑”。

## 4. 固定视觉语言，变化内容
- 纯黑白、高反差；灰阶来自密集排线、交叉排线与点描。
- 19 世纪书籍插画、木口木刻/铜版蚀刻、钢笔墨线；不是灰度照片。
- 大面积黑暗与精细亮部共存；主体轮廓缩小后仍清楚。
- 细节集中在有意义的主体上，不把整张图填满等密度噪声。
- 可以居中，可以偏置；不要误把“禁止居中”当规律。
- 尺度对比常有用，但并非必须“小人+巨大黑洞”。保留工作室、棋盘、手部特写等变化。
- 主封面默认不放字，不必机械预留一半面积给标题；如需后期加字，另做排版版式。

## 5. 通用提示词模板
填写所有槽位，交付时不要保留花括号。英文可直接粘贴：

A 16:9 horizontal monochrome editorial illustration depicting {具体主体、位置与动作}. {主体与环境的关系或一个超现实转换，用一个可见场景表达观点}. Composition: {视角、主体大小、视觉中心与负空间}. Nineteenth-century wood engraving and copperplate etching, precise pen-and-ink contours, dense cross-hatching and stippling, white ink-like highlights against deep pure-black shadows, tonal transitions made of engraved lines rather than smooth gradients. {光源及照亮的部位}. {情绪}. A clear silhouette at thumbnail size, selective intricate detail. No headline, no captions, no readable lettering, no logo, no watermark. No color, photography, 3D rendering, glossy surfaces, soft airbrush shading, neon glow, cartoon or anime.

如果使用带独立参数的模型，在确认当前工具支持后再添加横版参数；不要把某模型参数当作所有工具通用语法。

## 6. 五条完整示例（研究性近似，不是原提示词）
以下用公开作品里的可见场景检验提示词是否足够具体；正式创作应更换场景、角度及物件，避免逐像素临摹。

### A. 一个人承担完整创作工作
A 16:9 horizontal black-and-white editorial wood engraving. Rear view of a solitary writer in a textured wool sweater, seated centrally at a crowded wooden desk in a dark study. A shaded desk lamp stands on the left; a mechanical typewriter sits on the right; scattered manuscript pages and drawing tools surround the writer. The lamp illuminates papers and the shoulders, leaving the room in deep black shadow. Dense engraved linework, cross-hatching, crisp white highlights, nineteenth-century book illustration, quiet concentration. No headline, readable text, logo, watermark, color, photography, 3D render, airbrush or cartoon.

### B. 从熟悉世界走进未知
A 16:9 horizontal black-and-white wood engraving. A small lone traveler wearing a backpack stands with their back to the viewer, slightly right of center, on a pale forest path. Tall tree trunks, ferns and densely stippled foliage form an arch around an enormous unlit opening ahead. The entrance is an irregular pure-black absence rather than a glowing portal. Ground-level wide view, tiny human versus vast forest, detailed botanical contours and cross-hatching, bright foreground and deep shadow, quiet uncertainty and curiosity. No text, logo, watermark, color, photography, 3D render, soft gradient or cartoon.

### C. 在不确定性中行动
A 16:9 horizontal monochrome engraved illustration. A tiny human standing in a small rowboat on the left inner slope of a vast swirling ocean vortex. The water spirals diagonally into a huge off-center black abyss to the right. Dense white stippling and curved etched lines describe turbulent waves; the boat reads as a simple dark silhouette against a bright band of foam. Strong scale contrast, tightly controlled black-and-white tonal rhythm, nineteenth-century scientific-fantastical book engraving, precarious but determined mood. No lettering, logos, watermark, color, photography, 3D, glow, soft airbrush or anime.

### D. 知识不是无限收藏
A 16:9 horizontal black-and-white editorial engraving. A solitary small figure seen from behind stands near the bottom center inside a gigantic cylindrical library. Curving shelves stacked with books rise around the entire room, loose volumes scattered on the floor. High overhead, concentric engraved textures surround a perfectly dark circular opening; its bright white rim guides attention upward without digital glow. Wide low-angle composition, human dwarfed by accumulated knowledge, precise pen contours, layered cross-hatching, wood engraving texture, contemplative and overwhelming. No readable book titles, caption, logo, watermark, color, photo, 3D render or smooth shading.

### E. 把心智作为可运用的工具
A 16:9 horizontal monochrome editorial copperplate engraving. Close-up of a large open human hand entering from the right, palm facing upward and fingers curving toward the left foreground, carefully supporting an anatomically recognizable human brain. The brain sits in the upper-left and center of the frame; the sleeve recedes to the right into a completely black background. Bright directional light reveals folds, skin creases and precise hatching. Bold silhouette, strong perspective, detailed etched lines, nineteenth-century anatomical book illustration, thoughtful rather than macabre. No blood, gore, text, logo, watermark, color, photography, 3D render, airbrush or cartoon.

## 7. 输出结构
1. 一句话配图策略：为什么选这些位置，不是平均分配。
2. 配图清单：位置｜目的｜图种｜比例｜隐喻｜与原文关系。
3. 每张可复制完整提示词，必要时附负面词。
4. 如获明确生图要求，先试一张；检查后只改变一个维度再出第二张。不要声称“本人同款模型”或“精确复现”。

## 8. 自检与纠偏
- 不看标题能否辨认主体？看完标题能否理解关系？
- 画面是否表现观点，而不是仅有漂亮的黑白纹理？
- 缩到手机宽度是否还看得清？
- 高光是不是线条/点描，而不是照片转灰或油亮 3D？
- 是否无不必要文字、假证据和水印？是否每张都在重复黑洞？
- 太像照片：补充“all midtones constructed from engraved marks, no photographic texture”。
- 太拥挤：减少辅助物件，扩大纯黑负空间，保留一个主要关系。
- 太平：增加尺度对比、前中后景或方向明确的动作，而非继续加细节。
- 太恐怖：去骷髅、触手、血腥，保留哲学性与探索感。

## 研究依据与置信度
公开抽样：future/proof / Dan Koe，2026 年 7–11 月十二篇文章的封面元数据及公开正文。可直接看到黑白版画封面与功能性截图/图解并存；不能由视觉判定每张都由 AI 生成。第三方工具盘点提及 Midjourney 与 Figma，但不等于作者本人确认每张的流程。本技能中的提示词为独立逆向推测，不是泄露或官方原词。
参考：
- https://letters.thedankoe.com/archive
- https://letters.thedankoe.com/p/the-most-lucrative-ai-business-to
- https://letters.thedankoe.com/p/the-influencer-is-dead-the-age-of
- https://letters.thedankoe.com/p/you-need-to-be-delusional-if-you
- https://letters.thedankoe.com/p/how-to-remember-everything-you-read
- https://letters.thedankoe.com/p/the-most-profitable-skill-of-the
- https://toolfinder.com/stacks/dan-koe （第三方，工具归属未独立确证）
