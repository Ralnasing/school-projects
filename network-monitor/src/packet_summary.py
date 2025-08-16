"""
Provides data structures and extraction functions for packet summary and detail information.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Tuple, Any  # OPRAVENO: přidán Dict import
from scapy.packet import Packet

from src.protocol_analysis.analyze import analyze_packet


@dataclass
class PacketSummaryInfo:
    """Data structure representing high-level packet summary information."""
    packet_no: int
    timestamp: str
    protocol: str
    src: str
    dst: str
    length: int
    summary: str


@dataclass
class PacketDetailInfo:
    """Data structure containing detailed protocol-by-protocol packet analysis."""
    details: Dict[str, Dict[str, Any]]


def build_src_dst(summary: Dict[str, Any]) -> Tuple[str, str]:
    """Construct source and destination address strings from summary data."""
    src = summary.get("src", "")
    dst = summary.get("dst", "")
    
    # Append source port if available
    src_port = summary.get("src_port")
    if src_port:
        src += f":{src_port}"
        
    # Append destination port if available  
    dst_port = summary.get("dst_port")
    if dst_port:
        dst += f":{dst_port}"
        
    return src, dst


def extract_packet_summary(packet: Packet, packet_no: int) -> PacketSummaryInfo:
    """Extract high-level summary information from a Scapy packet."""
    if not isinstance(packet, Packet):
        raise TypeError("packet must be a Scapy Packet instance")
    if packet_no < 0:
        raise ValueError("packet_no cannot be negative")
    
    try:
        parsed = analyze_packet(packet, mode="summary")
        summary = parsed["summary"]
    except Exception as e:
        summary = {
            "protocol": "ERROR",
            "src": "",
            "dst": "",
            "src_port": "",
            "dst_port": "",
            "summary": f"Error parsing packet: {type(e).__name__}"
        }

    src, dst = build_src_dst(summary)
    
    return PacketSummaryInfo(
        packet_no=packet_no,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        protocol=summary.get("protocol", "UNKNOWN"),
        src=src,
        dst=dst,
        length=len(packet),
        summary=summary.get("summary", "")
    )


def extract_packet_details(packet: Packet) -> PacketDetailInfo:
    """Extract detailed field-level information from a Scapy packet."""
    if not isinstance(packet, Packet):
        raise TypeError("packet must be a Scapy Packet instance")
    
    try:
        parsed = analyze_packet(packet, mode="details")
        details = parsed["details"]
    except Exception:
        details = {}
        
    return PacketDetailInfo(details=details)


def create_empty_summary(packet_no: int, error_message: str = "Unknown error") -> PacketSummaryInfo:
    """Create an empty/error PacketSummaryInfo for failed packet processing."""
    return PacketSummaryInfo(
        packet_no=packet_no,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        protocol="ERROR",
        src="",
        dst="", 
        length=0,
        summary=error_message
    )


def create_empty_details(error_message: str = "Analysis failed") -> PacketDetailInfo:
    """Create an empty/error PacketDetailInfo for failed packet processing."""
    return PacketDetailInfo(details={
        "Error": {
            "message": error_message
        }
    })