"""
Split points table component for the MP4 Splitter application.
"""

from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView, 
                              QCheckBox, QWidget, QHBoxLayout)
from PySide6.QtCore import Qt


class SplitPoint:
    """
    Class representing a video split point with start and end times.
    """
    def __init__(self, start_time, end_time=None):
        self.start_time = start_time
        self.end_time = end_time
        self.selected = True
        
    @property
    def duration(self):
        """Calculate the duration of the segment."""
        if self.end_time is None or self.start_time is None:
            return 0
        return self.end_time - self.start_time


class SplitPointsTable(QTableWidget):
    """
    Table widget for managing video split points.
    """
    def __init__(self):
        super().__init__()
        self.split_points = []
        self.setup_table()
        
    def setup_table(self):
        """Set up the table structure."""
        self.setColumnCount(4)  # Checkbox, Start, End, Duration
        self.setHorizontalHeaderLabels(["", "Start", "End", "Duration"])
        
        # Set column widths
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.setColumnWidth(0, 30)
        
        # Enable editing for time cells
        self.cellChanged.connect(self.cell_edited)
        
    def add_split_point(self, current_time):
        """Add a new split point at the current time."""
        # If this is the first split point, set start to 0
        if not self.split_points:
            start_time = 0
        else:
            # Use the end time of the last split point as start
            start_time = self.split_points[-1].end_time
            
        split_point = SplitPoint(start_time, current_time)
        self.split_points.append(split_point)
        
        # Update the table
        self.update_table()
        
        # If this is not the first point, also update the previous point's end time
        if len(self.split_points) > 1:
            self.split_points[-2].end_time = start_time
            self.update_table()
            
    def update_table(self):
        """Update the table display with current split points."""
        # Block signals during update to prevent recursive calls
        self.blockSignals(True)
        
        self.setRowCount(len(self.split_points))
        
        for i, point in enumerate(self.split_points):
            # Checkbox column
            checkbox = QCheckBox()
            checkbox.setChecked(point.selected)
            
            # Create a widget to center the checkbox
            checkbox_widget = QWidget()
            layout = QHBoxLayout(checkbox_widget)
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            
            checkbox.stateChanged.connect(lambda state, row=i: self.toggle_selection(row, state))
            self.setCellWidget(i, 0, checkbox_widget)
            
            # Start time
            start_item = QTableWidgetItem(self.format_time(point.start_time))
            self.setItem(i, 1, start_item)
            
            # End time
            end_item = QTableWidgetItem(self.format_time(point.end_time))
            self.setItem(i, 2, end_item)
            
            # Duration
            duration_item = QTableWidgetItem(self.format_time(point.duration))
            duration_item.setFlags(duration_item.flags() & ~Qt.ItemIsEditable)  # Make duration non-editable
            self.setItem(i, 3, duration_item)
            
        self.blockSignals(False)
        
    def toggle_selection(self, row, state):
        """Toggle the selection state of a split point."""
        if row < len(self.split_points):
            self.split_points[row].selected = (state == Qt.Checked)
            
    def cell_edited(self, row, column):
        """Handle manual editing of time cells."""
        if row >= len(self.split_points) or column not in [1, 2]:
            return
            
        try:
            # Get the edited text
            time_str = self.item(row, column).text()
            time_ms = self.parse_time(time_str)
            
            # Update the appropriate time
            if column == 1:  # Start time
                self.split_points[row].start_time = time_ms
                
                # Update previous end time if needed
                if row > 0:
                    self.split_points[row-1].end_time = time_ms
            else:  # End time
                self.split_points[row].end_time = time_ms
                
                # Update next start time if needed
                if row < len(self.split_points) - 1:
                    self.split_points[row+1].start_time = time_ms
                    
            # Update the table to reflect changes
            self.update_table()
            
        except ValueError:
            # Reset to original value if parsing fails
            self.update_table()
            
    def parse_time(self, time_str):
        """Parse a time string (HH:MM:SS.mmm) to milliseconds."""
        try:
            hours, minutes, rest = time_str.split(':')
            seconds, milliseconds = rest.split('.')
            
            total_ms = (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) * 1000 + int(milliseconds)
            return total_ms
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}")
            
    def format_time(self, ms):
        """Format milliseconds as HH:MM:SS.mmm."""
        if ms is None:
            return "00:00:00.000"
            
        seconds = ms // 1000
        minutes = seconds // 60
        hours = minutes // 60
        
        return f"{hours:02d}:{minutes % 60:02d}:{seconds % 60:02d}.{ms % 1000:03d}"
        
    def get_selected_points(self):
        """Get a list of selected split points."""
        return [point for point in self.split_points if point.selected]
