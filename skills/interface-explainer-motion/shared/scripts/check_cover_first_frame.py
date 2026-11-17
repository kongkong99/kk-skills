#!/usr/bin/env python3
"""Check decoded first-frame/cover visual consistency using FFmpeg SSIM.

Only the Python standard library and FFmpeg are required. Exit codes:
0 = same dimensions and SSIM >= threshold; 1 = visual mismatch;
2 = invalid input, tool failure, or unreadable/unwritable output.
This does not assess cover quality or prove anything about timeline layers.
"""

import argparse
import json
import math
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile


class CheckError(Exception):
    """Invalid input or unavailable/failed tool."""


def threshold_value(value):
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("threshold must be a number") from exc
    if not math.isfinite(number) or not 0 <= number <= 1:
        raise argparse.ArgumentTypeError("threshold must be between 0 and 1")
    return number


def run_ffmpeg(executable, arguments):
    command = [executable, "-hide_banner", "-nostdin", *arguments]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, errors="replace", timeout=120
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckError(f"FFmpeg could not run: {exc}") from exc
    if result.returncode:
        raise CheckError(
            f"FFmpeg exited {result.returncode}: {result.stderr.strip()[-4000:]}"
        )
    return result.stderr


def decode_first_frame(executable, source, destination, video_input=False):
    run_ffmpeg(executable, [
        "-loglevel", "error", "-y", "-threads", "1",
        "-protocol_whitelist", "file,pipe", "-i", str(source),
        # Upper-case V excludes attached cover art and thumbnail streams.
        "-map", "0:V:0" if video_input else "0:v:0",
        "-frames:v", "1", "-an", "-sn", "-dn",
        "-vf", "format=rgb24", "-filter_threads", "1", "-threads", "1",
        "-c:v", "png", "-f", "image2", "-update", "1", str(destination),
    ])
    if not destination.is_file():
        raise CheckError(f"FFmpeg did not produce a frame for {source}")


def png_dimensions(path):
    with path.open("rb") as stream:
        header = stream.read(24)
    if (len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n"
            or header[12:16] != b"IHDR"):
        raise CheckError(f"Invalid decoded PNG: {path}")
    width, height = struct.unpack(">II", header[16:24])
    if not width or not height:
        raise CheckError(f"Invalid decoded dimensions: {path}")
    return {"width": width, "height": height}


def compare_ssim(executable, first_frame, cover_frame):
    # Both inputs are lossless decoded RGB PNGs, with no resizing or padding.
    # gbrp gives SSIM the three color planes at full spatial resolution.
    output = run_ffmpeg(executable, [
        "-loglevel", "info", "-threads", "1", "-i", str(first_frame),
        "-threads", "1", "-i", str(cover_frame),
        "-filter_complex_threads", "1", "-filter_complex",
        "[0:v]format=gbrp,setpts=PTS-STARTPTS[a];"
        "[1:v]format=gbrp,setpts=PTS-STARTPTS[b];[a][b]ssim[out]",
        "-map", "[out]", "-frames:v", "1", "-an", "-f", "null", "-",
    ])
    matches = re.findall(r"\bAll:([+\-0-9.eE]+)", output)
    if len(matches) != 1:
        raise CheckError("FFmpeg did not return exactly one SSIM All score")
    score = float(matches[0])
    if not math.isfinite(score):
        raise CheckError("FFmpeg returned a non-finite SSIM score")
    return score


def write_report(path, report):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=".cover-report-", suffix=".json", delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        temporary.replace(path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--cover", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG_PATH", "ffmpeg"),
                        help="FFmpeg path or PATH name; defaults to FFMPEG_PATH or ffmpeg")
    parser.add_argument("--threshold", type=threshold_value, default=0.98)
    args = parser.parse_args()
    report_path = None
    report = {
        "schema_version": 1,
        "status": "error",
        "exit_code": 2,
        "metric": "FFmpeg SSIM All, decoded RGB planes, no resizing",
        "threshold": args.threshold,
        "ssim": None,
        "dimensions": {"first_frame": None, "cover": None},
        "scope": "Visual consistency only; not cover quality or timeline-layer validation.",
    }
    try:
        video = args.video.expanduser().resolve()
        cover = args.cover.expanduser().resolve()
        directory = args.output_dir.expanduser().resolve()
        first_frame = directory / "first-frame.png"
        candidate_report = directory / "report.json"
        inputs = {video, cover}
        for target in (first_frame, candidate_report):
            if target.is_symlink() or target.resolve() in inputs:
                raise CheckError(f"Output would overwrite or redirect to input: {target}")
        directory.mkdir(parents=True, exist_ok=True)
        report_path = candidate_report
        report.update(video=str(video), cover=str(cover), first_frame=str(first_frame))
        for label, source in (("video", video), ("cover", cover)):
            if not source.is_file():
                raise CheckError(f"{label} is not a readable local file: {source}")
        # Preserve PATH names for environments that provide executable launchers.
        # Explicit paths remain supported, including FFMPEG_PATH overrides.
        executable = str(Path(args.ffmpeg).expanduser())
        if shutil.which(executable) is None:
            raise CheckError(f"FFmpeg executable not found: {args.ffmpeg}")
        report["ffmpeg"] = executable

        # Temporary decoding prevents a failed run from using an old frame.
        with tempfile.TemporaryDirectory(prefix=".cover-check-", dir=directory) as temp:
            temp = Path(temp)
            decoded_video = temp / "first.png"
            decoded_cover = temp / "cover.png"
            decode_first_frame(executable, video, decoded_video, video_input=True)
            report["dimensions"]["first_frame"] = png_dimensions(decoded_video)
            decoded_video.replace(first_frame)
            decode_first_frame(executable, cover, decoded_cover)
            report["dimensions"]["cover"] = png_dimensions(decoded_cover)
            if report["dimensions"]["first_frame"] != report["dimensions"]["cover"]:
                report.update(status="fail", exit_code=1, reason="dimension_mismatch")
            else:
                score = compare_ssim(executable, first_frame, decoded_cover)
                passed = score >= args.threshold
                report.update(
                    status="pass" if passed else "fail", exit_code=0 if passed else 1,
                    ssim=score, reason="threshold_met" if passed else "ssim_below_threshold",
                )
    except (CheckError, OSError, ValueError) as exc:
        report.update(status="error", exit_code=2, reason="input_or_tool_error", error=str(exc))

    if report_path is not None:
        try:
            write_report(report_path, report)
        except OSError as exc:
            print(f"Could not write report.json: {exc}", file=sys.stderr)
            return 2
    print(json.dumps(report, ensure_ascii=False), file=sys.stdout)
    return report["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
