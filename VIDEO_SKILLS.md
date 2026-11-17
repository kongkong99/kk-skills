# 视频技能：一份主干，两种安装包

公开版 `short-video-packaging` 是唯一通用主干；`profiles/video-personal` 保存个人配置和个人资源。个人版 `interface-explainer-motion` 由脚本组合生成，可单独安装，运行时会先读共享工作流，再读个人配置。

## 以后怎样改

- 通用方法和失败修复改 `skills/short-video-packaging`，例如源视频意外露底、字幕重复动画、音效截断、封面检查。
- 固定个人偏好改 `profiles/video-personal`，例如前三句1.1倍速、前10秒效果数量、圆形小窗固定右下、常驻双白标题。
- 参考样式可在公开版作为可选模式，由个人配置启用；不要把个人偏好变成所有使用者的强制要求。
- 不直接维护生成的 `skills/interface-explainer-motion`；改完源文件后统一构建、检查、打包。个人配置优先于主干默认值，用户当前明确要求优先于两者。

```bash
python3 scripts/build_video_skills.py
python3 scripts/build_video_skills.py --check
python3 scripts/build_video_skills.py --check --dist /absolute/path/dist --release-label 1.1
```

两个 ZIP 各自只有一个对应技能根目录，可独立解压安装。公开包包含通用工作流、可选星点模板及原创合成音效；个人包还包含个人规则和原有生产音效。它们均不包含用户视频、截图或聊天资料。WorkBuddy/聊天专用生成器仍是按任务需要使用的独立技能。

`version` 由公开入口声明，构建时写入个人版 `metadata.version`。发布时核对 ZIP 内每个文件与对应版本源码一致。个人包中的 `shared/` 是自动生成的独立运行快照，不是第二份手工维护的主干。

个人版的封面检查和合成音效脚本只转调共享实现；星点背景、关键词缩放和原创 WAV 的旧路径由构建脚本从公开资源生成，避免通用工具修好了而个人实际调用仍停留在旧版。
