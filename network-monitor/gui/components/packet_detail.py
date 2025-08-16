"""
Dialog window for displaying detailed information about a network packet.

This module defines the PacketDetailDialog class, which provides a scrollable
tree view interface for displaying the parsed fields of a network packet.
The dialog supports formatted display with hierarchical structure for different
protocol layers.
"""

from typing import Optional

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt

from src.packet_summary import PacketDetailInfo, PacketSummaryInfo


class PacketDetailDialog(QDialog):
    """
    Dialog window that presents detailed information about a single packet
    using a hierarchical tree structure.
    
    Displays packet information organized by protocol layers, with each
    layer showing its specific fields and values in a tree format.
    """

    def __init__(self, detail_info: PacketDetailInfo, summary_info: PacketSummaryInfo, parent: Optional[QDialog] = None):
        """
        Initialize the dialog and populate it with parsed packet data.

        Args:
            detail_info: Detailed packet information with protocol fields
            summary_info: Packet summary information for dialog title
            parent: Parent widget if any
        """
        super().__init__(parent, flags=Qt.Window)
        
        # Set dialog title with packet information
        self.setWindowTitle(f"Packet {summary_info.packet_no} ({summary_info.summary}) - Details")
        self.resize(600, 800)

        # Create and setup tree widget
        self.tree = QTreeWidget()
        self._setup_tree_widget()
        self._populate_tree(detail_info)

        # Setup dialog layout
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)
        
        # Configure dialog behavior
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.show()

    def _setup_tree_widget(self) -> None:
        """
        Configure the tree widget headers and display properties.
        
        Sets up column headers, widths, and text wrapping behavior
        for optimal packet data display.
        """
        self.tree.setHeaderLabels(["Field", "Value"])
        self.tree.setColumnCount(2)
        self.tree.setWordWrap(True)
        
        # Set column widths for optimal display
        self.tree.header().resizeSection(0, 250)  # Field name column
        self.tree.header().setStretchLastSection(True)  # Value column stretches

    def _populate_tree(self, packet: PacketDetailInfo) -> None:
        """
        Populate the tree widget with packet detail information.
        
        Creates a hierarchical view where each protocol layer is a top-level
        item with its fields as children.
        
        Args:
            packet: Detailed packet information to display
        """
        # Iterate through protocol layers and their fields
        for protocol, fields in packet.details.items():
            # Create top-level item for protocol
            top_item = QTreeWidgetItem([protocol, ""])
            
            # Add fields as child items
            for key, val in fields.items():
                child_item = QTreeWidgetItem([key, str(val)])
                top_item.addChild(child_item)
            
            # Add protocol item to tree
            self.tree.addTopLevelItem(top_item)
            
        # Expand all items by default for better visibility
        self.tree.expandAll()