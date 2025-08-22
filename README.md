# Video Processing Tool

This project provides a set of tools for basic video processing. It includes a command-line interface (CLI) and a graphical user interface (GUI) for performing the following operations:

*   **Extract Frames:** Extract frames from a video file at a rate of approximately one frame per second.
*   **Convert to MP4:** Convert videos from other formats to MP4. Note that this conversion does not preserve the audio track.
*   **Merge Videos:** Merge multiple video files within a directory into a single MP4 file. This process is recursive, so it will also merge videos in subdirectories.

## Components

*   **`video_tool_core.py`:** The core library containing the main video processing logic. It uses OpenCV for video manipulation.
*   **`video_tool_cli.py`:** A command-line interface for the tool.
*   **`video_tool_gui.py`:** A graphical user interface built with PyQt6.

## Installation

1.  Clone this repository.
2.  Install the required dependencies:

    ```bash
    cd ./V1
    pip install -r requirements.txt
    ```

## Usage

### GUI

To run the GUI, execute the following command:

```bash
python video_tool_gui.py
```

### Command-Line Interface (CLI)

The CLI provides the following commands:

*   `getframe <path>`: Extract frames from a video file or all video files in a directory.
*   `getmp4 <path>`: Convert a video file or all video files in a directory to MP4.
*   `mergevideo <path>`: Merge all video files in a directory and its subdirectories.

**Example:**

```bash
python video_tool_cli.py getframe /path/to/your/video.mp4
```

## Supported Formats

The tool supports the following video formats:

*   mp4
*   avi
*   mkv
*   mov
*   flv
*   wmv
*   webm
