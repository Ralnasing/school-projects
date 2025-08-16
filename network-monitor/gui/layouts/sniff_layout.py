"""
Packet sniffing layout for network monitoring GUI.

Provides interface for controlling packet capture (start/stop/clear)
and displays captured packets in a table format.
"""

from typing import Callable, Optional

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from scapy.all import get_if_addr

from src.sniffer.controller import SnifferController
from gui.components.packet_table_widget import PacketTableWidget
from gui.gui_paths import ICON_BACK, ICON_PAUSE, ICON_PLAY, ICON_RESET
from src.packet_summary import PacketDetailInfo, PacketSummaryInfo


class SniffLayout(QWidget):
    """
    Layout for packet sniffing interface with control buttons and packet display table.
    
    Handles starting/stopping packet capture and provides controls for managing
    captured packets.
    """
    
    def __init__(
        self,
        interface: str,
        packet_count: int,
        back_callback: Callable[[], None],
        save_enable_callback: Optional[Callable[[bool], None]] = None,
        save_to_history: bool = False
    ) -> None:
        """
        Initialize the sniff layout.
        
        Args:
            interface: Network interface to sniff on
            packet_count: Number of packets to capture (0 for unlimited)
            back_callback: Callback function for back navigation
            save_enable_callback: Callback to enable/disable save functionality
            save_to_history: Legacy parameter, kept for compatibility
        """
        super().__init__()

        self.interface = interface
        self.packet_count = packet_count
        self.back_callback = back_callback
        self.sniffer: Optional[SnifferController] = None

        # Set up main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Initialize UI components
        self.setup_controls()

        # Create packet table widget
        self.packet_table = PacketTableWidget()
        if save_enable_callback:
            self.packet_table.set_save_enable_callback(save_enable_callback)
        
        self.layout.addWidget(self.packet_table)

        # Initialize packet sniffer
        self.setup_sniffer()

    def setup_controls(self) -> None:
        """
        Creates the control panel with navigation and sniffing control buttons.
        """
        control_layout = QHBoxLayout()

        # Back button for navigation
        self.back_btn = QPushButton()
        self.back_btn.setIcon(QIcon(ICON_BACK))
        self.back_btn.setToolTip("Back to interface selection")
        self.back_btn.clicked.connect(self.handle_back)
        control_layout.addWidget(self.back_btn)

        # Toggle button for start/stop sniffing
        self.toggle_btn = QPushButton()
        self.toggle_btn.setIcon(QIcon(ICON_PAUSE))
        self.toggle_btn.setToolTip("Stop packet capture")
        self.toggle_btn.clicked.connect(self.toggle_sniffing)
        control_layout.addWidget(self.toggle_btn)

        # Clear button to remove captured packets
        self.clear_btn = QPushButton()
        self.clear_btn.setIcon(QIcon(ICON_RESET))
        self.clear_btn.setToolTip("Delete captured packets")
        self.clear_btn.clicked.connect(self.clear_packets)
        control_layout.addWidget(self.clear_btn)

        control_layout.addStretch(1)

        # Interface information display
        try:
            ip = get_if_addr(self.interface)
        except Exception:
            ip = "N/A"

        self.interface_ip_label = QLabel(f"{self.interface}: {ip}")
        self.status_label = QLabel("initialization...")

        # Info panel layout
        sniff_info_layout = QVBoxLayout()
        sniff_info_layout.addWidget(self.interface_ip_label, alignment=Qt.AlignRight)
        sniff_info_layout.addWidget(self.status_label, alignment=Qt.AlignRight)

        control_layout.addLayout(sniff_info_layout)
        self.layout.addLayout(control_layout)

    def disable_sniffing_controls(self):
        """
        Disables sniffing controls and sets static view mode.
        Used when displaying pre-loaded packets.
        """
        if self.sniffer:
            self.sniffer.stop()
            self.sniffer = None

        self.toggle_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.status_label.setText("static view")
        self.status_label.setStyleSheet("color: gray;")

    def setup_sniffer(self) -> None:
        """
        Initializes and starts the packet sniffer controller.
        """
        try:
            self.sniffer = SnifferController(
                interface=self.interface,
                packet_count=self.packet_count,
                packet_callback=self.packet_table.add_packet_callback,
                status_callback=self.update_status,
                error_callback=self.show_error
            )
            self.sniffer.start()
        except Exception as e:
            QMessageBox.critical(self, "Sniffer Initialization Error", f"Failed to start sniffer:\n{e}")
            self.update_status("stopped")

    def stop_sniffer(self) -> None:
        """
        Stops the packet sniffer if it's running.
        """
        if self.sniffer:
            self.sniffer.stop()
            self.sniffer = None

    def show_error(self, message: str) -> None:
        """
        Displays error message to the user.
        
        Args:
            message: Error message to display
        """
        QMessageBox.critical(self, "Sniffer Error", message)

    def toggle_sniffing(self) -> None:
        """
        Toggles packet sniffing on/off.
        """
        if not self.sniffer:
            QMessageBox.warning(self, "Sniffer Not Initialized", "Sniffer is not initialized.")
            return

        try:
            self.sniffer.toggle()
        except (OSError, ValueError, RuntimeError, AttributeError) as e:
            self.show_error(f"Failed to toggle sniffer:\n{type(e).__name__}: {str(e)}")

    def clear_packets(self) -> None:
        """
        Clears all captured packets from the table.
        """
        self.packet_table.clear_packets()

    def handle_back(self) -> None:
        """
        Handles back button click - stops sniffer and navigates back.
        """
        self.stop_sniffer()
        self.back_callback()

    def load_packets(self, packets: list[tuple[PacketSummaryInfo, PacketDetailInfo]]) -> None:
        """
        Loads pre-captured packets into the table view.
        
        Args:
            packets: List of packet data tuples (summary, detail)
        """
        self.packet_table.clear_packets()
        for summary, detail in packets:
            self.packet_table.display_packet(summary, detail)

        self.disable_sniffing_controls()

    def update_status(self, status: str) -> None:
        """
        Updates the sniffer status display and control button states.
        
        Args:
            status: Current sniffer status ("active" or "stopped")
        """
        status_map = {
            "active": {
                "text": "active",
                "color": "green",
                "icon": ICON_PAUSE,
            },
            "stopped": {
                "text": "stopped",
                "color": "red",
                "icon": ICON_PLAY,
            }
        }

        if status not in status_map:
            QMessageBox.critical(self, "Unknown Status", f"Received unknown sniffer status: '{status}'")
            return

        config = status_map[status]
        self.status_label.setText(config["text"])
        self.status_label.setStyleSheet(f"color: {config['color']};")
        self.toggle_btn.setIcon(QIcon(config["icon"]))