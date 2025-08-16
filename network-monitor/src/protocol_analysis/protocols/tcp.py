"""
Author: Petr Kalabis (kalabpe4)
File: src/protocol_analysis/protocols/tcp.py

Implements the TCP protocol analyzer.
Extracts TCP header fields, interprets flags, and optionally delegates to higher-layer protocols.
"""

from dataclasses import dataclass
from scapy.layers.inet import TCP

from src.protocol_analysis.protocols.protocol import Protocol
from src.protocol_analysis.protocols.http import HTTPProtocol
from src.protocol_analysis.protocols.tls import TLSProtocol


@dataclass
class TCPInfo:
    """
    Structured data representation of TCP packet fields.

    Attributes:
        src_port (int): Source TCP port.
        dst_port (int): Destination TCP port.
        seq (int): Sequence number.
        ack (int): Acknowledgement number.
        flags (str): TCP flags with interpretation.
        window (int): TCP window size.
        header_length (int): TCP header length in bytes.
        options (str): TCP options presence/length.
    """
    src_port: int
    dst_port: int
    seq: int
    ack: int
    flags: str
    window: int
    header_length: int
    options: str


class TCPProtocol(Protocol):
    """
    TCP protocol analyzer.

    Parses TCP packet details and delegates to application-layer protocols like TLS and HTTP.
    """

    TCP_FLAG_MEANINGS = {
        "S": "Connection initiation (SYN)",
        "SA": "Connection acknowledged (SYN-ACK)",
        "A": "Acknowledgement",
        "PA": "Data transfer (PSH-ACK)",
        "FA": "Connection termination (FIN-ACK)",
        "F": "Connection close (FIN)",
        "R": "Connection reset (RST)",
        "RA": "Reset with acknowledgement",
    }

    TCP_FLAG_SETS = {
        frozenset({"F", "P", "A"}): "End of data with push (F-P-ACK)",
        frozenset({"F", "U", "P"}): "Xmas scan signature (FPU)"
    }

    def identify(self) -> bool:
        """
        Check whether the packet contains a TCP layer.

        Return:
            bool: True if TCP is present.
        """
        return TCP in self.packet

    def interpret_flags(self, flags: str) -> str:
        """
        Interpret the TCP flags into a human-readable meaning.

        Args:
            flags (str): Flag characters extracted from TCP.

        Return:
            str: Description of the flags.
        """
        if flags in self.TCP_FLAG_MEANINGS:
            return self.TCP_FLAG_MEANINGS[flags]

        flag_set = frozenset(flags)
        if flag_set in self.TCP_FLAG_SETS:
            return self.TCP_FLAG_SETS[flag_set]

        return f"Flags: {flags}"

    def parse_layer_details(self) -> dict:
        """
        Parse the TCP layer and return relevant field information.

        Return:
            dict: TCP header fields and flag interpretation.
        """
        try:
            tcp = self.packet[TCP]

            hdr_len = tcp.dataofs * 4
            options_len = hdr_len - 20
            options_str = f"Present ({options_len} bytes)" if options_len > 0 else "None"

            flags = str(tcp.sprintf("%TCP.flags%"))
            meaning = self.interpret_flags(flags)
            combined_flag = f"{flags} ({meaning})"

            info = TCPInfo(
                src_port=tcp.sport,
                dst_port=tcp.dport,
                seq=tcp.seq,
                ack=tcp.ack,
                flags=combined_flag,
                window=tcp.window,
                header_length=hdr_len,
                options=options_str
            )
            return info.__dict__
        except (AttributeError, TypeError) as e:
            return {
                "src_port": -1,
                "dst_port": -1,
                "seq": -1,
                "ack": -1,
                "flags": f"ParseError ({type(e).__name__})",
                "window": -1,
                "header_length": -1,
                "options": "ERROR"
            }

    def get_summary(self) -> dict:
        """
        Generate a high-level summary of TCP traffic.

        Return:
            dict: Summary including ports and flag meanings.
        """
        try:
            tcp = self.packet[TCP]
            flags = str(tcp.sprintf("%TCP.flags%"))
            meaning = self.interpret_flags(flags)

            return {
                "protocol": "TCP",
                "src": None,
                "dst": None,
                "src_port": str(tcp.sport),
                "dst_port": str(tcp.dport),
                "summary": f"{meaning} from port {tcp.sport} to {tcp.dport}"
            }
        except (AttributeError, TypeError):
            return {
                "protocol": "TCP",
                "src": "ERROR",
                "dst": "ERROR",
                "src_port": "",
                "dst_port": "",
                "summary": "Malformed TCP packet"
            }

    def next_protocol(self):
        """
        Try to identify higher-layer protocols like TLS or HTTP.

        Return:
            Protocol | None: Instance of next protocol handler or None.
        """
        next_protocols = [TLSProtocol, HTTPProtocol]
        for protocol_name in next_protocols:
            protocol = protocol_name(self.packet)
            if protocol.identify():
                return protocol
        return None
