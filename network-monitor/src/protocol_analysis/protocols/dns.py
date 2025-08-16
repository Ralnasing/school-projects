"""
Author: Petr Kalabis (kalabpe4)
File: src/protocol_analysis/protocols/dns.py

Implements the DNS protocol analyzer.
Parses DNS queries and responses, and generates human-readable summaries.
"""

from dataclasses import dataclass

from scapy.layers.dns import DNS, DNSQR
from src.protocol_analysis.protocols.protocol import Protocol


@dataclass
class DNSInfo:
    """
    Structured data representation of DNS packet fields.

    Attributes:
        query_name (str): Queried domain name.
        query_type (str): DNS query type (e.g., A, AAAA).
        is_response (bool): Whether the DNS message is a response.
        response_count (int): Number of answers in the response.
    """
    query_name: str
    query_type: str
    is_response: bool
    response_count: int


class DNSProtocol(Protocol):
    """
    DNS protocol analyzer.

    Identifies DNS messages, extracts query and response data,
    and provides readable summaries.
    """

    TYPE_MAP = {
        1: "A",
        2: "NS",
        5: "CNAME",
        6: "SOA",
        12: "PTR",
        15: "MX",
        16: "TXT",
        28: "AAAA",
    }

    def identify(self) -> bool:
        """
        Check whether the packet contains a DNS layer.

        Return:
            bool: True if DNS is present.
        """
        return DNS in self.packet

    def parse_layer_details(self) -> dict:
        """
        Extract DNS query or response fields.

        Return:
            dict: Parsed DNS fields.
        """
        try:
            dns = self.packet[DNS]

            is_response = dns.qr == 1
            query_name = ""
            query_type = ""
            response_count = dns.ancount if is_response else 0

            if DNSQR in dns and dns.qd:
                query_name = dns.qd.qname.decode(errors="ignore") \
                    if isinstance(dns.qd.qname, bytes) else str(dns.qd.qname)
                query_type = dns.qd.qtype

            query_type_str = self.TYPE_MAP.get(query_type, str(query_type))

            info = DNSInfo(
                query_name=query_name,
                query_type=query_type_str,
                is_response=is_response,
                response_count=response_count
            )
            return info.__dict__
        except (AttributeError, TypeError) as e:
            return {
                "query_name": "ERROR",
                "query_type": f"ParseError ({type(e).__name__})",
                "is_response": False,
                "response_count": 0
            }

    def get_summary(self) -> dict:
        """
        Generate summary of DNS query or response.

        Return:
            dict: Human-readable DNS summary.
        """
        try:
            dns = self.packet[DNS]
            summary = "DNS"

            if dns.qr == 0 and DNSQR in dns and dns.qd:
                qname = dns.qd.qname.decode(errors="ignore") \
                    if isinstance(dns.qd.qname, bytes) else str(dns.qd.qname)
                summary = f"DNS Query for {qname}"

            elif dns.qr == 1 and dns.ancount > 0:
                summary = f"DNS Response ({dns.ancount} answer{'s' if dns.ancount != 1 else ''})"

            return {
                "protocol": "DNS",
                "src": None,
                "dst": None,
                "src_port": None,
                "dst_port": None,
                "summary": summary
            }
        except (AttributeError, TypeError):
            return {
                "protocol": "DNS",
                "src": "ERROR",
                "dst": "ERROR",
                "src_port": "",
                "dst_port": "",
                "summary": "Malformed DNS packet"
            }

    def next_protocol(self):
        """
        DNS is typically a top-level protocol with no next layer.

        Return:
            None
        """
        return None
