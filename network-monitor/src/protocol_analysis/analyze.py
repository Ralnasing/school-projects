"""
Provides top-level packet analysis entry point for protocol dissection.
This module starts with Ethernet protocol and descends through protocol layers
with built-in protection against infinite recursion and comprehensive error handling.

The analysis system supports three modes:
- 'summary': Quick overview of packet contents
- 'details': Complete field-by-field analysis  
- 'full': Both summary and details combined
"""

from scapy.packet import Packet

from src.protocol_analysis.protocols.eth import EthernetProtocol
from src.protocol_analysis.protocols.protocol import RecursionLimitError


def analyze_packet(packet: Packet, mode: str = "full") -> dict:
    """
    Analyzes the provided packet, starting from Ethernet layer.
    
    This function serves as the main entry point for packet analysis.
    It creates an Ethernet protocol analyzer and recursively descends
    through all protocol layers present in the packet.

    Args:
        packet (Packet): Scapy Packet object to analyze. Must be a valid
            network packet with at least an Ethernet header.
        mode (str, optional): Analysis mode controlling output detail level.
            Valid values:
            - 'summary': Returns only high-level packet summary
            - 'details': Returns only detailed field analysis
            - 'full': Returns both summary and details (default)

    Returns:
        dict: Analysis results dictionary. Structure depends on mode:
        
        For mode='summary':
        {
            'summary': {
                'protocol': str,    # Top-level protocol name
                'src': str,         # Source address
                'dst': str,         # Destination address  
                'src_port': int,    # Source port (if applicable)
                'dst_port': int,    # Destination port (if applicable)
                'summary': str,     # Human-readable summary
                ...                 # Additional protocol-specific fields
            }
        }
        
        For mode='details':
        {
            'details': {
                'Ethernet': {...},      # Ethernet layer fields
                'IP': {...},           # IP layer fields (if present)
                'TCP': {...},          # TCP layer fields (if present)  
                ...                    # Additional protocol layers
            }
        }
        
        For mode='full':
        {
            'summary': {...},    # As above
            'details': {...}     # As above
        }
        
    Raises:
        ValueError: If packet cannot be analyzed or mode is invalid.
        TypeError: If packet is not a Scapy Packet instance.
        
    Example:
        >>> from scapy.all import *
        >>> pkt = Ether()/IP(dst="8.8.8.8")/TCP(dport=80)
        >>> result = analyze_packet(pkt, mode="summary")
        >>> print(result['summary']['protocol'])
        'TCP'
        
    Note:
        - Analysis starts with Ethernet protocol and may not work correctly
          for packets that don't have Ethernet headers
        - Unknown protocols will be marked as 'ERROR' in the results
        - Recursion is limited to prevent infinite loops in malformed packets
    """
    # Input validation
    if not isinstance(packet, Packet):
        raise TypeError("packet must be a Scapy Packet instance")
    
    if mode not in {'summary', 'details', 'full'}:
        raise ValueError(f"Invalid mode '{mode}'. Must be one of: 'summary', 'details', 'full'")
    
    try:
        # Initialize Ethernet protocol analyzer
        eth = EthernetProtocol(packet)
        
        # Check if packet has recognizable Ethernet header
        if not eth.identify():
            raise ValueError("Packet does not contain valid Ethernet header")

        # Perform analysis based on requested mode
        if mode == "summary":
            result = {
                "summary": eth.descend_summary()
            }
            
        elif mode == "details":
            details_result = eth.descend_detail()
            result = {
                "details": details_result["details"]
            }
            
        else:  # mode == "full"
            result = eth.descend()
        
        return result

    except RecursionLimitError as e:
        error_msg = f"Analysis failed due to recursion limit: {str(e)}"
        return _create_error_result(error_msg, "RECURSION_LIMIT", mode)
        
    except (AttributeError, ValueError, TypeError) as e:
        error_msg = f"Analysis error: {type(e).__name__}: {str(e)}"
        return _create_error_result(error_msg, "ANALYSIS_ERROR", mode)
        
    except Exception as e:
        error_msg = f"Unexpected error during analysis: {type(e).__name__}: {str(e)}"
        return _create_error_result(error_msg, "UNEXPECTED_ERROR", mode)


def _create_error_result(error_message: str, error_type: str, mode: str) -> dict:
    """
    Create a standardized error result dictionary.
    
    This internal function generates consistent error responses when
    packet analysis fails, ensuring that calling code receives a
    predictable data structure even in error conditions.
    
    Args:
        error_message (str): Human-readable error description
        error_type (str): Error category for programmatic handling
        mode (str): Original analysis mode requested
        
    Returns:
        dict: Error result dictionary matching the requested mode structure
    """
    error_summary = {
        "protocol": error_type,
        "src": "",
        "dst": "", 
        "src_port": None,
        "dst_port": None,
        "summary": error_message
    }
    
    error_details = {
        "Error": {
            "type": error_type,
            "message": error_message,
            "analysis_mode": mode
        }
    }
    
    if mode == "summary":
        return {"summary": error_summary}
    elif mode == "details":
        return {"details": error_details}
    else:  # mode == "full"
        return {
            "summary": error_summary,
            "details": error_details
        }


def validate_packet_structure(packet: Packet) -> bool:
    """
    Perform basic validation of packet structure before analysis.
    
    This function performs lightweight checks to ensure the packet
    has the minimum required structure for successful analysis.
    
    Args:
        packet (Packet): Packet to validate
        
    Returns:
        bool: True if packet appears valid for analysis
        
    Note:
        This is a basic check and doesn't guarantee successful analysis,
        but can catch obviously malformed packets early.
    """
    try:
        # Basic checks
        if not packet:
            return False
            
        # Check if packet has layers
        if not hasattr(packet, 'layers') or not packet.layers():
            return False
            
        # Check if packet has minimal length
        if len(packet) < 14:  # Minimum Ethernet frame size
            return False
            
        return True
        
    except Exception:
        return False