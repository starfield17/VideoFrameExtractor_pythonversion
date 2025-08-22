# video_tool_cli.py
import sys
from pathlib import Path
from video_tool_core import (
    extract_frames,
    convert_to_mp4,
    merge_videos_recursively,
)

def show_usage():
    print("==============================================")
    print("          Video Processing Tool Guide")
    print("==============================================")
    print("Usage: VideoFrameExtractor <command> <path>")
    print("")
    print("Command Description:")
    print("  getframe      Extract video frames")
    print("  getmp4        Convert non-MP4 videos to MP4 format (video only)")
    print("  mergevideo    Merge video files in directory (recursively process each subdirectory)")
    print("")
    print("Parameter Description:")
    print("  <path>  Specify a single video file or directory containing video files.")
    print("")
    print("Supported Video Formats:")
    print("  mp4, avi, mkv, mov, flv, wmv, webm")
    print("==============================================")

def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) < 2:
        show_usage()
        return 1

    command = argv[0].lower()
    input_path = argv[1]
    p = Path(input_path)

    if not p.exists():
        print(f"Error: Path '{input_path}' does not exist.")
        return 1

    if command == "getframe":
        ok = extract_frames(input_path)
    elif command == "getmp4":
        ok = convert_to_mp4(input_path)
    elif command == "mergevideo":
        ok = merge_videos_recursively(input_path)
    else:
        print(f"Error: Unknown command '{command}'.")
        show_usage()
        return 1

    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())

