"""
Main window module for network monitoring application.

This module contains the MainWindow class which serves as the primary
interface for the network packet monitoring application. It manages
navigation between different views, handles theme switching, and
coordinates packet capture operations.
"""

from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QStackedLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt

from gui.layouts.interface_layout import InterfaceLayout
from gui.layouts.sniff_layout import SniffLayout
from gui.components.toggle import ToggleSwitch
from gui.top_menu.file_menu import FileMenu
from gui.gui_paths import STYLE_DARK, STYLE_LIGHT


class MainWindow(QMainWindow):
    """
    Main window of the network monitoring application.
    Manages switching between different layouts and provides basic functionality.
    """
    
    def __init__(self) -> None:
        super().__init__()
        # Set basic window properties
        self.setWindowTitle("Network monitor")
        self.setMinimumSize(700, 400)

        # Instance of the packet sniffing layout
        self.sniff_widget: Optional[SniffLayout] = None
        # View history for back navigation
        self.view_history = []

        # Create central widget and stack layout for screen switching
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.stack_layout = QStackedLayout()
        self.setup_interface_layout()

        # Initialize menu
        self.file_menu = FileMenu(self, self.get_current_packets)

        # Set up header with navigation buttons
        self.setup_header()

        # Assemble main layout
        outer_layout = QVBoxLayout()
        outer_layout.addWidget(self.header_widget)
        outer_layout.addLayout(self.stack_layout)
        central_widget.setLayout(outer_layout)

        # Apply default light theme
        self.apply_theme("light")

    def setup_header(self) -> None:
        """
        Creates header with navigation buttons and theme toggle.
        """
        self.header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 5, 10, 5)

        # Create File navigation button
        file_button = QPushButton("File")
        file_button.setFixedSize(90, 30)
        file_button.setFlat(True)
        file_button.setCursor(Qt.PointingHandCursor)
        file_button.setMenu(self.file_menu.menu)
        header_layout.addWidget(file_button)

        # Theme toggle (light/dark)
        self.theme_toggle = ToggleSwitch()
        self.theme_toggle.setChecked(False)  # Default light theme
        self.theme_toggle.clicked.connect(self.toggle_theme)

        # Add spacer and theme toggle on the right
        header_layout.addStretch()
        header_layout.addWidget(self.theme_toggle)

        self.header_widget.setLayout(header_layout)
        self.header_widget.setObjectName("HeaderWidget")

    def setup_interface_layout(self) -> None:
        """
        Sets up initial layout with network interface selection.
        """
        self.interface_widget = InterfaceLayout(self.show_sniff_layout)

        interface_screen = QWidget()
        interface_layout = QVBoxLayout()
        interface_layout.addWidget(self.interface_widget)
        interface_screen.setLayout(interface_layout)

        # Add to stack layout and set as current
        self.stack_layout.addWidget(interface_screen)
        self.stack_layout.setCurrentWidget(interface_screen)

    def show_interface_layout(self) -> None:
        """
        Shows main interface layout and clears application state.
        """
        # Stop and remove sniff widget if exists
        if self.sniff_widget:
            self.sniff_widget.stop_sniffer()
            self.stack_layout.removeWidget(self.sniff_widget)
            self.sniff_widget.deleteLater()
            self.sniff_widget = None

        # Switch to main screen
        self.stack_layout.setCurrentIndex(0)
        self.set_save_enabled(False)
        self.view_history.clear()

    def show_sniff_layout(self, interface: str, packet_count: int, save_to_history: bool) -> None:
        """
        Shows layout for packet sniffing with given parameters.
        
        Args:
            interface: Network interface name
            packet_count: Number of packets to capture
            save_to_history: Whether to save to history
        """
        # Create new sniff layout
        self.sniff_widget = SniffLayout(
            interface=interface,
            packet_count=packet_count,
            back_callback=self.go_back,
            save_enable_callback=self.set_save_enabled,
            save_to_history=save_to_history
        )

        # Wrap in widget and add to stack
        sniff_screen = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.sniff_widget)
        sniff_screen.setLayout(layout)

        # Save current screen to history and switch to new one
        self.view_history.append(self.stack_layout.currentWidget())
        self.stack_layout.addWidget(sniff_screen)
        self.stack_layout.setCurrentWidget(sniff_screen)

    def go_back(self):
        """
        Navigate back to previous screen according to view history.
        """
        if self.view_history:
            previous = self.view_history.pop()
            self.stack_layout.setCurrentWidget(previous)

    def toggle_theme(self, checked: bool) -> None:
        """
        Toggles between light and dark theme.
        
        Args:
            checked: True for dark theme, False for light theme
        """
        self.apply_theme("dark" if checked else "light")

    def apply_theme(self, theme_name: str) -> None:
        """
        Applies chosen theme to the entire application.
        
        Args:
            theme_name: Theme name ("light" or "dark")
        """
        theme_path = None

        if theme_name == "light":
            theme_path = STYLE_LIGHT
        elif theme_name == "dark":
            theme_path = STYLE_DARK
        else:
            QMessageBox.critical(self, "Theme Error", f"A style called '{theme_name}' cannot be loaded.")
            return

        # Load and apply CSS style
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            QMessageBox.critical(self, "Theme Error", f"Failed to load theme file:\n{e}")

    def set_save_enabled(self, enabled: bool) -> None:
        """
        Enables or disables save option in File menu.
        
        Args:
            enabled: True to enable saving
        """
        self.file_menu.set_save_enabled(enabled)

    def get_current_packets(self):
        """
        Returns currently captured packets from sniff widget.
        
        Returns:
            List of packets or empty list
        """
        if self.sniff_widget:
            return self.sniff_widget.packet_table.model.packets
        return []

    def load_packets_into_view(self, packets):
        """
        Loads packets into view for examination.
        
        Args:
            packets: List of packets to display
        """
        # If sniff widget doesn't exist, create empty one
        if not self.sniff_widget:
            self._prepare_empty_sniff_view()

        # Load packets and enable saving
        self.sniff_widget.load_packets(packets)
        self.set_save_enabled(True)

    def _prepare_empty_sniff_view(self):
        """
        Prepares empty sniff view for displaying loaded packets.
        """
        self.sniff_widget = SniffLayout(
            interface="static",  # Static interface for loaded packets
            packet_count=0,
            back_callback=self.go_back
        )
        sniff_screen = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.sniff_widget)
        sniff_screen.setLayout(layout)

        # Add to history and display
        self.view_history.append(self.stack_layout.currentWidget())
        self.stack_layout.addWidget(sniff_screen)
        self.stack_layout.setCurrentWidget(sniff_screen)