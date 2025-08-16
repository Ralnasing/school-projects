"""
SnifferWorker module.

Provides asynchronous packet sniffing functionality using scapy's
AsyncSniffer. Operates in its own QObject to run in a QThread. Captured
packets are pushed to a queue for later processing by the controller.
"""

import logging
import threading
from queue import Queue
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal
from scapy.all import AsyncSniffer, Packet, get_if_list

logger = logging.getLogger(__name__)

class SnifferWorker(QObject):
    """
    Worker class that handles asynchronous packet sniffing using AsyncSniffer.

    Emits:
        packet_ready (object, object): Emitted when a packet is ready for processing.
        error_occurred (str): Emitted if an exception is raised during operation.
        status_changed (str): 'active' when sniffing starts, 'stopped' when stopped.
    """

    packet_ready = pyqtSignal(object, object)
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, interface: str, packet_count: int, packet_queue: Queue) -> None:
        """
        Initialize the sniffer worker.

        Args:
            interface (str): Network interface to sniff on.
            packet_count (int): Expected number of packets (0 = unlimited, for reference only).
            packet_queue (Queue): Queue for transferring packets to the controller.
            
        Raises:
            ValueError: If interface is invalid or packet_count is negative.
            TypeError: If packet_queue is not a Queue instance.
        """
        super().__init__()
        
        # Input validation
        if not interface or not interface.strip():
            raise ValueError("Interface cannot be empty")
        
        # Validate interface exists (optional - might fail on some systems)
        try:
            available_interfaces = get_if_list()
            if interface not in available_interfaces:
                logger.warning(f"Interface '{interface}' not found in available interfaces: {available_interfaces}")
        except Exception as e:
            logger.debug(f"Could not validate interface: {e}")
        
        if not isinstance(packet_queue, Queue):
            raise TypeError("packet_queue must be a Queue instance")
        if packet_count < 0:
            raise ValueError("packet_count cannot be negative")
        
        self.interface = interface.strip()
        self.packet_count_limit = packet_count
        self.packet_queue = packet_queue
        self.sniffer: Optional[AsyncSniffer] = None
        self.packet_counter = 1
        self.paused = False
        
        # Thread safety for packet counter
        self._counter_lock = threading.Lock()
        
        # Statistics
        self.total_packets_captured = 0
        self.errors_count = 0

    def start_sniffing(self) -> None:
        """
        Start asynchronous packet sniffing on the configured interface.

        Emits:
            status_changed (str): "active" when sniffing starts.
            error_occurred (str): If an exception occurs during sniffer startup.
        """
        try:
            if self.sniffer and self.sniffer.running:
                logger.warning("Sniffer is already running")
                return
                
            self.sniffer = AsyncSniffer(
                iface=self.interface,
                prn=self.enqueue_packet,
                store=False
            )
            self.sniffer.start()
            self.paused = False
            logger.info(f"Started sniffing on interface {self.interface}")
            self.status_changed.emit("active")
        except (OSError, ValueError, RuntimeError) as e:
            error_msg = f"Sniffer failed to start: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            self.errors_count += 1
            self.error_occurred.emit(error_msg)

    def stop_sniffing(self) -> None:
        """
        Stop the sniffer if it is currently running.

        Emits:
            status_changed (str): "stopped" when sniffing stops.
            error_occurred (str): If an exception occurs while stopping.
        """
        try:
            if self.sniffer and self.sniffer.running:
                self.sniffer.stop()
                logger.info(f"Stopped sniffing. Captured {self.total_packets_captured} packets")
                self.status_changed.emit("stopped")
            else:
                logger.debug("Sniffer was not running")
        except (RuntimeError, AttributeError) as e:
            error_msg = f"Failed to stop sniffer: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            self.errors_count += 1
            self.error_occurred.emit(error_msg)

    def toggle_sniffing(self) -> None:
        """
        Toggle the sniffer between active and paused states.
        
        Note: This creates a new AsyncSniffer instance when resuming,
        as AsyncSniffer doesn't support pause/resume functionality.

        Emits:
            status_changed (str): "active" if resumed, "stopped" if paused.
            error_occurred (str): If an exception occurs during toggle.
        """
        try:
            if self.sniffer and self.sniffer.running:
                # Stop current sniffer
                self.sniffer.stop()
                self.paused = True
                logger.info("Sniffing paused")
                self.status_changed.emit("stopped")
            else:
                # Start new sniffer (AsyncSniffer doesn't support resume)
                # Clean up old sniffer reference
                if self.sniffer:
                    del self.sniffer
                    
                self.sniffer = AsyncSniffer(
                    iface=self.interface,
                    prn=self.enqueue_packet,
                    store=False
                )
                self.sniffer.start()
                self.paused = False
                logger.info("Sniffing resumed")
                self.status_changed.emit("active")
        except (OSError, ValueError, RuntimeError) as e:
            error_msg = f"Failed to toggle sniffer: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            self.errors_count += 1
            self.error_occurred.emit(error_msg)

    def enqueue_packet(self, packet: Packet) -> None:
        """
        Enqueue a received packet into the packet queue.
        This method is called by AsyncSniffer for each captured packet.

        Args:
            packet (Packet): A Scapy packet to be processed.

        Emits:
            packet_ready (object, object): When packet is successfully queued.
            error_occurred (str): If the packet cannot be queued.
        """
        try:
            # Thread-safe counter increment
            with self._counter_lock:
                current_pkt_no = self.packet_counter
                self.packet_counter += 1
                self.total_packets_captured += 1
            
            # Add packet to queue
            self.packet_queue.put((packet, current_pkt_no))
            
            # Emit signal that packet is ready
            self.packet_ready.emit(packet, current_pkt_no)
            
            logger.debug(f"Enqueued packet {current_pkt_no}")
            
        except (TypeError, AttributeError) as e:
            error_msg = f"Failed to enqueue packet: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            self.errors_count += 1
            self.error_occurred.emit(error_msg)
    
    def get_statistics(self) -> dict:
        """Get current worker statistics."""
        return {
            'interface': self.interface,
            'total_packets_captured': self.total_packets_captured,
            'errors_count': self.errors_count,
            'is_running': self.sniffer.running if self.sniffer else False,
            'is_paused': self.paused,
            'packet_count_limit': self.packet_count_limit,
            'queue_size': self.packet_queue.qsize()
        }
    
    def __del__(self) -> None:
        """Cleanup resources when worker is destroyed."""
        try:
            if self.sniffer and self.sniffer.running:
                self.sniffer.stop()
                logger.debug("Cleaned up sniffer in destructor")
        except Exception as e:
            logger.error(f"Error during worker cleanup: {e}")