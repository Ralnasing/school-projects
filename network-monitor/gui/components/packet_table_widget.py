"""
Packet table widget for displaying captured network packets.

Provides a table view with sorting capabilities for displaying packet
summary information and detailed packet inspection on double-click.
"""

from typing import Callable, Union, Optional, Any
import ipaddress

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView, QSizePolicy, QHeaderView
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, pyqtSignal, pyqtSlot

from scapy.packet import Packet
from src.packet_summary import PacketSummaryInfo, PacketDetailInfo, extract_packet_details
from gui.components.packet_detail import PacketDetailDialog


class PacketTableModel(QAbstractTableModel):
    """
    Table model for displaying packet summary information.
    
    Provides data for the packet table view with support for sorting
    and dynamic packet addition/removal.
    """
    
    # Column headers for the packet table
    HEADERS = ["No", "Time", "Proto", "Src", "Dst", "Len", "Info"]

    def __init__(self) -> None:
        """Initialize the packet table model with empty packet list."""
        super().__init__()
        self.packets: list[tuple[PacketSummaryInfo, Union[Packet, PacketDetailInfo]]] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Return the number of packets in the model.
        
        Args:
            parent: Parent model index (unused)
            
        Returns:
            Number of packets
        """
        return len(self.packets)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Return the number of columns in the model.
        
        Args:
            parent: Parent model index (unused)
            
        Returns:
            Number of columns
        """
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Optional[Any]:
        """
        Return data for the given index and role.
        
        Args:
            index: Model index specifying row and column
            role: Data role (DisplayRole supported)
            
        Returns:
            Data value or None if invalid
        """
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        if index.row() >= len(self.packets):
            return None

        summary, _ = self.packets[index.row()]
        col = index.column()

        # Column data getters mapping
        getters = [
            lambda p: p.packet_no,      # Packet number
            lambda p: p.timestamp,      # Timestamp
            lambda p: p.protocol,       # Protocol
            lambda p: p.src,           # Source address
            lambda p: p.dst,           # Destination address
            lambda p: p.length,        # Packet length
            lambda p: p.summary,       # Packet summary
        ]

        return getters[col](summary) if 0 <= col < len(getters) else None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Optional[str]:
        """
        Return header data for the given section and orientation.
        
        Args:
            section: Header section index
            orientation: Header orientation
            role: Data role
            
        Returns:
            Header text or None
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if 0 <= section < len(self.HEADERS):
                return self.HEADERS[section]
        return None

    def add_packet(self, summary: PacketSummaryInfo, raw_packet: Union[Packet, PacketDetailInfo]) -> None:
        """
        Add a new packet to the model.
        
        Args:
            summary: Packet summary information
            raw_packet: Raw packet or detailed packet info
        """
        row_count = len(self.packets)
        self.beginInsertRows(QModelIndex(), row_count, row_count)
        self.packets.append((summary, raw_packet))
        self.endInsertRows()

    def clear(self) -> None:
        """Remove all packets from the model."""
        self.beginResetModel()
        self.packets.clear()
        self.endResetModel()

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:
        """
        Sort packets by the specified column.
        
        Args:
            column: Column index to sort by
            order: Sort order (ascending/descending)
        """
        if not self.packets or column < 0 or column >= len(self.HEADERS):
            return

        # Define sorting key functions for each column
        key_funcs = [
            lambda p: p[0].packet_no,                    # Packet number
            lambda p: p[0].timestamp,                    # Timestamp
            lambda p: p[0].protocol,                     # Protocol
            lambda p: self._safe_ip_sort(p[0].src),      # Source IP
            lambda p: self._safe_ip_sort(p[0].dst),      # Destination IP
            lambda p: p[0].length,                       # Length
            lambda p: p[0].summary,                      # Summary
        ]

        try:
            self.layoutAboutToBeChanged.emit()
            self.packets.sort(
                key=key_funcs[column], 
                reverse=(order == Qt.DescendingOrder)
            )
            self.layoutChanged.emit()
        except Exception:
            # If sorting fails, emit layout changed to refresh view
            self.layoutChanged.emit()

    def _safe_ip_sort(self, address: str) -> tuple:
        """
        Safely extract IP address for sorting, handling ports and invalid IPs.
        
        Args:
            address: IP address string, possibly with port
            
        Returns:
            Tuple for sorting (IP address object, port)
        """
        try:
            # Handle address:port format
            if ':' in address:
                ip_part = address.split(':')[0]
                port_part = int(address.split(':')[1]) if len(address.split(':')) > 1 else 0
            else:
                ip_part = address
                port_part = 0
                
            return (ipaddress.ip_address(ip_part), port_part)
        except (ValueError, IndexError):
            # Fallback to string sorting for non-IP addresses
            return (address, 0)


class PacketTableWidget(QWidget):
    """
    Widget for displaying network packets in a table format.
    
    Provides functionality for packet display, sorting, and detailed
    packet inspection via double-click.
    """
    
    # Signal emitted when a packet is received
    packet_received = pyqtSignal(object, object)  # summary, raw packet or detail

    def __init__(self, max_packets_display: int = 100000) -> None:
        """
        Initialize the packet table widget.
        
        Args:
            max_packets_display: Maximum number of packets to keep in view
        """
        super().__init__()
        self.max_packets_display = max_packets_display
        
        # Initialize table model and view
        self.model = PacketTableModel()
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSortingEnabled(True)

        # Configure table headers
        header = self.view.horizontalHeader()
        header.setVisible(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        # Set column widths for optimal display
        self._setup_column_widths()

        # Configure table behavior
        self.view.verticalHeader().setVisible(False)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setEditTriggers(QTableView.NoEditTriggers)
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Setup layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setLayout(layout)

        # Connect signals
        self.packet_received.connect(self.display_packet)
        self.view.doubleClicked.connect(self.show_packet_details)

        # Callback for enabling save functionality
        self.save_enable_callback: Optional[Callable[[bool], None]] = None

    def _setup_column_widths(self) -> None:
        """Configure optimal column widths for packet display."""
        column_widths = [50, 120, 80, 180, 180, 60]  # No, Time, Proto, Src, Dst, Len
        
        for i, width in enumerate(column_widths):
            if i < self.model.columnCount():
                self.view.setColumnWidth(i, width)

    def set_save_enable_callback(self, callback: Callable[[bool], None]) -> None:
        """
        Set callback function to enable/disable save functionality.
        
        Args:
            callback: Function to call when save should be enabled/disabled
        """
        self.save_enable_callback = callback

    @pyqtSlot(object, object)
    def display_packet(self, summary: PacketSummaryInfo, raw_or_detail: Union[Packet, PacketDetailInfo]) -> None:
        """
        Display a new packet in the table.
        
        Args:
            summary: Packet summary information
            raw_or_detail: Raw packet data or detailed packet info
        """
        # Check if user is at bottom for auto-scrolling
        scrollbar = self.view.verticalScrollBar()
        user_at_bottom = scrollbar.value() >= scrollbar.maximum() - 5

        # Add packet to model
        self.model.add_packet(summary, raw_or_detail)

        # Remove oldest packet if we exceed maximum display count
        if self.model.rowCount() > self.max_packets_display:
            self.model.beginRemoveRows(QModelIndex(), 0, 0)
            del self.model.packets[0]
            self.model.endRemoveRows()

        # Auto-scroll to bottom if user was already at bottom
        if user_at_bottom:
            self.view.scrollToBottom()

        # Enable save functionality when packets are available
        if self.save_enable_callback:
            self.save_enable_callback(True)

    @pyqtSlot(QModelIndex)
    def show_packet_details(self, index: QModelIndex) -> None:
        """
        Show detailed packet information in a dialog.
        
        Args:
            index: Model index of the selected packet
        """
        if not index.isValid() or index.row() >= len(self.model.packets):
            return

        summary, detail_or_packet = self.model.packets[index.row()]

        # Extract packet details if we have raw packet data
        if isinstance(detail_or_packet, Packet):
            try:
                detail = extract_packet_details(detail_or_packet)
                # Cache the extracted details for future use
                self.model.packets[index.row()] = (summary, detail)
            except Exception:
                # If extraction fails, use empty detail info
                detail = PacketDetailInfo(details={})
        else:
            detail = detail_or_packet

        # Show packet detail dialog
        try:
            dialog = PacketDetailDialog(detail_info=detail, summary_info=summary, parent=self)
            dialog.exec_()
        except Exception:
            # Silently handle dialog creation errors
            pass

    def add_packet_callback(self, summary: PacketSummaryInfo, raw_or_detail: Union[Packet, PacketDetailInfo]) -> None:
        """
        Callback function for adding packets (emits signal).
        
        Args:
            summary: Packet summary information
            raw_or_detail: Raw packet data or detailed packet info
        """
        self.packet_received.emit(summary, raw_or_detail)

    def clear_packets(self) -> None:
        """Remove all packets from the table."""
        self.model.clear()