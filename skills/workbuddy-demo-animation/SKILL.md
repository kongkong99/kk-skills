---
name: workbuddy-demo-animation
version: "1.0.0"
display_name: "WorkBuddy 演示动画"
display_name_en: "WorkBuddy Demo Animation"
description_zh: "根据任务描述制作 WorkBuddy 风格的任务运行模拟、提示词输入动画和图片结果展示，交付可编辑 HTML、截图或 MP4。用户要 WorkBuddy 教程动画、软件演示素材、模拟执行过程或提示词打字视频时使用；不用于实际操作 WorkBuddy。"
description_en: "Create WorkBuddy-style task simulations, prompt typing animations, and image result reveals from a task description. Deliver editable HTML, screenshots, or MP4 videos for WorkBuddy tutorials and illustrative demonstrations. This skill creates simulated visuals and does not operate WorkBuddy or verify real task execution."
description: 根据任务描述制作 WorkBuddy 风格的任务运行模拟、提示词输入动画和图片结果展示，交付可编辑 HTML、截图或 MP4。用户要 WorkBuddy 教程动画、软件演示素材、模拟执行过程或提示词打字视频时使用；不用于实际操作 WorkBuddy。
---

# WorkBuddy 演示动画

把一段任务描述转成可编辑的演示素材。动画展示的是设计的过程，不代表 WorkBuddy 已经真实执行了任务。

## 开始制作

从当前请求读取任务内容、交付形式和已有素材。已有信息不重复询问。未指定样式时使用模板的中性演示账号和可修改配色；未指定形式时交付 HTML，明确要视频时同时完成 MP4。只有缺少必要的任务内容或无法确定关键交付条件时才问。

- 运行过程：用 [任务界面模板](assets/workbuddy-demo.html)，展示消息、处理步骤、工具提示、产物和完成状态。
- 展示提示词：用 [输入动画模板](assets/workbuddy-prompt.html)，按时间逐字显示文本，留出完整阅读时间。
- 展示图片结果：用 [图片揭晓模板](assets/workbuddy-image-reveal.html)，展示缩略图、点击放大、停留和返回。使用真实提供的图片；模板的咖啡海报只是示例。

样式、字号、昵称、头像、时长和背景由本次任务决定，不要求固定配色、固定图片数量、人物位置或开场效果。三个模板均可独立使用。若同时需要口播剪辑、字幕和混音，可使用环境已有的编辑工具；已安装 `short-video-packaging` 时可按需配合。

## 制作流程

1. 根据任务组织少量有意义的状态变化，例如“收到任务 → 整理信息 → 展示产物”。步骤文字和时序与讲解一致，不编造真实工具调用、真实完成结果或未经证实的功能。
2. 将所选模板复制到输出目录，编辑其中的 JSON 配置。具体字段和布局限制见 [模板配置与运行](references/template-guide.md)。保留原始模板，修改副本。
3. 将任务文字作为文本处理。写入内嵌 JSON 时将 `<` 编码为 `\u003c`；不要将文本拼接成 HTML。图片使用本地相对路径或 data URI，交付时附上被引用的文件。
4. 调整布局和时序。文字需在目标尺寸读得清、完整显示；长提示词优先分段或分镜，不能通过裁切隐藏内容。复制模板后可编辑 CSS 和场景尺寸，以适配横版、竖版或方形输出。
5. HTML 可直接在现代浏览器预览。需要 MP4 时运行下面的渲染器，再检查成片。要截图时，在指定时间调用 `window.setSimulationTime(seconds)` 后截图。

默认在画面保留“模拟演示”标记。若请求明确要求无画面标记，可在交付说明中清楚说明模拟性质，同时删除副本中的标记；不能把动画描述为真实录屏或实际执行记录。

## 导出视频

在当前 Skill 目录执行，输入和输出使用实际路径：

```bash
python3 scripts/render_video.py /path/to/demo.html /path/to/demo.mp4 --fps 24 --width 1512 --height 886
```

竖版提示词或图片模板可用 `--width 1080 --height 1920`。脚本依赖 Python 3、Node.js 22+、Chrome/Chromium 和 FFmpeg（含 libx264），不需要第三方 JS 包。浏览器/编码器不在自动搜索路径时，用 `CHROME_PATH` / `FFMPEG_PATH` 指向可执行文件。自动发现以 macOS/Linux 常见路径为主，其他平台需要自行配置并验证。

渲染器只导出无声 MP4；需要配音、键盘声、点击声或音乐时，用当前环境的音视频工具另行同步混音。它会阻止远程 HTTP(S) 资源加载，字体和图片需使用本地文件或内嵌资源。缺少依赖时仍可交付 HTML，但明确说明视频尚未导出，不把源码当成已完成视频。

## 验证与交付

- 在目标尺寸检查开始、文字最长的时刻、面板变化、图片放大和结束；无重叠、裁切、丢图或误导性状态。
- 检查拖动进度与按时间定位结果一致，`window.SIMULATION_DURATION` 和 `window.setSimulationTime(seconds)` 可用。
- 视频需实际解码并检查时长、宽高、画面；声轨另行制作时需播放检查同步。
- 交付可编辑 HTML、所需本地素材，以及请求的截图/MP4。说明模拟性质、关键配置位置和未验证事项。

## 调用示例

- “做一个 WorkBuddy 整理会议纪要的 12 秒横版模拟演示，给我 HTML 和 MP4。”
- “把这段提示词做成紫色主题的逐字输入动画，字号适合手机观看。”
- “把这张实际生成的海报做成从缩略图点击放大的 5 秒演示素材。”
