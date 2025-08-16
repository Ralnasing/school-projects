"""
Author: Petr Kalabis (kalabpe4)
File: src/protocol_analysis/protocols/udp.py

Implements the UDP protocol analyzer.
Extracts source and destination ports, length, and checksum from UDP headers.
Delegates to protocols such as DNS and QUIC when applicable.
"""

from dataclasses import dataclass

from scapy.layers.inet import UDP

from src.protocol_analysis.protocols.protocol import Protocol
from src.protocol_analysis.protocols.dns import DNSProtocol
from src.protocol_analysis.protocols.quic import QUICProtocol
from src.protocol_analysis.protocols.dhcp import DHCPProtocol


@dataclass
class UDPInfo:
    """
    Structured data representation of UDP packet fields.

    Attributes:
        src_port (int): Source UDP port.
        dst_port (int): Destination UDP port.
        length (int): Total length of the UDP segment.
        checksum (str): Hexadecimal string of UDP checksum, or "None".
    """
    src_port: int
    dst_port: int
    length: int
    checksum: str


class UDPProtocol(Protocol):
    """
    UDP protocol analyzer.

    Identifies UDP packets, extracts metadata, and optionally delegates
    to application-layer protocols like DNS and QUIC.
    """

    def identify(self) -> bool:
        """
        Check whether the packet contains a UDP layer.

        Return:
            bool: True if UDP is present.
        """
        return UDP in self.packet

    def parse_layer_details(self) -> dict:
        """
        Extract UDP header fields including ports, length, and checksum.

        Return:
            dict: Parsed UDP fields.
        """
        try:
            udp = self.packet[UDP]
            info = UDPInfo(
                src_port=udp.sport,
                dst_port=udp.dport,
                length=udp.len,
                checksum=hex(udp.chksum) if udp.chksum else "None"
            )
            return info.__dict__
        except (AttributeError, TypeError) as e:
            return {
                "src_port": -1,
                "dst_port": -1,
                "length": -1,
                "checksum": f"ParseError ({type(e).__name__})"
            }

    def get_summary(self) -> dict:
        """
        Generate human-readable summary of UDP communication.

        Return:
            dict: Summary with source and destination ports.
        """
        try:
            udp = self.packet[UDP]
            return {
                "protocol": "UDP",
                "src": None,
                "dst": None,
                "src_port": str(udp.sport),
                "dst_port": str(udp.dport),
                "summary": f"UDP from port {udp.sport} to {udp.dport}"
            }
        except (AttributeError, TypeError):
            return {
                "protocol": "UDP",
                "src": "ERROR",
                "dst": "ERROR",
                "src_port": "",
                "dst_port": "",
                "summary": "Malformed UDP packet"
            }

    def next_protocol(self):
        """
        Attempt to identify and delegate to encapsulated higher-layer protocols.

        Return:
            Protocol | None: Instance of next protocol analyzer or None.
        """
        next_protocols = [DNSProtocol, QUICProtocol, DHCPProtocol]
        for proto in next_protocols:
            instance = proto(self.packet)
            if instance.identify():
                return instance
        return None
