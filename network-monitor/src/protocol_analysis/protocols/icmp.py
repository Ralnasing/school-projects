"""
Author: Petr Kalabis (kalabpe4)
File: src/protocol_analysis/protocols/icmp.py

Implements the ICMP protocol analyzer.
Recognizes ICMP packets, extracts message types and codes, and generates readable summaries.
"""

from dataclasses import dataclass
from scapy.layers.inet import ICMP
from src.protocol_analysis.protocols.protocol import Protocol


@dataclass
class ICMPInfo:
    """
    Structured data for ICMP fields.

    Attributes:
        type (int): ICMP message type.
        code (int): ICMP message code.
        description (str): Human-readable description.
        id (int): Identifier (if present).
        seq (int): Sequence number (if present).
    """
    type: int
    code: int
    description: str
    id: int
    seq: int


class ICMPProtocol(Protocol):
    """
    ICMP protocol analyzer.

    Identifies ICMP messages and provides parsed info and human-readable summaries.
    """

    ICMP_TYPES = {
        0: "Echo Reply",
        3: "Destination Unreachable",
        5: "Redirect",
        8: "Echo Request",
        11: "Time Exceeded",
        12: "Parameter Problem"
    }

    def identify(self) -> bool:
        """
        Check whether the packet contains an ICMP layer.

        Return:
            bool: True if ICMP is present.
        """
        return ICMP in self.packet

    def parse_layer_details(self) -> dict:
        """
        Parse ICMP layer fields into structured dictionary.

        Return:
            dict: Parsed ICMP layer information.
        """
        try:
            icmp = self.packet[ICMP]
            type_code = (icmp.type, icmp.code)
            description = self._describe_icmp(type_code)

            info = ICMPInfo(
                type=icmp.type,
                code=icmp.code,
                description=description,
                id=getattr(icmp, "id", -1),
                seq=getattr(icmp, "seq", -1)
            )
            return info.__dict__
        except (AttributeError, TypeError) as e:
            return {
                "type": -1,
                "code": -1,
                "description": f"ParseError ({type(e).__name__})",
                "id": -1,
                "seq": -1
            }

    def _describe_icmp(self, type_code: tuple[int, int]) -> str:
        """
        Return description based on ICMP type and code.

        Args:
            type_code (tuple[int, int]): ICMP type and code pair.

        Return:
            str: Human-readable description.
        """
        type_, code = type_code
        type_desc = self.ICMP_TYPES.get(type_, f"Type {type_}")
        return f"{type_desc} (code {code})"

    def get_summary(self) -> dict:
        """
        Generate summary description for ICMP message.

        Return:
            dict: Human-readable summary with description.
        """
        try:
            icmp = self.packet[ICMP]
            type_code = (icmp.type, icmp.code)
            description = self._describe_icmp(type_code)

            return {
                "protocol": "ICMP",
                "src": None,
                "dst": None,
                "src_port": "",
                "dst_port": "",
                "summary": f"ICMP {description}"
            }
        except (AttributeError, TypeError):
            return {
                "protocol": "ICMP",
                "src": "ERROR",
                "dst": "ERROR",
                "src_port": "",
                "dst_port": "",
                "summary": "Malformed ICMP packet"
            }
