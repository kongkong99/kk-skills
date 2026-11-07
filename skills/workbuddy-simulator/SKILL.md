---
name: workbuddy-simulator
description: 根据任务内容生成模拟 WorkBuddy 正在运行的可编辑教程画面或演示视频。适用于 WorkBuddy 界面复刻、任务执行过程演示和教学素材制作；不用于实际操作 WorkBuddy 或伪称真实执行记录。
---

# WorkBuddy 任务运行模拟

用用户提供的任务内容制作 WorkBuddy 风格的动态教程画面。默认直接制作可播放、可修改的本地 HTML；用户希望视频、成片或没有指定形式但明显用于视频教程时，同时生成 MP4。用户仅提供任务描述时，合理推导标题、步骤和展示内容，不必追问；按用途选横版，用户指定尺寸、时长或细节时遵从。

用户需要突出展示或逐字输入 prompt 时，可使用独立的 [WorkBuddy 提示词窗口模板](assets/workbuddy-prompt.html)：参考 Jeff 视频的深色圆角大卡片、上方 WorkBuddy 标识、分段文字与发送按钮，而非把它当作真实软件截图。修改其中 `prompt-config` JSON 的 `prompt`、`duration`、`typingStart`、`typingEnd`；对中文和换行按时间逐字显示，预留阅读停留。长文拆页或调整文字与布局，禁止让文字被裁切。模板支持预览、暂停、拖动进度，也实现 `window.setSimulationTime(seconds)` 和 `window.SIMULATION_DURATION`，可用现有渲染脚本生成无声视频；如成片需要打字、点击或镜头音效，在编辑器中另加并混音。保留明显的「模拟演示」标记，发送按钮仅为演示。Jeff 风格的音效和编排可配合 interface-explainer-motion skill。

## 工作流

1. 读取 [界面与运行参考](references/界面与运行参考.md)，原始截图和视频不包含在公开版本中，必要时使用用户提供的截图。素材是 WorkBuddy 5.9.3 的单次样本，不等于所有版本及任务的精确行为。默认左上显示 macOS 红黄绿窗口按钮，不绘制截图采集期间出现的紫色电脑控制标识。
2. 围绕任务编写简洁、可读的模拟时间线，默认从用户消息已提交的状态开始，随后展示处理或思考；用户需要输入和点击发送的动画时再补做。时间线可包括与任务相关的步骤、可选的工具/产物面板和结果状态。步骤和产物用虚构示例；界面清楚标记「模拟演示」，不要把推测结果说成真实运行结果。账户昵称默认使用「示例用户」，可按用户要求更换；不要照搬截图中的历史对话、个人路径和任务内容。
3. 基于 [可编辑模板](assets/workbuddy-demo.html) 生成独立 HTML，复制模板后编辑 `<script id="demo-config" type="application/json">` 中的 JSON：`title`、`prompt`、`model`、`profileName`（可改账户昵称）、`pinned`、`tasks`、`duration`（秒）和 `events`；事件格式为 `{"at": 秒数, "type": "status|tool|text|artifact|panel|complete", "text": "内容"}`。按时间升序安排事件；写入 JSON 前将 `<` 编码为 `\u003c`，避免用户文本破坏脚本标签。保留播放、暂停、重播和按时间定位接口；自行调整布局、文案、节奏和尺寸，确保文字不溢出。保留模板中按真实界面复刻的图标与头像，不用 Unicode 字符或 emoji 充当工具栏、导航、WorkBuddy 头像、模型及账户图标。用户指定截图时输出所需状态的高清图；需要视频时使用 [视频渲染脚本](scripts/render_video.py)；例如从本 Skill 目录运行 `python3 scripts/render_video.py /绝对路径/演示.html /绝对路径/演示.mp4 --fps 12`。脚本需要本机 Node 22+、Chrome/Chromium 和 ffmpeg，默认 1512×886，其他比例可用 `--width`、`--height` 指定；也可用其他本地动画或视频工具完成导出。用户明确要求成片时不要只交付代码或方案。
4. 在实际输出中检查开头、运行中、工具/面板变化和结尾；依据文字参考和用户提供的截图核对左上工具栏、侧栏导航、WorkBuddy 头像、右上工具栏、模型与账户区域的图形、布局和大小，再检查内容与任务的对应关系。验证生成的视频可解码、时长和尺寸正确。交付文件和可编辑源，并说明模拟性质和受原始样本限制的细节。

公开版本不包含原始截图；用户提供的截图可能包含个人信息，不要直接作为最终底图或随成品发布。默认昵称可替换。用户要求的外部发布、实际执行或数据连接按具体授权处理。
