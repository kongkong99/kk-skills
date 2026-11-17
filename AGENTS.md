# 视频技能维护

修改视频包装相关内容前读取 `VIDEO_SKILLS.md`。

- 通用源：`skills/short-video-packaging/`。
- 个人源：`profiles/video-personal/`。
- `skills/interface-explainer-motion/` 是构建结果，不手工双改。
- 修改后运行 `python3 scripts/build_video_skills.py` 和 `--check`，按需生成两个独立 ZIP。
- 保留既有用户明确偏好；个人配置覆盖主干默认值。通用修复回到主干，个人偏好留在配置。
