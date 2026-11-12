#!/usr/bin/env python3
"""Render an editable chat case as a scrolling phone-screen MP4."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

try:
    from PIL import Image, ImageDraw
except ImportError:
    bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
    if bundled.exists() and os.path.realpath(sys.executable) != os.path.realpath(bundled):
        os.execv(str(bundled), [str(bundled), str(Path(__file__).resolve()), *sys.argv[1:]])
    sys.exit('Pillow 不可用，请安装与当前 Python 匹配的 Pillow。')

import generate

# Each tuple is start time, duration, and target location (0=top, 1=bottom).
# A series of quick flicks, deceleration, pauses and reversals, based on the
# supplied screen recording. Time stretches proportionally for custom duration.
GESTURES = [
    (0.20, 0.75, 0.20), (1.05, 0.83, 0.38), (2.10, 0.72, 0.58),
    (3.12, 0.80, 0.80), (4.25, 0.90, 1.00),
    (5.90, 0.85, 0.82), (7.00, 0.90, 0.65),
    (8.20, 0.86, 0.80), (9.35, 0.95, 0.98),
    (10.62, 0.95, 0.82), (12.10, 0.90, 0.96),
    (13.35, 0.95, 0.78), (14.50, 0.95, 0.62),
]

def find_ffmpeg():
    candidates = [os.environ.get('FFMPEG'), shutil.which('ffmpeg'),
                  str(Path.home()/'.local/bin/ffmpeg'),
                  '/Applications/ChatCut.app/Contents/Resources/app.asar.unpacked/node_modules/ffmpeg-ffprobe-static/ffmpeg']
    for candidate in candidates:
        if not candidate:
            continue
        try:
            check = subprocess.run([candidate, '-version'], stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, timeout=8)
            if check.returncode == 0:
                return candidate
        except (OSError, subprocess.TimeoutExpired):
            pass
    raise ValueError('找不到可运行的 FFmpeg，请安装 FFmpeg 或用 FFMPEG 环境变量指定可执行文件。')


def motion_expression(distance, duration):
    """Piecewise ease-out flicks with holds, offset measured in source pixels."""
    previous = 0.0
    pieces = []
    for start, span, target in GESTURES:
        start, span = start * duration / 16.13, span * duration / 16.13
        end = start + span
        # easeOutCubic: fast start, then decay like a released finger swipe.
        u = f'((t-{start:.5f})/{span:.5f})'
        eased = f'(1-pow(1-{u},3))'
        pieces.append((start, end, previous, target, eased))
        previous = target
    expr = f'{previous * distance:.4f}'
    for start, end, before, target, eased in reversed(pieces):
        val = f'({before * distance:.4f}+{(target-before)*distance:.4f}*{eased})'
        expr = f'if(lt(t,{start:.5f}),{before * distance:.4f},if(lt(t,{end:.5f}),{val},{expr}))'
    return expr


def scrollbar_opacity(duration):
    # The narrow indicator appears while the list is moving, then fades away.
    intervals = []
    for start, span, _ in GESTURES:
        start, span = start * duration / 16.13, span * duration / 16.13
        end = start + span
        fade = min(0.35, duration / 16.13 * 0.35)
        intervals.append(f'if(between(T,{start:.5f},{end:.5f}),1,'
                         f'if(between(T,{end:.5f},{end+fade:.5f}),'
                         f'({end+fade:.5f}-T)/{fade:.5f},0))')
    expr = '0'
    for interval in intervals:
        expr = f'max({expr},{interval})'
    return expr


def render_video(src, dst, duration, fps, width):
    if not 3 <= duration <= 120:
        raise ValueError('视频时长需在 3 到 120 秒之间。')
    if fps not in (24, 30, 60):
        raise ValueError('帧率只支持 24、30 或 60。')
    if not 360 <= width <= 1260 or width % 2:
        raise ValueError('视频宽度需为 360 到 1260 之间的偶数。')
    with src.open(encoding='utf-8-sig') as f:
        data = json.load(f)
    still = generate.render(data, src.parent)
    pinned = generate.HEADER + (184 if data.get('group') and data.get('announcement') else 0)
    footer = generate.FOOTER
    viewport_h = generate.BASE_H - pinned - footer
    full_body_h = still.height - pinned - footer
    if full_body_h <= viewport_h:
        raise ValueError('对话内容不足一屏，无法滚动；请添加更多消息或较长图片。')
    ffmpeg = find_ffmpeg()
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='chat-scroll-') as tmp:
        tmp = Path(tmp)
        # Retain the original screenshot's top bar and input area, while only
        # the middle strip is translated and clipped to the phone viewport.
        header = still.crop((0, 0, generate.W, pinned))
        body = still.crop((0, pinned, generate.W, still.height-footer))
        bottom = still.crop((0, still.height-footer, generate.W, still.height))
        scale = width / generate.W
        def even(n): return max(2, round(n/2)*2)
        out_h = even(generate.BASE_H * scale)
        top_h = even(pinned * scale)
        bottom_h = even(footer * scale)
        mid_h = out_h-top_h-bottom_h
        body_h = max(mid_h+2, even(full_body_h*scale))
        resample = Image.Resampling.LANCZOS
        header.resize((width,top_h),resample).save(tmp/'header.png')
        body.resize((width,body_h),resample).save(tmp/'body.png')
        bottom.resize((width,bottom_h),resample).save(tmp/'footer.png')
        travel = body_h-mid_h
        expr = motion_expression(travel, duration)
        # Transparent moving scroll indicator follows the visible position. It
        # stays confined to the message viewport, never over the navigation bars.
        scrollbar_h = max(28, int(mid_h * mid_h / body_h))
        bar = Image.new('RGBA',(4,scrollbar_h),(110,110,110,140))
        bar.save(tmp/'scrollbar.png')
        bar_expr = motion_expression(mid_h-scrollbar_h, duration)
        opacity = scrollbar_opacity(duration)
        graph = (f"[3:v]format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                 f"a='alpha(X,Y)*({opacity})'[scrollbar];"
                 f"[1:v]crop={width}:{mid_h}:0:'{expr}'[mid];"
                 f"[0:v][mid]vstack=inputs=2[top];"
                 f"[top][2:v]vstack=inputs=2[base];"
                 f"[base][scrollbar]overlay=x={width-11}:y='{top_h}+{bar_expr}':shortest=1,format=yuv420p[out]")
        cmd = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y']
        for name in ('header.png','body.png','footer.png','scrollbar.png'):
            cmd += ['-loop','1','-framerate',str(fps),'-i',str(tmp/name)]
        cmd += ['-filter_complex',graph,'-map','[out]','-t',str(duration),
                '-an','-c:v','libx264','-preset','veryfast','-crf','20',
                '-movflags','+faststart',str(dst)]
        process = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if process.returncode:
            raise ValueError('FFmpeg 视频生成失败：'+process.stderr[-2500:])
    print(f'已生成：{dst}（{width} × {out_h}，{duration:g} 秒，{fps} fps）')


def main():
    ap = argparse.ArgumentParser(description='生成竖版手机聊天滑动视频')
    ap.add_argument('--input','-i',required=True,help='聊天 JSON 文件')
    ap.add_argument('--output','-o',required=True,help='输出 MP4 文件')
    ap.add_argument('--duration',type=float,default=16.13,help='时长（秒），默认 16.13')
    ap.add_argument('--fps',type=int,default=60,help='帧率：24、30 或 60，默认 60')
    ap.add_argument('--width',type=int,default=1260,help='视频宽度（偶数），默认 1260')
    args=ap.parse_args()
    try:
        src=Path(args.input).expanduser().resolve(); dst=Path(args.output).expanduser().resolve()
        if dst.suffix.lower() != '.mp4': raise ValueError('输出文件必须以 .mp4 结尾。')
        render_video(src,dst,args.duration,args.fps,args.width)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print('生成失败：'+str(exc),file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
