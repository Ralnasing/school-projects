"""
Author: Petr Kalabis (kalabpe4)
File: gui/layouts/interface_layout.py

Interface selection layout for a network sniffing GUI.

Displays available network interfaces and allows the user to
select one and specify the number of packets to capture.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSpinBox, QLabel, QHBoxLayout, QFrame, QSizePolicy, QScrollArea
from PyQt5.QtCore import Qt

from scapy.all import get_if_list, get_if_addr

class InterfaceLayout(QWidget):
    """
    A layout that displays network interfaces as buttons and
    allows the user to specify initial settings for packet capture.
    """
    def __init__(self, start_sniff_callback):
        """
        Initialize the interface selection layout.

        Args:
            start_sniff_callback (Callable): Callback to invoke with (interface, packet_count) when user starts sniffing.
        """
        super().__init__()

        self.start_sniff_callback = start_sniff_callback

        self.layout = QHBoxLayout()

        self.setup_interface_panel()
        self.setup_capture_settings_panel()

        self.setLayout(self.layout)

    def setup_interface_panel(self) -> None:
        """
        Creates the left-side panel listing available network interfaces.
        Each interface is a button that triggers packet sniffing when clicked.
        """
        button_layout = QVBoxLayout()
        button_layout.addStretch(1)

        # Interface detection using scapy and adding as buttons
        for iface in get_if_list():
            try:
                ip = get_if_addr(iface)
            except Exception:
                ip = "N/A"

            btn = QPushButton(f"{iface}: {ip}")
            btn.setFixedHeight(40)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda checked, iface=iface: self.start_sniffing(iface))
            button_layout.addWidget(btn)

        button_layout.addStretch(1)

        # Create scrollable container for interface buttons
        container_widget = QWidget()
        container_widget.setLayout(button_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container_widget)

        self.layout.addWidget(scroll_area, 1)

    def setup_capture_settings_panel(self) -> None:
        """
        Creates the right-side panel for setting packet capture options.

        Contains a spin box to let the user specify the number of packets to capture.
        A value of 0 indicates unlimited capture.
        """
        # Spin box for packet count selection
        self.packet_count_spin = QSpinBox()
        self.packet_count_spin.setRange(0, 1_000_000)
        self.packet_count_spin.setValue(0)
        self.packet_count_spin.setAlignment(Qt.AlignCenter)

        # Create layout for capture settings
        capture_settings_panel_layout = QVBoxLayout()
        capture_settings_panel_layout.addStretch(1)
        capture_settings_panel_layout.addWidget(QLabel("Number of captured packets (0 = inf):"), alignment=Qt.AlignCenter)
        capture_settings_panel_layout.addWidget(self.packet_count_spin, alignment=Qt.AlignCenter)
        capture_settings_panel_layout.addStretch(1)

        # Add settings panel to frame and main layout
        capture_settings_frame = QFrame()
        capture_settings_frame.setLayout(capture_settings_panel_layout)
        self.layout.addWidget(capture_settings_frame, 2)

    def start_sniffing(self, iface):
        """
        Calls the sniffing start callback with selected interface and packet count.

        Args:
            iface (str): Network interface name selected by the user.
        """
        packet_count = self.packet_count_spin.value()
        self.start_sniff_callback(iface, packet_count, False)