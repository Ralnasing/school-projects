"""
Author: Petr Kalabis (kalabpe4)
File: src/protocol_analysis/protocols/quic.py

Implements the QUIC protocol analyzer.
Detects QUIC packets in UDP, extracts version, connection IDs, and header type.
"""

from dataclasses import dataclass

from scapy.layers.inet import UDP
from scapy.packet import Raw

from src.protocol_analysis.protocols.protocol import Protocol


@dataclass
class QUICInfo:
    """
    Structured data representation of QUIC packet fields.

    Attributes:
        version (str): QUIC version in hexadecimal.
        dcid (str): Destination Connection ID (hex).
        scid (str): Source Connection ID (hex).
        is_long_header (bool): True if QUIC uses long header format.
        packet_type (str): Type of the QUIC packet (Initial, Handshake, etc.).
    """
    version: str
    dcid: str
    scid: str
    is_long_header: bool
    packet_type: str


class QUICProtocol(Protocol):
    """
    QUIC protocol analyzer.

    Recognizes QUIC traffic over UDP on port 443, checks for long headers,
    and parses version and connection identifiers.
    """

    QUIC_TYPE = {
        0x00: "Initial",
        0x01: "0-RTT",
        0x02: "Handshake",
        0x03: "Retry"
    }

    def identify(self) -> bool:
        """
        Determine if the packet likely contains QUIC traffic.

        Return:
            bool: True if packet matches QUIC heuristics.
        """
        if UDP in self.packet and Raw in self.packet:
            try:
                udp = self.packet[UDP]
                payload = self.packet[Raw].load
                if udp.dport == 443 or udp.sport == 443:
                    first_byte = payload[0]
                    is_long_header = (first_byte & 0x80) != 0
                    return is_long_header
            except (IndexError, AttributeError):
                return False
        return False

    def parse_layer_details(self) -> dict:
        """
        Parse fields from a QUIC long header.

        Return:
            dict: Parsed QUIC fields including version and connection IDs.
        """
        try:
            payload = self.packet[Raw].load
            version = "Unknown"
            dcid = ""
            scid = ""
            packet_type = "Unknown"
            is_long = (payload[0] & 0x80) != 0

            version_bytes = payload[1:5]
            version = f"0x{version_bytes.hex()}"

            dcid_len = payload[5]
            dcid = payload[6:6 + dcid_len].hex()

            scid_offset = 6 + dcid_len
            scid_len = payload[scid_offset]
            scid = payload[scid_offset + 1:scid_offset + 1 + scid_len].hex()

            packet_type = self._interpret_packet_type(payload[0])

            info = QUICInfo(
                version=version,
                dcid=dcid,
                scid=scid,
                is_long_header=is_long,
                packet_type=packet_type
            )
            return info.__dict__

        except (IndexError, AttributeError, TypeError) as e:
            return {
                "version": f"ParseError ({type(e).__name__})",
                "dcid": "ERROR",
                "scid": "ERROR",
                "is_long_header": False,
                "packet_type": "ERROR"
            }

    def _interpret_packet_type(self, first_byte: int) -> str:
        """
        Map QUIC type bits to a descriptive string.

        Args:
            first_byte (int): First byte of QUIC header.

        Return:
            str: Descriptive packet type.
        """
        type_bits = (first_byte & 0x30) >> 4
        return self.QUIC_TYPE.get(type_bits, "Unknown")

    def get_summary(self) -> dict:
        """
        Generate summary for QUIC communication.

        Return:
            dict: Summary with QUIC label.
        """
        return {
            "protocol": "QUIC",
            "src": None,
            "dst": None,
            "src_port": None,
            "dst_port": None,
            "summary": "Encrypted QUIC traffic"
        }
