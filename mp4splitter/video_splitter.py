"""
Video splitter component for the MP4 Splitter application.
"""

import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from PySide6.QtCore import QObject, Signal


class VideoSplitter(QObject):
    """
    Class for splitting videos based on defined split points.
    """
    # Signals for progress updates
    progress_updated = Signal(int, int)  # current, total
    segment_started = Signal(int, str)   # segment number, filename
    splitting_completed = Signal()
    error_occurred = Signal(str)         # error message

    def __init__(self, video_path=None, output_dir=None):
        super().__init__()
        self.video_path = video_path
        self.output_dir = output_dir

    def set_video_path(self, video_path):
        """Set the path to the video file to be split."""
        self.video_path = video_path

    def set_output_dir(self, output_dir):
        """Set the output directory for split segments."""
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def split_video(self, split_points):
        """
        Split the video according to the provided split points.

        Args:
            split_points: List of SplitPoint objects defining where to split the video.
        """
        if not self.video_path or not self.output_dir:
            self.error_occurred.emit("Video path or output directory not set")
            return

        if not split_points:
            self.error_occurred.emit("No split points defined")
            return

        try:
            # Get original filename without extension
            base_name = os.path.splitext(os.path.basename(self.video_path))[0]

            # Load the video
            video = VideoFileClip(self.video_path)

            # Add the end of the video as the final split point if needed
            if split_points and split_points[-1].end_time is None:
                split_points[-1].end_time = int(video.duration * 1000)

            # Process each split point
            total_segments = len(split_points)
            for i, point in enumerate(split_points):
                # Convert milliseconds to seconds
                start_sec = point.start_time / 1000
                end_sec = point.end_time / 1000

                # Create output filename
                output_filename = f"{base_name}_split_{i+1}.mp4"
                output_path = os.path.join(self.output_dir, output_filename)

                # Emit progress signals
                self.segment_started.emit(i+1, output_filename)
                self.progress_updated.emit(i, total_segments)

                # Extract the segment - using the new API for MoviePy 2.0+
                segment = video.subclipped(start_sec, end_sec)

                # Save the segment
                segment.write_videofile(
                    output_path,
                    codec="libx264",
                    audio_codec="aac",
                    temp_audiofile=os.path.join(self.output_dir, f"temp_audio_{i}.m4a"),
                    remove_temp=True,
                    logger=None  # Disable moviepy's console output
                )

            # Clean up
            video.close()

            # Signal completion
            self.progress_updated.emit(total_segments, total_segments)
            self.splitting_completed.emit()

        except Exception as e:
            self.error_occurred.emit(f"Error splitting video: {str(e)}")

    def get_video_info(self):
        """
        Get information about the loaded video.

        Returns:
            dict: Video information including duration, resolution, etc.
        """
        if not self.video_path:
            return None

        try:
            video = VideoFileClip(self.video_path)
            info = {
                "duration": video.duration * 1000,  # Convert to milliseconds
                "width": video.w,
                "height": video.h,
                "fps": video.fps,
                "filename": os.path.basename(self.video_path)
            }
            video.close()
            return info
        except Exception as e:
            self.error_occurred.emit(f"Error getting video info: {str(e)}")
            return None

