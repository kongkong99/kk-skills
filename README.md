# kk-skills

个人 Skills 集合：把可重复的工作方法整理成可维护、可复用的独立 Skill。

## 通用公开版

首次使用建议从下面三个独立技能开始。它们使用通用默认值，支持自己的素材、品牌和输出要求；原有个人版保留。

| Skill | 用途 |
| --- | --- |
| [ppt-production-workflow](skills/ppt-production-workflow/SKILL.md) | 按模板与演讲目标协同设计讲稿、Excel 工单和 PPTX。 |
| [short-video-packaging](skills/short-video-packaging/SKILL.md) | 剪辑口播并制作字幕、画面、界面演示和音效包装。 |
| [workbuddy-demo-animation](skills/workbuddy-demo-animation/SKILL.md) | 制作可编辑的 WorkBuddy 模拟教程画面、提示词动画与演示视频。 |

安装、依赖和使用示例见 [公开版使用说明](PUBLIC_SKILLS.md)。

## 原有技能

| Skill | 用途 |
| --- | --- |
| [product-benchmark-tasks](skills/product-benchmark-tasks/SKILL.md) | 分析对标产品，把观察结果转成可验证的执行任务。 |
| [attention-driven-storyboard](skills/attention-driven-storyboard/SKILL.md) | 围绕观众注意力和内容推进，策划知识短视频及其分镜。 |
| [knowledge-video-storyboard](skills/knowledge-video-storyboard/SKILL.md) | 把已剪辑口播或逐字稿转换成知识分享视频分镜。 |
| [interface-explainer-motion](skills/interface-explainer-motion/SKILL.md) | 将口播转为同步的界面演示、动画图解和可编辑视频。 |
| [workbuddy-simulator](skills/workbuddy-simulator/SKILL.md) | 生成可编辑的 WorkBuddy 模拟界面、Prompt 卡片与图片揭晓动画。 |
| [chat-screenshot-demo](skills/chat-screenshot-demo/SKILL.md) | 生成微信风格长屏聊天案例与滚动视频，含 10 个整头像打码模板。 |
| [x-article-layout](skills/x-article-layout/SKILL.md) | 将长文整理为分节图文排版，标注加粗、生成配图提示词并插入 AI 配图。 |
| [ppt-order-workflow](skills/ppt-order-workflow/SKILL.md) | 讲稿与 PPT 相互约束：写逐字稿前先读模板排版，讲稿按版式限制组织，PPT 由讲稿决定，生成工单后逐页出片。 |

## 结构

每个 Skill 有自己的目录和 `SKILL.md`。需要时，在对应目录中添加 `references/`、`scripts/` 或 `assets/`，并保持引用路径可移植。

## 使用与维护

1. 在支持 Agent Skills 的工具中，按该工具的说明安装或链接所需的 Skill 目录。仓库本身不会自动启用所有 Skill。
2. 在此仓库维护正式版本，修改后提交 Git，避免多个副本分别修改。
3. 新增 Skill 时，复制完整目录并在上面的目录表中登记；与具体项目紧密绑定的 Skill 可留在项目仓库。
4. 提交前检查是否包含密钥、个人或客户资料，以及第三方内容的来源和授权。

不同工具的安装路径和加载方式可能不同，请以工具当前文档为准。

