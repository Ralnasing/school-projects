"""
SnifferController module.

Provides a controller class that manages asynchronous packet sniffing
in a separate worker thread using PyQt's threading and signaling mechanisms.

This controller:
- Initializes and manages a background sniffer (SnifferWorker).
- Periodically polls a queue for captured packets.
- Forwards processed packet data to a user-defined callback.
- Communicates status and errors back to the GUI or calling code.

Designed for integration with GUI applications using PyQt5.
"""

import logging
from queue import Queue, Empty
from typing import Callable, Optional

from PyQt5.QtCore import QTimer, QObject, QThread
from scapy.packet import Packet

from src.sniffer.worker import SnifferWorker
from src.packet_summary import PacketSummaryInfo, extract_packet_summary

logger = logging.getLogger(__name__)

class SnifferController(QObject):
    """
    Controller class that manages packet sniffing in a background thread and
    handles communication with the GUI via callbacks.

    Responsibilities:
        - Starts and stops the worker sniffer thread.
        - Polls packets from a queue and invokes the provided packet_callback.
        - Forwards status and error updates via optional callbacks.
    """

    def __init__(
        self,
        interface: str,
        packet_count: int,
        packet_callback: Callable[[PacketSummaryInfo, Packet], None],
        status_callback: Optional[Callable[[str], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
        poll_interval_ms: int = 100
    ) -> None:
        """
        Initialize the SnifferController with a given interface and callbacks.

        Args:
            interface (str): Network interface to sniff packets on.
            packet_count (int): Maximum number of packets to process (0 = unlimited).
            packet_callback (Callable): Function called for each processed packet.
            status_callback (Optional[Callable]): Called with status updates (e.g., "active", "stopped").
            error_callback (Optional[Callable]): Called with error messages as strings.
            poll_interval_ms (int): Time interval in milliseconds to poll the queue.
            
        Raises:
            ValueError: If interface is empty or packet_count is negative.
            TypeError: If callbacks are not callable.
        """
        super().__init__()
        
        # Input validation
        if not interface or not interface.strip():
            raise ValueError("Interface cannot be empty")
        if packet_count < 0:
            raise ValueError("Packet count cannot be negative")
        if not callable(packet_callback):
            raise TypeError("packet_callback must be callable")
        if status_callback is not None and not callable(status_callback):
            raise TypeError("status_callback must be callable")
        if error_callback is not None and not callable(error_callback):
            raise TypeError("error_callback must be callable")

        self.packet_callback = packet_callback
        self.status_callback = status_callback
        self.error_callback = error_callback
        self.packet_count_limit = packet_count
        
        # Metrics
        self.processed_packets = 0
        self.error_count = 0

        self.packet_queue = Queue()

        self.worker = SnifferWorker(interface.strip(), packet_count, self.packet_queue)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.start_sniffing)

        self.worker.status_changed.connect(self.emit_status)
        self.worker.error_occurred.connect(self.emit_error)
        self.worker.packet_ready.connect(self._on_packet_ready)

        self.timer = QTimer()
        self.timer.setInterval(poll_interval_ms)
        self.timer.timeout.connect(self.poll_queue)
        
        self._is_running = False

    def start(self) -> None:
        """
        Start the worker thread and the polling timer for packet processing.

        Emits:
            error_callback (str): If the controller fails to start due to a runtime or attribute error.
        """
        if self._is_running:
            logger.warning("Controller is already running")
            return
            
        try:
            self.thread.start()
            self.timer.start()
            self._is_running = True
            logger.info(f"Controller started on interface {self.worker.interface}")
        except (RuntimeError, AttributeError) as e:
            error_msg = f"Failed to start controller: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            self.emit_error(error_msg)

    def stop(self) -> None:
        """
        Stop the worker thread and polling timer gracefully.

        Emits:
            error_callback (str): If stopping the controller fails.
        """
        if not self._is_running:
            logger.warning("Controller is not running")
            return
            
        try:
            self.worker.stop_sniffing()
            self.timer.stop()
            self.thread.quit()
            
            # Wait with timeout to prevent hanging
            if not self.thread.wait(5000):  # 5 seconds timeout
                logger.warning("Thread did not finish gracefully, terminating")
                self.thread.terminate()
                self.thread.wait(2000)  # Give it 2 more seconds
                
            self._is_running = False
            logger.info(f"Controller stopped. Processed {self.processed_packets} packets, {self.error_count} errors")
        except (RuntimeError, AttributeError) as e:
            error_msg = f"Failed to stop controller: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            self.emit_error(error_msg)

    def poll_queue(self) -> None:
        """
        Poll the internal packet queue and process pending packets.

        Processes up to a fixed number of packets per poll (max_per_poll).
        Extracts packet summaries and invokes the packet_callback.
        Enforces packet count limit if set.

        Emits:
            error_callback (str): If packet processing fails due to summary extraction or callback failure.
        """
        processed = 0
        max_per_poll = 10

        while processed < max_per_poll:
            # Check packet limit (0 means unlimited)
            if self.packet_count_limit > 0 and self.processed_packets >= self.packet_count_limit:
                logger.info(f"Reached packet limit of {self.packet_count_limit}, stopping")
                self.stop()
                break
                
            try:
                packet, pkt_no = self.packet_queue.get_nowait()
                summary = extract_packet_summary(packet, pkt_no)
                self.packet_callback(summary, packet)
                processed += 1
                self.processed_packets += 1
            except Empty:
                break
            except (ValueError, TypeError, AttributeError) as e:
                error_msg = f"Failed to process packet: {type(e).__name__}: {str(e)}"
                logger.error(error_msg)
                self.emit_error(error_msg)
                self.error_count += 1
                break

    def emit_status(self, status: str) -> None:
        """Emit status update via callback if provided."""
        logger.debug(f"Status changed to: {status}")
        if self.status_callback:
            try:
                self.status_callback(status)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")

    def emit_error(self, error_msg: str) -> None:
        """Emit error message via callback if provided."""
        logger.error(f"Error occurred: {error_msg}")
        self.error_count += 1
        if self.error_callback:
            try:
                self.error_callback(error_msg)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")

    def toggle(self) -> None:
        """
        Toggle sniffing state - pause if active, resume if stopped.

        Raises:
            OSError: If there's an issue with network interface
            ValueError: If there's an invalid parameter
            RuntimeError: If there's an issue with the sniffer state
            AttributeError: If the worker is not properly initialized
        """
        if not self.worker:
            raise AttributeError("Worker is not initialized")

        try:
            self.worker.toggle_sniffing()
            logger.info("Toggled sniffing state")
        except (OSError, ValueError, RuntimeError) as e:
            logger.error(f"Failed to toggle sniffing: {e}")
            # Re-raise the exception to be handled by the calling code
            raise e
    
    def _on_packet_ready(self, packet: Packet, pkt_no: int) -> None:
        """Handle packet_ready signal from worker (for future use)."""
        # This could be used for real-time packet notifications
        # Currently just logs for debugging
        logger.debug(f"Packet {pkt_no} ready for processing")
    
    def get_statistics(self) -> dict:
        """Get current processing statistics."""
        return {
            'processed_packets': self.processed_packets,
            'error_count': self.error_count,
            'queue_size': self.packet_queue.qsize(),
            'is_running': self._is_running,
            'packet_limit': self.packet_count_limit
        }
    
    def __del__(self) -> None:
        """Cleanup resources when controller is destroyed."""
        try:
            if self._is_running:
                self.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")