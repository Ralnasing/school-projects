"""
Author: Petr Kalabis (kalabpe4)
File: src/protocol_analysis/protocols/dhcp.py

Implements the DHCP protocol analyzer.
Parses DHCP messages to extract message type, MAC, requested IP, and server identifier.
"""

from dataclasses import dataclass

from scapy.layers.dhcp import DHCP
from scapy.layers.inet import UDP

from src.protocol_analysis.protocols.protocol import Protocol


@dataclass
class DHCPInfo:
    """
    Structured data representation of DHCP packet fields.

    Attributes:
        message_type (str): Type of DHCP message (e.g., Discover, Offer).
        client_mac (str): MAC address of the client.
        requested_ip (str): IP address requested by the client.
        server_id (str): Server identifier IP address.
    """
    message_type: str
    client_mac: str
    requested_ip: str
    server_id: str


class DHCPProtocol(Protocol):
    """
    DHCP protocol analyzer.

    Detects DHCP messages over UDP and extracts key option fields.
    """

    def identify(self) -> bool:
        """
        Determine if the packet contains DHCP over UDP.

        Return:
            bool: True if DHCP packet on port 67.
        """
        return DHCP in self.packet and UDP in self.packet and (
            self.packet[UDP].sport == 67 or self.packet[UDP].dport == 67
        )

    def parse_layer_details(self) -> dict:
        """
        Parse relevant DHCP options and client info.

        Return:
            dict: Parsed DHCP details.
        """
        try:
            dhcp = self.packet[DHCP]
            options = dhcp.options

            msg_type = "Unknown"
            requested_ip = ""
            server_id = ""

            for opt in options:
                if isinstance(opt, tuple):
                    if opt[0] == "message-type":
                        msg_type = self._interpret_dhcp_type(opt[1])
                    elif opt[0] == "requested_addr":
                        requested_ip = opt[1]
                    elif opt[0] == "server_id":
                        server_id = opt[1]

            client_mac = self.packet.src if hasattr(self.packet, "src") else "Unknown"

            info = DHCPInfo(
                message_type=msg_type,
                client_mac=client_mac,
                requested_ip=requested_ip,
                server_id=server_id
            )
            return info.__dict__
        except (AttributeError, TypeError) as e:
            return {
                "message_type": f"ParseError ({type(e).__name__})",
                "client_mac": "ERROR",
                "requested_ip": "",
                "server_id": ""
            }

    def _interpret_dhcp_type(self, value: int) -> str:
        """
        Map numeric DHCP message types to readable names.

        Args:
            value (int): Message type ID.

        Return:
            str: Human-readable DHCP message type.
        """
        types = {
            1: "Discover",
            2: "Offer",
            3: "Request",
            4: "Decline",
            5: "ACK",
            6: "NAK",
            7: "Release",
            8: "Inform"
        }
        return f"DHCP {types.get(value, f'Unknown ({value})')}"

    def get_summary(self) -> dict:
        """
        Generate a summary string from DHCP message type.

        Return:
            dict: Summary dictionary with ports and type.
        """
        try:
            msg_type = "DHCP"
            dhcp = self.packet[DHCP]
            for opt in dhcp.options:
                if isinstance(opt, tuple) and opt[0] == "message-type":
                    msg_type = self._interpret_dhcp_type(opt[1])
                    break

            return {
                "protocol": "DHCP",
                "src": None,
                "dst": None,
                "src_port": str(self.packet[UDP].sport),
                "dst_port": str(self.packet[UDP].dport),
                "summary": msg_type
            }
        except (AttributeError, TypeError):
            return {
                "protocol": "DHCP",
                "src": "ERROR",
                "dst": "ERROR",
                "src_port": "",
                "dst_port": "",
                "summary": "Malformed DHCP packet"
            }
