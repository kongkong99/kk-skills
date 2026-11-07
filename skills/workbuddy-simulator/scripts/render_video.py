#!/usr/bin/env python3
"""Render a deterministic local simulation HTML into a silent MP4.

The page must expose window.setSimulationTime(seconds). Its optional
window.SIMULATION_DURATION supplies the default duration in seconds.
Requires Node 22+, Chrome/Chromium and ffmpeg; no third-party JS packages.
"""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


NODE_RENDERER = r'''
const { spawn } = require('node:child_process');
const fs = require('node:fs/promises');
const { pathToFileURL } = require('node:url');
const { once } = require('node:events');

const [html, output, chromePath, ffmpegPath, profile, fpsArg, durationArg, widthArg, heightArg] = process.argv.slice(1);
const fps = Number(fpsArg), width = Number(widthArg), height = Number(heightArg);
let chrome, ffmpeg, socket;
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
let requestId = 0;
const pending = new Map();
let loadResolve;
async function command(method, params = {}) {
  const id = ++requestId;
  const promise = new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
  socket.send(JSON.stringify({ id, method, params }));
  return promise;
}
async function evaluate(expression) {
  const response = await command('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (response.exceptionDetails) throw new Error(response.exceptionDetails.text + ': ' + (response.exceptionDetails.exception?.description || ''));
  return response.result.value;
}
async function run() {
  chrome = spawn(chromePath, [
    '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
    '--disable-background-networking', '--remote-debugging-address=127.0.0.1',
    '--remote-debugging-port=0', '--user-data-dir=' + profile, 'about:blank'
  ], { stdio: 'ignore' });
  let port;
  for (let i = 0; i < 200; i++) {
    if (chrome.exitCode !== null) throw new Error('Chrome exited before DevTools was ready.');
    try { port = Number((await fs.readFile(profile + '/DevToolsActivePort', 'utf8')).split('\n')[0]); if (port) break; } catch {}
    await delay(100);
  }
  if (!port) throw new Error('Timed out waiting for Chrome DevTools.');
  const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = targets.find(x => x.type === 'page');
  if (!page) throw new Error('Chrome did not expose a page target.');
  socket = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.addEventListener('open', resolve, { once: true }); socket.addEventListener('error', reject, { once: true }); });
  socket.addEventListener('message', event => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) {
      const item = pending.get(msg.id); pending.delete(msg.id);
      msg.error ? item.reject(new Error(msg.error.message)) : item.resolve(msg.result);
    } else if (msg.method === 'Page.loadEventFired' && loadResolve) { loadResolve(); loadResolve = null; }
  });
  socket.addEventListener('close', () => { for (const item of pending.values()) item.reject(new Error('Chrome DevTools closed.')); pending.clear(); });
  await command('Page.enable');
  await command('Runtime.enable');
  await command('Network.enable');
  await command('Network.setBlockedURLs', { urls: ['http://*', 'https://*'] });
  await command('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
  const loaded = new Promise(resolve => { loadResolve = resolve; });
  const pageUrl = pathToFileURL(html); pageUrl.searchParams.set('clean', '1');
  const navigation = await command('Page.navigate', { url: pageUrl.href });
  if (navigation.errorText) throw new Error('Could not open HTML: ' + navigation.errorText);
  let loadTimer;
  try { await Promise.race([loaded, new Promise((_, reject) => { loadTimer = setTimeout(() => reject(new Error('Timed out loading simulation.')), 15000); })]); }
  finally { clearTimeout(loadTimer); }
  await evaluate('document.fonts.ready.then(() => true)');
  const info = await evaluate('({hasController: typeof window.setSimulationTime === "function", duration: Number(window.SIMULATION_DURATION ?? window.simulationDuration)})');
  if (!info.hasController) throw new Error('HTML must define window.setSimulationTime(seconds).');
  const duration = durationArg === '' ? info.duration : Number(durationArg);
  if (!Number.isFinite(duration) || duration <= 0) throw new Error('Set a positive --duration or window.SIMULATION_DURATION.');
  const count = Math.ceil(duration * fps);
  ffmpeg = spawn(ffmpegPath, ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-vcodec', 'png', '-framerate', String(fps), '-i', 'pipe:0', '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-f', 'mp4', output], { stdio: ['pipe', 'ignore', 'inherit'] });
  let encoderError;
  ffmpeg.on('error', err => { encoderError = err; });
  ffmpeg.stdin.on('error', err => { encoderError = err; });
  for (let frame = 0; frame < count; frame++) {
    if (encoderError) throw encoderError;
    const seconds = frame / fps;
    await evaluate(`Promise.resolve(window.setSimulationTime(${seconds})).then(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))))`);
    const image = await command('Page.captureScreenshot', { format: 'png', fromSurface: true });
    if (!ffmpeg.stdin.write(Buffer.from(image.data, 'base64'))) await once(ffmpeg.stdin, 'drain');
    if (frame % Math.max(1, Math.floor(fps * 5)) === 0) process.stderr.write(`\rRendering ${frame + 1}/${count} frames`);
  }
  ffmpeg.stdin.end();
  const [code] = await once(ffmpeg, 'close');
  if (code !== 0) throw new Error('ffmpeg failed with exit code ' + code);
  process.stderr.write(`\rRendered ${count} frames (${duration}s at ${fps} fps).\n`);
}
run().catch(err => { console.error('\nRender failed:', err.message); process.exitCode = 1; }).finally(() => {
  if (socket) socket.close();
  if (ffmpeg && ffmpeg.exitCode === null) ffmpeg.kill('SIGTERM');
  if (chrome && chrome.exitCode === null) chrome.kill('SIGTERM');
});
'''


def find_chrome():
    candidates = [
        os.environ.get("CHROME_PATH"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    return next((p for p in candidates if p and Path(p).is_file()), None)


def find_ffmpeg():
    candidates = [os.environ.get("FFMPEG_PATH"), shutil.which("ffmpeg"),
                  str(Path.home() / ".local/bin/ffmpeg"), "/opt/homebrew/bin/ffmpeg"]
    for candidate in candidates:
        if not candidate or not Path(candidate).is_file():
            continue
        try:
            if subprocess.run([candidate, "-version"], stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, timeout=5).returncode == 0:
                return candidate
        except (OSError, subprocess.TimeoutExpired):
            continue
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path, help="local simulation HTML")
    parser.add_argument("output", type=Path, help="output MP4 path")
    parser.add_argument("--duration", type=float, help="duration in seconds; defaults to window.SIMULATION_DURATION")
    parser.add_argument("--fps", type=float, default=12, help="output frames per second (default: 12)")
    parser.add_argument("--width", type=int, default=1512, help="viewport width in pixels (default: 1512)")
    parser.add_argument("--height", type=int, default=886, help="viewport height in pixels (default: 886)")
    args = parser.parse_args()
    html = args.html.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not html.is_file():
        parser.error(f"HTML not found: {html}")
    if output.suffix.lower() != ".mp4":
        parser.error("output must have an .mp4 extension")
    if args.duration is not None and not 0 < args.duration <= 3600:
        parser.error("--duration must be greater than 0 and at most 3600")
    if not 0 < args.fps <= 60 or args.width <= 0 or args.height <= 0 or args.width % 2 or args.height % 2:
        parser.error("--fps must be in (0, 60], and dimensions must be positive even integers")
    node, ffmpeg, chrome = shutil.which("node"), find_ffmpeg(), find_chrome()
    if not all((node, ffmpeg, chrome)):
        parser.error("Requires Node 22+, ffmpeg and Chrome/Chromium (set CHROME_PATH if needed)")
    major = subprocess.check_output([node, "-p", "Number(process.versions.node.split('.')[0])"], text=True).strip()
    if int(major) < 22:
        parser.error("Node 22+ is required for the built-in WebSocket client")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="workbuddy-render-") as temp:
        partial = str(Path(temp) / "output.mp4")
        command = [node, "-e", NODE_RENDERER, str(html), partial, chrome, ffmpeg, temp,
                   str(args.fps), "" if args.duration is None else str(args.duration), str(args.width), str(args.height)]
        result = subprocess.run(command)
        if result.returncode:
            return result.returncode
        shutil.copyfile(partial, output)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
