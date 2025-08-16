"""
Defines the abstract base class for protocol analyzers in the packet analysis framework.
Each subclass must implement identification, summary, and detail extraction logic.

This module provides recursive protocol analysis with built-in protection against
infinite recursion and circular protocol references.
"""

from abc import ABC, abstractmethod

from scapy.all import Packet


class RecursionLimitError(Exception):
    """Raised when protocol analysis exceeds maximum recursion depth."""
    pass


class Protocol(ABC):
    """
    Abstract base class for protocol analyzers.
    
    Provides a framework for recursive protocol analysis with built-in
    protection against infinite recursion. Each protocol implementation
    must define how to identify itself, extract summary information,
    and provide detailed field parsing.

    Args:
        packet (Packet): The Scapy packet object being analyzed.
        
    Attributes:
        packet (Packet): The packet being analyzed.
        MAX_RECURSION_DEPTH (int): Maximum allowed recursion depth (default: 20).
    """

    MAX_RECURSION_DEPTH = 20

    def __init__(self, packet: Packet) -> None:
        """
        Initialize the protocol analyzer with a packet.
        
        Args:
            packet (Packet): The Scapy packet object to analyze.
            
        Raises:
            TypeError: If packet is not a Scapy Packet instance.
        """
        if not isinstance(packet, Packet):
            raise TypeError("packet must be a Scapy Packet instance")
        self.packet = packet

    @abstractmethod
    def identify(self) -> bool:
        """
        Check whether this protocol matches the current packet.
        
        This method should examine the packet structure and determine
        if this protocol analyzer is appropriate for the current layer.

        Returns:
            bool: True if protocol is present in packet, False otherwise.
            
        Note:
            This method should be lightweight and not raise exceptions
            under normal circumstances.
        """

    @abstractmethod
    def parse_layer_details(self) -> dict:
        """
        Extract detailed protocol-specific information from the current layer.
        
        This method should parse all relevant fields from the protocol
        header and return them in a structured dictionary format.

        Returns:
            dict: Dictionary of parsed fields and values. Keys should be
                 human-readable field names, values should be the parsed
                 field values (strings, integers, etc.).
                 
        Raises:
            ValueError: If the packet structure is invalid for this protocol.
            AttributeError: If required packet fields are missing.
        """

    @abstractmethod
    def get_summary(self) -> dict:
        """
        Generate a high-level summary of this protocol layer.
        
        This method should extract the most important information from
        the protocol for display in summary views. Common fields include
        protocol name, source/destination addresses, ports, etc.

        Returns:
            dict: Summary fields dictionary. Common keys include:
                - protocol (str): Protocol name
                - src (str): Source address
                - dst (str): Destination address  
                - src_port (int): Source port (if applicable)
                - dst_port (int): Destination port (if applicable)
                - summary (str): Human-readable summary string
                
        Note:
            Values may be None if not applicable to this protocol.
            The summary should prioritize the most relevant information.
        """

    def next_protocol(self):
        """
        Optionally return the next protocol analyzer for encapsulated data.
        
        This method should examine the current protocol layer and determine
        what protocol (if any) is encapsulated within it. It should return
        an appropriate Protocol subclass instance for further analysis.

        Returns:
            Protocol | None: Next protocol instance if applicable, else None.
            
        Note:
            This method should return None if:
            - No encapsulated protocol is present
            - The encapsulated protocol is not supported
            - An error occurs during next protocol detection
        """
        return None

    def descend_summary(self, inherited_summary: dict = None, depth: int = 0) -> dict:
        """
        Recursively descend through protocol layers to build complete summary.
        
        This method combines summary information from the current protocol
        layer with information from encapsulated protocols, creating a
        comprehensive packet summary.

        Args:
            inherited_summary (dict, optional): Summary data from parent protocols.
                Defaults to empty dict if not provided.
            depth (int, optional): Current recursion depth. Used internally
                for recursion limit enforcement. Defaults to 0.

        Returns:
            dict: Combined summary dictionary containing information from
                 all protocol layers in the packet.
                 
        Raises:
            RecursionLimitError: If recursion depth exceeds MAX_RECURSION_DEPTH.
            
        Note:
            Child protocol fields take precedence over parent protocol fields
            when there are naming conflicts.
        """
        # Recursion depth protection
        if depth >= self.MAX_RECURSION_DEPTH:
            raise RecursionLimitError(f"Protocol analysis exceeded maximum recursion depth of {self.MAX_RECURSION_DEPTH}")

        if inherited_summary is None:
            inherited_summary = {}

        try:
            current_summary = self.get_summary()
        except Exception as e:
            current_summary = {
                "protocol": f"ERROR_{self.__class__.__name__}",
                "summary": f"Summary extraction failed: {type(e).__name__}"
            }

        # Combine summaries, with current layer taking precedence for non-None values
        combined_summary = {
            **inherited_summary,
            **{k: v for k, v in current_summary.items() if v is not None}
        }

        # Continue to next protocol layer
        try:
            next_proto = self.next_protocol()
            if next_proto and next_proto.identify():
                return next_proto.descend_summary(
                    inherited_summary=combined_summary, 
                    depth=depth + 1
                )
        except Exception:
            # Continue with current summary if next protocol fails
            pass

        return combined_summary

    def descend_detail(self, depth: int = 0) -> dict:
        """
        Recursively descend through protocol layers to build detailed analysis.
        
        This method extracts detailed field information from each protocol
        layer and combines them into a comprehensive nested dictionary
        structure representing the complete packet analysis.

        Args:
            depth (int, optional): Current recursion depth. Used internally
                for recursion limit enforcement. Defaults to 0.

        Returns:
            dict: Dictionary with 'details' key containing nested protocol
                 analysis. Structure:
                 {
                     "details": {
                         "ProtocolName1": {...fields...},
                         "ProtocolName2": {...fields...},
                         ...
                     }
                 }
                 
        Raises:
            RecursionLimitError: If recursion depth exceeds MAX_RECURSION_DEPTH.
            
        Note:
            Protocol names are derived from class names with 'Protocol' suffix removed.
        """
        # Recursion depth protection
        if depth >= self.MAX_RECURSION_DEPTH:
            raise RecursionLimitError(f"Protocol analysis exceeded maximum recursion depth of {self.MAX_RECURSION_DEPTH}")

        details = {}

        # Parse current layer details
        try:
            current_details = self.parse_layer_details()
            if current_details:
                protocol_name = self.__class__.__name__.replace("Protocol", "")
                details[protocol_name] = current_details
        except Exception as e:
            protocol_name = self.__class__.__name__.replace("Protocol", "")
            details[protocol_name] = {
                "error": f"Detail parsing failed: {type(e).__name__}",
                "message": str(e)
            }

        # Continue to next protocol layer
        try:
            next_proto = self.next_protocol()
            if next_proto and next_proto.identify():
                result = next_proto.descend_detail(depth + 1)
                details.update(result["details"])
        except RecursionLimitError:
            # Re-raise recursion limit errors
            raise
        except Exception:
            # Continue with current details if next protocol fails
            pass

        return {
            "details": details
        }

    def descend(self, depth: int = 0) -> dict:
        """
        Perform complete packet analysis including both summary and details.
        
        This is a convenience method that combines both summary and detail
        analysis into a single result dictionary.

        Args:
            depth (int, optional): Current recursion depth. Used internally
                for recursion limit enforcement. Defaults to 0.

        Returns:
            dict: Complete analysis dictionary with both 'summary' and 'details' keys:
                 {
                     "summary": {...summary fields...},
                     "details": {
                         "ProtocolName1": {...fields...},
                         ...
                     }
                 }
                 
        Raises:
            RecursionLimitError: If recursion depth exceeds MAX_RECURSION_DEPTH.
        """
        try:
            summary = self.descend_summary(depth=depth)
            details_result = self.descend_detail(depth=depth)
            
            return {
                "summary": summary,
                "details": details_result["details"]
            }
        except RecursionLimitError:
            # Re-raise recursion limit errors
            raise
        except Exception as e:
            return {
                "summary": {
                    "protocol": "ERROR",
                    "summary": f"Analysis failed: {type(e).__name__}"
                },
                "details": {
                    "Error": {
                        "message": str(e),
                        "type": type(e).__name__
                    }
                }
            }

    def __repr__(self) -> str:
        """
        Return a string representation of the protocol analyzer.
        
        Returns:
            str: String representation showing class name and packet summary.
        """
        return f"{self.__class__.__name__}(packet={self.packet.summary()})"