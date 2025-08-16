"""
JSON serialization and deserialization utilities for packet data.

Provides functions to save and load packet summary and detail information
to/from JSON format for persistent storage and data exchange.
"""

import json
from typing import List, Tuple
from src.packet_summary import PacketSummaryInfo, PacketDetailInfo


def save_packets_to_json(file_path: str, packets: List[Tuple[PacketSummaryInfo, PacketDetailInfo]]) -> None:
    """
    Save packet summary and detail information to a JSON file.
    
    Args:
        file_path (str): Path where the JSON file should be created.
        packets (List[Tuple[PacketSummaryInfo, PacketDetailInfo]]): 
            List of packet information tuples to serialize.
            
    Raises:
        IOError: If the file cannot be written to the specified path.
        TypeError: If packets contain invalid data types.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([
            {"summary": summary.__dict__, "detail": detail.details}
            for summary, detail in packets
        ], f, indent=2)


def load_packets_from_json(file_path: str) -> List[Tuple[PacketSummaryInfo, PacketDetailInfo]]:
    """
    Load packet summary and detail information from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file to load.
            
    Returns:
        List[Tuple[PacketSummaryInfo, PacketDetailInfo]]: 
            List of reconstructed packet information tuples.
            
    Raises:
        IOError: If the file cannot be read from the specified path.
        ValueError: If the JSON format is invalid or data is corrupted.
        FileNotFoundError: If the specified file does not exist.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

        if not isinstance(raw, list):
            raise ValueError("Invalid JSON format: Expected a list.")

        validated = []
        for entry in raw:
            if not isinstance(entry, dict) or "summary" not in entry or "detail" not in entry:
                raise ValueError("Invalid JSON format: Missing 'summary' or 'detail' keys.")

            summary_data = entry["summary"]
            detail_data = entry["detail"]

            required_keys = {"packet_no", "timestamp", "protocol", "src", "dst", "length", "summary"}
            if not isinstance(summary_data, dict) or not required_keys.issubset(summary_data):
                raise ValueError("Invalid packet summary structure.")

            # OPRAVENO: detail_data už obsahuje přímo dictionary pro details field
            if not isinstance(detail_data, dict):
                raise ValueError("Invalid packet detail structure.")

            validated.append((
                PacketSummaryInfo(**summary_data),
                PacketDetailInfo(details=detail_data)  # OPRAVENO: detail_data jde přímo jako details
            ))

        return validated