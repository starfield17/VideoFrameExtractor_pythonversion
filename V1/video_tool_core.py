# video_tool_core.py
from __future__ import annotations
import cv2
import os
from pathlib import Path
from typing import Callable, Iterable

VIDEO_EXTENSIONS = {"mp4", "avi", "mkv", "mov", "flv", "wmv", "webm"}

LogFn = Callable[[str], None]

def is_video_file(p: str | os.PathLike) -> bool:
    ext = Path(p).suffix.lower().lstrip(".")
    return ext in VIDEO_EXTENSIONS

def _safe_fps(cap, default: float = 25.0) -> float:
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    return fps if fps and fps > 0 else default

def _iter_all_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file() and is_video_file(p):
            yield p

def _ensure_parent_dir(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)

# ------------------------
# getframe implementation
# ------------------------
def extract_frames(input_path: str | os.PathLike, log: LogFn = print) -> bool:
    p = Path(input_path)
    if p.is_dir():
        log(f"Detected directory: {p}")
        log("Starting to process video files in directory...")
        ok_all = True
        for f in _iter_all_files(p):
            log(f"Processing video file: {f}")
            if not _extract_frames_single(f, log):
                log(f"Processing failed: {f}")
                ok_all = False
        log("All video files processed.")
        return ok_all
    elif p.is_file():
        if not is_video_file(p):
            log(f"Error: File '{p}' is not a supported video format.")
            return False
        log(f"Processing single video file: {p}")
        ok = _extract_frames_single(p, log)
        log("Video file processed successfully." if ok else "Video file processing failed.")
        return ok
    else:
        log(f"Error: '{p}' is neither a file nor a directory.")
        return False

def _extract_frames_single(video_path: Path, log: LogFn) -> bool:
    if not video_path.exists():
        log(f"Error: File '{video_path}' does not exist.")
        return False

    name = video_path.stem
    out_dir = video_path.parent / f"{name}_frames"
    out_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        log(f"Error: Cannot open video '{video_path}'.")
        return False

    fps = _safe_fps(cap, 25.0)
    # save roughly 1 frame per second
    frame_interval = max(int(round(fps)), 1)

    saved = 0
    idx = 0
    next_save = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx >= next_save:
            saved += 1
            out_path = out_dir / f"{name}_{saved}.png"  # 1-based numbering
            cv2.imwrite(str(out_path), frame)
            next_save += frame_interval
        idx += 1

    cap.release()
    log(f"Frames saved to directory: {out_dir}")
    return True

# ------------------------
# getmp4 implementation
# ------------------------
def convert_to_mp4(input_path: str | os.PathLike, log: LogFn = print) -> bool:
    p = Path(input_path)
    if p.is_dir():
        log(f"Detected directory: {p}")
        log("Starting to convert non-MP4 video files in directory...")
        ok_all = True
        for f in _iter_all_files(p):
            if f.suffix.lower() == ".mp4":
                log(f"File '{f}' is already in MP4 format, skipping conversion.")
                continue
            log(f"Processing video file: {f}")
            if not _convert_single_to_mp4(f, log):
                log(f"Processing failed: {f}")
                ok_all = False
        log("All video files converted.")
        return ok_all
    elif p.is_file():
        if not is_video_file(p):
            log(f"Error: File '{p}' is not a supported video format.")
            return False
        log(f"Processing single video file: {p}")
        ok = _convert_single_to_mp4(p, log)
        log("Video file converted successfully." if ok else "Video file conversion failed.")
        return ok
    else:
        log(f"Error: '{p}' is neither a file nor a directory.")
        return False

def _convert_single_to_mp4(video_path: Path, log: LogFn) -> bool:
    if video_path.suffix.lower() == ".mp4":
        log(f"File '{video_path}' is already in MP4 format, skipping conversion.")
        return True

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        log(f"Error: Cannot open video '{video_path}'.")
        return False

    fps = _safe_fps(cap, 25.0)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    if w == 0 or h == 0:
        cap.release()
        log(f"Error: Cannot determine resolution for '{video_path}'.")
        return False

    # OpenCV-friendly MP4 encoder (video only; audio dropped)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_path = video_path.with_suffix(".mp4")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))
    if not writer.isOpened():
        cap.release()
        log(f"Error: Cannot create output MP4 for '{video_path}'.")
        return False

    frames = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        writer.write(frame)
        frames += 1

    writer.release()
    cap.release()

    if frames == 0:
        log(f"Error: No frames written for '{video_path}'.")
        return False

    log("Note: Audio is not preserved when converting without ffmpeg.")
    log(f"Converted '{video_path}' to '{out_path}'")
    return True

# ------------------------
# mergevideo implementation
# ------------------------
def merge_videos_recursively(input_dir: str | os.PathLike, log: LogFn = print) -> bool:
    p = Path(input_dir)
    if not p.is_dir():
        log("Error: 'mergevideo' command requires a directory as input.")
        return False

    log(f"Detected directory: {p}")
    log("Starting to recursively merge video files in directory...")
    ok_all = True
    # Process the root dir and each subdir independently
    for current, dirs, files in os.walk(p):
        dir_path = Path(current)
        log(f"Processing directory: {dir_path}")
        if not _merge_dir(dir_path, log):
            log(f"Merge failed: {dir_path}")
            ok_all = False
    log("All video files in all directories merged.")
    return ok_all

def _merge_dir(directory: Path, log: LogFn) -> bool:
    vids = sorted([directory / f for f in os.listdir(directory)
                   if is_video_file(directory / f)])
    if len(vids) < 2:
        log(f"Less than 2 video files in directory '{directory}', skipping merge.")
        return True

    # Use first video as reference for size & fps
    cap0 = cv2.VideoCapture(str(vids[0]))
    if not cap0.isOpened():
        log(f"Error: Cannot open '{vids[0]}'")
        return False
    fps0 = _safe_fps(cap0, 25.0)
    w0 = int(cap0.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    h0 = int(cap0.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    cap0.release()
    if w0 == 0 or h0 == 0:
        log(f"Error: Cannot determine resolution from '{vids[0]}'.")
        return False

    out_path = directory / "merged_output.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps0, (w0, h0))
    if not writer.isOpened():
        log(f"Error: Cannot create '{out_path}'.")
        return False

    total_frames = 0
    for v in vids:
        cap = cv2.VideoCapture(str(v))
        if not cap.isOpened():
            log(f"Error: Cannot open '{v}', skipping.")
            continue
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        if w != w0 or h != h0:
            log(f"Warning: Resizing '{v.name}' from {w}x{h} to {w0}x{h0} to match first video.")
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame.shape[1] != w0 or frame.shape[0] != h0:
                frame = cv2.resize(frame, (w0, h0), interpolation=cv2.INTER_AREA)
            writer.write(frame)
            total_frames += 1
        cap.release()

    writer.release()
    log("Note: Audio is not preserved when merging without ffmpeg.")
    log(f"Merged {len(vids)} videos in directory '{directory}' into '{out_path}' (frames written: {total_frames})")
    return True

