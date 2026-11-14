# 模板配置与运行

这组模板用于说明 WorkBuddy 风格的交互。任务界面布局参考早期桌面版样本，不能作为当前版本精确 UI 或全部功能的证明。需要匹配具体版本时，依据本次提供的截图调整。公开包不依赖作者电脑上的截图、个人素材或编辑项目。

三个模板的字段按下文分别配置，并非共享同一套 JSON。任务界面支持账号昵称和头像；输入动画支持可选页眉昵称和顶部标识；图片揭晓只支持标识，不提供账号昵称字段。

## 任务界面：`assets/workbuddy-demo.html`

编辑 `<script id="demo-config" type="application/json">`：

| 字段 | 用途 |
| --- | --- |
| `title`、`prompt` | 任务名和用户消息 |
| `model`、`version` | 演示模型名与界面版本文字，默认标为示意 |
| `profileName`、`profileAvatar` | 昵称及可选本地/data URI头像；空头像使用通用圆形图案 |
| `accentColor`、`accentSoft` | 强调色和浅背景色 |
| `fontScale` | 字号系数，默认 1；建议 0.75–1.5，改变后检查溢出 |
| `pinned`、`tasks` | 示例侧栏任务名列表 |
| `duration` | 总时长，秒 |
| `events` | 时间顺序事件，见下例 |

事件格式：`{"at": 3, "type": "text", "text": "正在整理待办事项"}`。
支持 `status`、`tool`、`text`、`artifact`、`panel`、`complete`。`artifact` 会同时显示产物面板；`panel` 只打开面板。任务内容应为明确的演示文本或本次获准使用的内容。

任务界面默认约 1.71:1 宽屏布局。竖版可用上下留白作为构图，或修改 `.shell`、侧栏和面板 CSS；仅改变导出宽高不会自动重排成手机 UI。

## 输入动画：`assets/workbuddy-prompt.html`

`prompt-config` 提供 `prompt`、`duration`、`typingStart`、`typingEnd`。`fontSize` 是提示词字号 CSS 值，例如 `clamp(24px, 4vw, 48px)`；`accentColor` 设置示意标识和强调色；`backgroundColor` 设置背景，`starBackground` 可开启星点（默认关闭）。`brandImage` 可替换顶部标识，空值用通用 W 图案。

`profileName` 为可选页眉昵称，例如 `"Demo Team"`。默认空字符串，不显示昵称；非空时显示在左上角，与右侧模拟标记分开。昵称用 `textContent` 写入，仅作文字显示。此模板没有独立账号头像字段，`brandImage` 替换的是顶部标识。

提示词卡片是演示版式，发送按钮无真实功能。确保 `0 <= typingStart < typingEnd < duration`，为长文增加时长或拆分卡片。字号是可编辑起点，不能以模板尺寸代替输出检查。

输入模板提供 `window.validateSimulation()`，检查完整提示词、可选页眉昵称是否溢出及时间区间。渲染器在导出前调用此检查；发现溢出会中止并给出原因，先缩短昵称、拆分提示词或调整布局再导出。它不代替其他元素的目检。

## 图片揭晓：`assets/workbuddy-image-reveal.html`

`image-reveal-config` 提供：

- `imageSrc`：本地相对路径或 data URI。空值使用包内 SVG 示例海报。
- `prompt`、`statusText`：界面文案。
- `duration`、`clickAt`、`zoomAt`、`zoomDuration`、`returnAt`、`returnDuration`：秒数。
- `accentColor`、`backgroundColor`、`starBackground`：强调色、背景色与可选星点。
- `brandImage`：可选替换标识。

默认 4 秒只是演示节奏。保证点击、放大、停留、返回完整落在总时长内，按口播和读图时间调整。该模板设计画布为 1080×1920，会等比缩放；横版时需重新布置场景，避免把窄画面误当作横版适配。图片保持原比例，不把内置海报说成实际生成结果。

## 所有模板的控制接口

```javascript
window.SIMULATION_DURATION       // 秒数
window.setSimulationTime(2.5)     // 停在确定的时间画面
```

预览页面有播放/暂停和拖动进度。URL 加 `?clean=1` 隐藏控制条，渲染器会自动使用。修改模板时保留时间驱动逻辑，避免录制速度影响动画结果。

## 素材与输出

模板使用本地/内嵌图形和系统字体。自定义图片和字体需连同 HTML 一起交付，或转换成内嵌资源。按对应模板支持的字段修改昵称、任务和模型文字；默认演示数据不代表真实账户或服务承诺。

运行 `python3 scripts/render_video.py --help` 查看渲染参数。`--duration` 可覆盖模板时长，但不改变内部事件时间；只截取前几秒时注意最终状态是否展示完整。分辨率须为正偶数，帧率为 0–60（不含 0）。脚本成功退出并不替代画面目检。
