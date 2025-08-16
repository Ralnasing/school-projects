"""
File menu component for network monitoring application.

Provides functionality for saving captured packets to JSON files
and loading previously saved packet data.
"""

from typing import Callable, List, Tuple, Any
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QMessageBox
from src.json import save_packets_to_json, load_packets_from_json


class FileMenu:
    """
    File menu handler for packet data operations.
    
    Manages save/load operations for packet data in JSON format,
    providing user interface for file selection and error handling.
    """
    
    def __init__(self, parent, get_packets_callback: Callable[[], List[Any]]):
        """
        Initialize the file menu.
        
        Args:
            parent: Parent widget for dialog positioning
            get_packets_callback: Function that returns current packet data
        """
        self.parent = parent
        self.get_packets = get_packets_callback

        # Create main menu
        self.menu = QMenu()

        # Save action - initially disabled until packets are available
        self.save_action = QAction("Save as JSON", parent)
        self.save_action.setEnabled(False)
        self.save_action.triggered.connect(self.save_as_json)

        # Open action - always available
        self.open_action = QAction("Open JSON", parent)
        self.open_action.triggered.connect(self.open_from_json)

        # Add actions to menu
        self.menu.addAction(self.save_action)
        self.menu.addAction(self.open_action)

    def save_as_json(self) -> None:
        """
        Save current packet data to a JSON file.
        
        Opens file dialog for user to select save location and
        handles the saving process with error checking.
        """
        # Get current packets from callback
        packets = self.get_packets()
        if not packets:
            QMessageBox.warning(self.parent, "No Data", "No packet data available to save.")
            return

        # Open save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, 
            "Save Packet Data", 
            "", 
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return  # User cancelled dialog
            
        # Ensure .json extension
        if not file_path.endswith(".json"):
            file_path += ".json"
            
        try:
            # Attempt to save packets
            save_packets_to_json(file_path, packets)
            QMessageBox.information(
                self.parent, 
                "Save Successful", 
                f"Packet data successfully saved to:\n{file_path}"
            )
        except PermissionError:
            QMessageBox.critical(
                self.parent, 
                "Permission Error", 
                f"Access denied when trying to write to:\n{file_path}\n\nPlease check file permissions or choose a different location."
            )
        except OSError as e:
            QMessageBox.critical(
                self.parent, 
                "File System Error", 
                f"Failed to save file:\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.parent, 
                "Save Error", 
                f"An unexpected error occurred while saving:\n{str(e)}"
            )

    def open_from_json(self) -> None:
        """
        Load packet data from a JSON file.
        
        Opens file dialog for user to select file and loads
        the packet data with comprehensive error handling.
        """
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, 
            "Open Packet Data", 
            "", 
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return  # User cancelled dialog
            
        try:
            # Attempt to load packets
            packets = load_packets_from_json(file_path)
            
            if not packets:
                QMessageBox.warning(
                    self.parent, 
                    "Empty File", 
                    "The selected file contains no packet data."
                )
                return
                
            # Load packets into view
            self.parent.load_packets_into_view(packets)
            QMessageBox.information(
                self.parent, 
                "Load Successful", 
                f"Successfully loaded {len(packets)} packets from:\n{file_path}"
            )
            
        except FileNotFoundError:
            QMessageBox.critical(
                self.parent, 
                "File Not Found", 
                f"The selected file could not be found:\n{file_path}"
            )
        except PermissionError:
            QMessageBox.critical(
                self.parent, 
                "Permission Error", 
                f"Access denied when trying to read:\n{file_path}\n\nPlease check file permissions."
            )
        except ValueError as e:
            QMessageBox.critical(
                self.parent, 
                "Invalid File Format", 
                f"The selected file is not a valid packet data file:\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.parent, 
                "Load Error", 
                f"An unexpected error occurred while loading:\n{str(e)}"
            )

    def set_save_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the save action based on data availability.
        
        Args:
            enabled: True to enable save action, False to disable
        """
        self.save_action.setEnabled(enabled)