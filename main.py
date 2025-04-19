#!/usr/bin/env python3
"""
MP4 Splitter - A tool for splitting MP4 video files into segments.

This is the main entry point for the application.
"""

import sys
from PySide6.QtWidgets import QApplication
from mp4splitter.main_window import MainWindow


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
