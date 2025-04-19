# MP4 Splitter

MP4 Splitter is a desktop application that allows you to easily split MP4 video files into multiple segments. It provides a user-friendly interface for defining split points and extracting segments from your videos.

![image](https://github.com/user-attachments/assets/21c9d570-673c-4b96-bd44-3795802cf2f7)


## Features

- **Video Playback**: Watch your videos with full audio and video support
- **Intuitive Split Point Management**: Define where to split your videos with precise timestamp control
- **Segment Extraction**: Extract video segments with preserved quality
- **Progress Tracking**: Monitor the splitting process with a progress bar
- **Volume Control**: Adjust audio volume during playback

## Installation

### Prerequisites

- Python 3.9 or higher
- PIP package manager

### Setup

1. Clone this repository or download the source code:
   ```
   git clone https://github.com/SS-ekow/python_mp4_splitter_desktop_app.git
   cd mp4_splitter
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

## Usage

### Loading a Video

1. Click the "Open Video" button or use File → Open Video
2. Select an MP4 file from your computer
3. The video will load and display information about its resolution and duration

### Creating Split Points

1. Play the video using the play button (▶)
2. Navigate to the desired split point using the slider or time input
3. Click "Add split point >" to mark the current position as a split point
4. Repeat steps 2-3 to add more split points
5. You can edit split points directly in the table by clicking on the time values

### Splitting the Video

1. Click "Select" to choose an output directory for the split segments
2. Ensure the checkboxes next to the desired split points are checked
3. Click "Start Splitting" to begin the process
4. A progress bar will show the splitting progress
5. When complete, the segments will be available in the selected output directory

## How It Works

MP4 Splitter uses the following technologies:

- **PySide6 (Qt for Python)**: For the graphical user interface
- **MoviePy**: For video processing and splitting
- **FFmpeg**: Used by MoviePy for the actual video encoding/decoding

The application extracts segments from the original video without re-encoding the entire file, which helps preserve quality and speeds up the process.

## Troubleshooting

### Common Issues

- **No audio during playback**: Make sure your system's audio is not muted and the volume slider in the application is set appropriately.
- **Splitting fails**: Ensure you have write permissions to the selected output directory.
- **Video doesn't load**: The application currently only supports MP4 format. Make sure your video is in MP4 format.

### Error Messages

If you encounter an error, a message will be displayed explaining the issue. Common errors include:
- "No split points defined": Add at least one split point before starting the splitting process.
- "Video path or output directory not set": Make sure you've loaded a video and selected an output directory.

## Contributing

Contributions are welcome! If you'd like to contribute to the project, please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Add your changes
4. Submit a pull request



## Acknowledgments

- [PySide6](https://doc.qt.io/qtforpython-6/) for the GUI framework
- [MoviePy](https://zulko.github.io/moviepy/) for video processing capabilities
- [FFmpeg](https://ffmpeg.org/) for the underlying video processing engine


