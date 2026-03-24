#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional


def build_ffmpeg_command(
    *,
    ffmpeg_bin: str,
    input_path: Path,
    output_pattern: Path,
    fps: Optional[str],
    every_n_frames: Optional[int],
) -> List[str]:
    command = [
        ffmpeg_bin,
        "-i",
        str(input_path),
    ]
    if every_n_frames is not None:
        command.extend(
            [
                "-vf",
                f"select=not(mod(n\\,{every_n_frames}))",
                "-vsync",
                "vfr",
            ]
        )
    else:
        command.extend(["-vf", f"fps={fps or '1'}"])
    command.append(str(output_pattern))
    return command


def resolve_ffmpeg_bin(env: Optional[dict] = None) -> Optional[str]:
    runtime_env = env or os.environ
    override = runtime_env.get("SPCA_FFMPEG_BIN")
    if override:
        override_path = Path(override).expanduser()
        if override_path.exists():
            return str(override_path)
    return shutil.which("ffmpeg")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract video frames for competitor-analysis experience review")
    parser.add_argument("--input", required=True, help="Input video path")
    parser.add_argument("--output-dir", required=True, help="Directory to save frames")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--fps",
        default="1",
        help="Frames per second to export. Use 1 for sparse extraction, or higher for denser review.",
    )
    group.add_argument(
        "--every-n-frames",
        type=int,
        help="Export one frame every N frames. Use 10 to match the default competitor-analysis experience rule.",
    )
    args = parser.parse_args()

    ffmpeg = resolve_ffmpeg_bin()
    if not ffmpeg:
        print("ffmpeg not found. Run bootstrap-macos.sh first so the managed runtime can prepare ffmpeg.")
        return 1

    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_pattern = output_dir / "frame-%05d.png"

    command = build_ffmpeg_command(
        ffmpeg_bin=ffmpeg,
        input_path=input_path,
        output_pattern=output_pattern,
        fps=args.fps,
        every_n_frames=args.every_n_frames,
    )
    result = subprocess.run(command, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
