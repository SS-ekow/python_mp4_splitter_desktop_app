"""
Video player component for the MP4 Splitter application.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QSlider, QLabel, QLineEdit)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, QUrl, Signal


class VideoPlayer(QWidget):
    """
    Video player component that handles video playback and time controls.
    """
    # Signal to notify when the "Add split point" button is clicked
    add_split_point_signal = Signal(int)

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_player()

    def setup_ui(self):
        """Set up the user interface components."""
        layout = QVBoxLayout(self)

        # Video display
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)

        # Slider for seeking
        self.position_slider = QSlider(Qt.Horizontal)
        layout.addWidget(self.position_slider)

        # Controls
        controls_layout = QHBoxLayout()

        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(40, 40)
        controls_layout.addWidget(self.play_button)

        self.time_label = QLabel("00:00:00.000")
        controls_layout.addWidget(self.time_label)

        self.time_edit = QLineEdit()
        self.time_edit.setInputMask("99:99:99.999")
        self.time_edit.setText("00:00:00.000")
        controls_layout.addWidget(self.time_edit)

        # Volume control
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume:")
        volume_layout.addWidget(volume_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)  # Default volume at 70%
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)

        controls_layout.addLayout(volume_layout)

        # Add split point button
        self.add_split_button = QPushButton("Add split point >")
        self.add_split_button.clicked.connect(self.add_split_point)
        controls_layout.addWidget(self.add_split_button)

        layout.addLayout(controls_layout)

    def setup_player(self):
        """Set up the media player and connect signals."""
        self.media_player = QMediaPlayer()

        # Set up audio output
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        # Set initial volume (0.0 to 1.0)
        self.audio_output.setVolume(0.7)  # 70% volume

        # Set up video output
        self.media_player.setVideoOutput(self.video_widget)

        # Connect signals
        self.play_button.clicked.connect(self.toggle_play)
        self.media_player.positionChanged.connect(self.position_changed)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.time_edit.returnPressed.connect(self.time_edit_changed)

        # Set up duration handling
        self.media_player.durationChanged.connect(self.duration_changed)

    def load_video(self, file_path):
        """Load a video file into the player."""
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.play_button.setText("▶")

    def toggle_play(self):
        """Toggle between play and pause states."""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_button.setText("▶")
        else:
            self.media_player.play()
            self.play_button.setText("⏸")

    def position_changed(self, position):
        """Handle position changes in the video."""
        # Update slider without triggering signals
        self.position_slider.blockSignals(True)
        self.position_slider.setValue(position)
        self.position_slider.blockSignals(False)

        # Update time display
        time_str = self.format_time(position)
        self.time_label.setText(time_str)
        self.time_edit.setText(time_str)

    def duration_changed(self, duration):
        """Handle changes to the video duration."""
        self.position_slider.setRange(0, duration)

    def set_position(self, position):
        """Set the playback position."""
        self.media_player.setPosition(position)

    def time_edit_changed(self):
        """Handle manual time input."""
        time_str = self.time_edit.text()
        try:
            # Parse time string (HH:MM:SS.mmm)
            hours, minutes, rest = time_str.split(':')
            seconds, milliseconds = rest.split('.')

            total_ms = (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) * 1000 + int(milliseconds)
            self.set_position(total_ms)
        except ValueError:
            # Reset to current position if parsing fails
            self.time_edit.setText(self.format_time(self.media_player.position()))

    def format_time(self, ms):
        """Format milliseconds as HH:MM:SS.mmm."""
        if ms is None:
            return "00:00:00.000"

        seconds = ms // 1000
        minutes = seconds // 60
        hours = minutes // 60

        return f"{hours:02d}:{minutes % 60:02d}:{seconds % 60:02d}.{ms % 1000:03d}"

    def get_current_time(self):
        """Get the current playback position in milliseconds."""
        return self.media_player.position()

    def get_time_controls(self):
        """Create a widget with time controls for external use."""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        time_label = QLabel("Time:")
        layout.addWidget(time_label)
        layout.addWidget(self.time_edit)

        go_button = QPushButton("Go")
        go_button.clicked.connect(self.time_edit_changed)
        layout.addWidget(go_button)

        return widget

    def add_split_point(self):
        """Emit signal with current time when add split point is clicked."""
        current_time = self.get_current_time()
        self.add_split_point_signal.emit(current_time)

    def set_volume(self, value):
        """Set the audio volume based on slider value."""
        # Convert slider value (0-100) to volume (0.0-1.0)
        volume = value / 100.0
        self.audio_output.setVolume(volume)
