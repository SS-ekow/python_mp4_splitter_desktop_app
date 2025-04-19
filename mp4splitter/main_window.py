"""
Main window component for the MP4 Splitter application.
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QFileDialog, QLabel, QProgressBar,
                              QMessageBox, QStatusBar, QSplitter)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction

from mp4splitter.split_points_table import SplitPointsTable
from mp4splitter.video_player import VideoPlayer
from mp4splitter.video_splitter import VideoSplitter


class MainWindow(QMainWindow):
    """
    Main window for the MP4 Splitter application.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP4 Splitter")
        self.setMinimumSize(900, 600)

        # Initialize components
        self.video_splitter = VideoSplitter()
        self.setup_ui()
        self.setup_connections()
        self.setup_menu()

        # Initialize state
        self.current_video_path = None
        self.output_dir = None

    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Create a splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Video Player
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.video_player = VideoPlayer()
        left_layout.addWidget(self.video_player)

        # Right panel - Split Points & Controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Open video button
        open_btn_layout = QHBoxLayout()
        self.open_btn = QPushButton("Open Video")
        open_btn_layout.addWidget(self.open_btn)

        self.video_info_label = QLabel("No video loaded")
        open_btn_layout.addWidget(self.video_info_label)
        open_btn_layout.addStretch()

        right_layout.addLayout(open_btn_layout)

        # Split points table
        right_layout.addWidget(QLabel("Split points:"))
        self.split_points_table = SplitPointsTable()
        right_layout.addWidget(self.split_points_table)

        # Output directory selection
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output directory:"))
        self.output_dir_label = QLabel("Not selected")
        output_layout.addWidget(self.output_dir_label, 1)
        self.select_output_btn = QPushButton("Select")
        output_layout.addWidget(self.select_output_btn)
        right_layout.addLayout(output_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)

        # Start splitting button
        split_btn_layout = QHBoxLayout()
        split_btn_layout.addStretch()
        self.start_splitting_btn = QPushButton("Start Splitting")
        self.start_splitting_btn.setEnabled(False)
        split_btn_layout.addWidget(self.start_splitting_btn)
        right_layout.addLayout(split_btn_layout)

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        # Set initial sizes (60% left, 40% right)
        splitter.setSizes([600, 400])

        # Add splitter to main layout
        main_layout.addWidget(splitter)

        # Set central widget
        self.setCentralWidget(main_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_connections(self):
        """Set up signal connections."""
        # Button connections
        self.open_btn.clicked.connect(self.open_video)
        self.select_output_btn.clicked.connect(self.select_output_directory)
        self.start_splitting_btn.clicked.connect(self.start_splitting)

        # Connect video player's add split point signal
        self.video_player.add_split_point_signal.connect(self.split_points_table.add_split_point)

        # Connect video splitter signals
        self.video_splitter.progress_updated.connect(self.update_progress)
        self.video_splitter.segment_started.connect(self.segment_started)
        self.video_splitter.splitting_completed.connect(self.splitting_completed)
        self.video_splitter.error_occurred.connect(self.show_error)

    def setup_menu(self):
        """Set up the application menu."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open Video", self)
        open_action.triggered.connect(self.open_video)
        file_menu.addAction(open_action)

        select_output_action = QAction("Select Output Directory", self)
        select_output_action.triggered.connect(self.select_output_directory)
        file_menu.addAction(select_output_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menu_bar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def open_video(self):
        """Open a video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video", "", "Video Files (*.mp4)"
        )
        if file_path:
            self.video_player.load_video(file_path)
            self.current_video_path = file_path
            self.video_splitter.set_video_path(file_path)

            # Update video info
            video_info = self.video_splitter.get_video_info()
            if video_info:
                duration_str = self.format_time(video_info["duration"])
                resolution = f"{video_info['width']}x{video_info['height']}"
                self.video_info_label.setText(
                    f"{video_info['filename']} ({resolution}, {duration_str})"
                )

            # Clear existing split points
            self.split_points_table.split_points = []
            self.split_points_table.update_table()

            # Update status
            self.status_bar.showMessage(f"Loaded video: {file_path}")
            self.update_splitting_button_state()

    def select_output_directory(self):
        """Select output directory for split files."""
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        if output_dir:
            self.output_dir = output_dir
            self.output_dir_label.setText(output_dir)
            self.video_splitter.set_output_dir(output_dir)
            self.update_splitting_button_state()
            self.status_bar.showMessage(f"Output directory set: {output_dir}")

    def start_splitting(self):
        """Start the video splitting process."""
        if not self.current_video_path or not self.output_dir:
            return

        selected_points = self.split_points_table.get_selected_points()
        if not selected_points:
            QMessageBox.warning(
                self,
                "No Split Points Selected",
                "Please select at least one split point to proceed."
            )
            return

        # Prepare UI for splitting
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.start_splitting_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.select_output_btn.setEnabled(False)

        # Start splitting
        self.status_bar.showMessage("Splitting video...")
        self.video_splitter.split_video(selected_points)

    def update_progress(self, current, total):
        """Update the progress bar."""
        progress_percent = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress_percent)

    def segment_started(self, segment_num, filename):
        """Update status when a new segment starts processing."""
        self.status_bar.showMessage(f"Processing segment {segment_num}: {filename}")

    def splitting_completed(self):
        """Handle completion of the splitting process."""
        self.status_bar.showMessage("Splitting completed successfully")

        # Reset UI
        self.progress_bar.setVisible(False)
        self.start_splitting_btn.setEnabled(True)
        self.open_btn.setEnabled(True)
        self.select_output_btn.setEnabled(True)

        # Show success message
        QMessageBox.information(
            self,
            "Splitting Completed",
            f"Video has been successfully split into {len(self.split_points_table.get_selected_points())} segments."
        )

    def show_error(self, error_message):
        """Display error message."""
        self.status_bar.showMessage(f"Error: {error_message}")

        # Reset UI
        self.progress_bar.setVisible(False)
        self.start_splitting_btn.setEnabled(True)
        self.open_btn.setEnabled(True)
        self.select_output_btn.setEnabled(True)

        # Show error message
        QMessageBox.critical(
            self,
            "Error",
            f"An error occurred: {error_message}"
        )

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About MP4 Splitter",
            "MP4 Splitter v0.1.2\n\n"
            "A tool for splitting MP4 video files into segments.\n\n"
            "Built with PySide6 and MoviePy."
        )

    def update_splitting_button_state(self):
        """Update the state of the start splitting button."""
        self.start_splitting_btn.setEnabled(
            self.current_video_path is not None and
            self.output_dir is not None and
            len(self.split_points_table.split_points) > 0
        )

    def format_time(self, ms):
        """Format milliseconds into HH:MM:SS.mmm string."""
        # Convert to integers to avoid float formatting issues
        total_seconds = int(ms / 1000)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        ms = int(ms % 1000)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"

