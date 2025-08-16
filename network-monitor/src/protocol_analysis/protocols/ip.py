"""
Author: Petr Kalabis (kalabpe4)
File: src/protocol_analysis/protocols/ip.py

Implements the IP protocol analyzer for IPv4 packets.
Detects IP layer presence, extracts header details, and delegates further
analysis to TCP, UDP, or ICMP protocol analyzers.
"""

from dataclasses import dataclass
from ipaddress import ip_address

from scapy.layers.inet import IP

from src.protocol_analysis.protocols.protocol import Protocol
from src.protocol_analysis.protocols.tcp import TCPProtocol
from src.protocol_analysis.protocols.udp import UDPProtocol
from src.protocol_analysis.protocols.icmp import ICMPProtocol


@dataclass
class IPInfo:
    """
    Structured data representation of IPv4 packet fields.

    Attributes:
        version (str): IP version string.
        src_ip (str): Source IP address with scope.
        dst_ip (str): Destination IP address with scope.
        ttl (str): Time-To-Live value.
        df (str): Don't Fragment flag (Set/Not set).
        total_length (int): Total length of the IP packet.
        header_length (int): Length of the IP header in bytes.
        ip_options (str): Presence and size of IP options.
        id (int): IP packet ID.
        protocol (int): Next protocol number.
    """
    version: str
    src_ip: str
    dst_ip: str
    ttl: str
    df: str
    total_length: int
    header_length: int
    ip_options: str
    id: int
    protocol: int


class IPProtocol(Protocol):
    """
    IP protocol analyzer.

    Detects IPv4 packets and extracts core header fields, including option handling.
    Delegates analysis to TCP, UDP, or ICMP based on protocol number.
    """

    def identify(self) -> bool:
        """
        Check whether the packet contains an IP layer.

        Return:
            bool: True if IP layer is present.
        """
        return IP in self.packet

    def parse_layer_details(self) -> dict:
        """
        Extract IPv4 header fields into structured dictionary.

        Return:
            dict: Parsed IP layer fields.
        """
        try:
            ip = self.packet[IP]

            def annotate_scope(ip_str: str) -> str:
                try:
                    ip_obj = ip_address(ip_str)
                    scope = "Private" if ip_obj.is_private else "Public"
                    return f"{ip_str} ({scope})"
                except ValueError:
                    return f"{ip_str} (Invalid)"

            header_length_bytes = ip.ihl * 4
            ip_options = (
                f"Present ({header_length_bytes - 20} bytes)"
                if header_length_bytes > 20 else "None"
            )

            info = IPInfo(
                version=f"IPv{ip.version}",
                src_ip=annotate_scope(ip.src),
                dst_ip=annotate_scope(ip.dst),
                ttl=str(ip.ttl),
                df="Set" if ip.flags.DF else "Not set",
                total_length=ip.len,
                header_length=header_length_bytes,
                ip_options=ip_options,
                id=ip.id,
                protocol=ip.proto
            )
            return info.__dict__
        except (AttributeError, TypeError) as e:
            return {
                "version": f"ParseError ({type(e).__name__})",
                "src_ip": "ERROR",
                "dst_ip": "ERROR",
                "ttl": "ERROR",
                "df": "ERROR",
                "total_length": -1,
                "header_length": -1,
                "ip_options": "ERROR",
                "id": -1,
                "protocol": -1
            }

    def get_summary(self) -> dict:
        """
        Generate human-readable summary for IP packet.

        Return:
            dict: Summary with IP version, source and destination.
        """
        try:
            ip = self.packet[IP]
            return {
                "protocol": f"IPv{ip.version}",
                "src": ip.src,
                "dst": ip.dst,
                "src_port": "",
                "dst_port": "",
                "summary": f"IPv{ip.version} packet from {ip.src} to {ip.dst}"
            }
        except (AttributeError, TypeError):
            return {
                "protocol": "IPv4",
                "src": "ERROR",
                "dst": "ERROR",
                "src_port": "",
                "dst_port": "",
                "summary": "Malformed IP packet"
            }

    def next_protocol(self):
        """
        Determine and return next encapsulated protocol analyzer.

        Return:
            Protocol | None: TCP, UDP, ICMP analyzer instance or None.
        """
        next_protocols = [TCPProtocol, UDPProtocol, ICMPProtocol]
        for protocol_name in next_protocols:
            protocol = protocol_name(self.packet)
            if protocol.identify():
                return protocol
        return None
