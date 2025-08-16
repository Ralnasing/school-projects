"""
Author: Petr Kalabis (kalabpe4)
File: src/protocol_analysis/protocols/arp.py

Implements the ARP (Address Resolution Protocol) analyzer.
Identifies ARP packets, extracts key header information, and formats summary.
"""

from dataclasses import dataclass

from scapy.layers.l2 import ARP
from src.protocol_analysis.protocols.protocol import Protocol


@dataclass
class ARPInfo:
    """
    Structured data for ARP packet fields.

    Attributes:
        operation (str): Type of ARP operation (Request/Reply).
        sender_ip (str): IP address of the sender.
        sender_mac (str): MAC address of the sender.
        target_ip (str): IP address of the target.
        target_mac (str): MAC address of the target.
    """
    operation: str
    sender_ip: str
    sender_mac: str
    target_ip: str
    target_mac: str


class ARPProtocol(Protocol):
    """
    ARP protocol analyzer.

    Identifies ARP packets and extracts details such as sender and target information.
    """

    def identify(self) -> bool:
        """
        Check whether the packet contains an ARP layer.

        Return:
            bool: True if ARP is present.
        """
        return ARP in self.packet

    def parse_layer_details(self) -> dict:
        """
        Extract key ARP fields and convert to dictionary.

        Return:
            dict: Parsed ARP layer details.
        """
        try:
            arp = self.packet[ARP]

            op_map = {
                1: "ARP Request",
                2: "ARP Reply"
            }

            info = ARPInfo(
                operation=op_map.get(arp.op, f"Unknown ({arp.op})"),
                sender_ip=arp.psrc,
                sender_mac=arp.hwsrc,
                target_ip=arp.pdst,
                target_mac=arp.hwdst if arp.hwdst != "00:00:00:00:00:00" else "Unknown"
            )
            return info.__dict__
        except (AttributeError, TypeError) as e:
            return {
                "operation": f"ParseError ({type(e).__name__})",
                "sender_ip": "ERROR",
                "sender_mac": "ERROR",
                "target_ip": "ERROR",
                "target_mac": "ERROR"
            }

    def get_summary(self) -> dict:
        """
        Generate human-readable ARP summary.

        Return:
            dict: Summary including operation and addresses.
        """
        try:
            arp = self.packet[ARP]
            if arp.op == 1:
                summary = f"Who has {arp.pdst}? Tell {arp.psrc}"
            elif arp.op == 2:
                summary = f"{arp.psrc} is at {arp.hwsrc}"
            else:
                summary = f"ARP op {arp.op}"

            return {
                "protocol": "ARP",
                "src": arp.hwsrc,
                "dst": arp.hwdst,
                "src_port": "",
                "dst_port": "",
                "summary": summary
            }
        except (AttributeError, TypeError):
            return {
                "protocol": "ARP",
                "src": "ERROR",
                "dst": "ERROR",
                "src_port": "",
                "dst_port": "",
                "summary": "Malformed ARP packet"
            }
