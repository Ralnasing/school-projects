"""
Author: Petr Kalabis (kalabpe4)
File: src/protocol_analysis/protocols/tls.py

Implements the TLS protocol analyzer.
Identifies TLS packets, extracts versions, cipher suite, and message type.
Maps raw values to human-readable formats using a cipher suite lookup table.
"""

from dataclasses import dataclass

from scapy.layers.tls.all import TLS, TLSClientHello, TLSServerHello, TLSChangeCipherSpec
from src.protocol_analysis.protocols.protocol import Protocol
from src.protocol_analysis.lookup_loader import load_tls_cipher_lookup


@dataclass
class TLSInfo:
    """
    Structured data for TLS communication.

    Attributes:
        tls_version (str): TLS version name (e.g. TLSv1.2).
        message_type (str): Type of TLS message.
        cipher_suite (str): Selected or offered cipher suite.
        recommended (str): Security recommendation.
    """
    tls_version: str
    message_type: str
    cipher_suite: str
    recommended: str


class TLSProtocol(Protocol):
    """
    TLS protocol analyzer.

    Interprets TLS handshake and control messages using Scapy TLS layers.
    Matches cipher suite codes to descriptions via lookup table.
    """

    CIPHER_LOOKUP = load_tls_cipher_lookup("data/tls-parameters-4.csv")

    TLS_VERSION_MAP = {
        0x0300: "TLSv1.0 (SSL 3.0)",
        0x0301: "TLSv1.0",
        0x0302: "TLSv1.1",
        0x0303: "TLSv1.2",
        0x0304: "TLSv1.3"
    }

    TLS_MESG_MAP = {
        20: "ChangeCipherSpec",
        21: "Alert",
        22: "Handshake",
        23: "ApplicationData"
    }

    def identify(self) -> bool:
        """
        Check if the packet contains TLS.

        Return:
            bool: True if TLS is detected.
        """
        return TLS in self.packet

    def get_tls_layer_and_type(self):
        """
        Try to extract the relevant TLS layer and its type.

        Return:
            tuple: (TLS layer object, message type string)
        """
        if TLSClientHello in self.packet:
            return self.packet[TLSClientHello], "ClientHello"
        if TLSServerHello in self.packet:
            return self.packet[TLSServerHello], "ServerHello"
        if TLSChangeCipherSpec in self.packet:
            return self.packet[TLSChangeCipherSpec], "ChangeCipherSpec"

        if TLS in self.packet:
            tls_layer = self.packet[TLS]

            if hasattr(tls_layer, "msgtype") and tls_layer.msgtype:
                msg_code = tls_layer.msgtype[0] if isinstance(tls_layer.msgtype, list) else tls_layer.msgtype
                msg_type = self.TLS_MESG_MAP.get(msg_code, f"Unknown ({msg_code})")
                return tls_layer, msg_type

            if hasattr(tls_layer, 'type'):
                msg_code = tls_layer.type
                msg_type = self.TLS_MESG_MAP.get(msg_code, f"Unknown ({msg_code})")
                return tls_layer, msg_type

            return tls_layer, "TLS"

        return None, "Unknown"

    def interpret_cipher_suite(self, tls_layer):
        """
        Resolve cipher suite ID to name and security recommendation.

        Args:
            tls_layer: Scapy TLS layer.

        Return:
            tuple[str, str, str]: Cipher suite name, hex code, recommendation.
        """
        cipher_hex = None
        cipher_name = "Unknown"
        recommended = "Unknown"

        if hasattr(tls_layer, 'cipher') and tls_layer.cipher:
            try:
                cipher_hex = f"0x{tls_layer.cipher:04X}"
            except (ValueError, TypeError) as e:
                cipher_name = f"ParseError ({type(e).__name__})"
                return cipher_name, None, "Unknown"

        elif hasattr(tls_layer, 'ciphers') and tls_layer.ciphers:
            try:
                first_cipher = tls_layer.ciphers[0]
                cipher_hex = f"0x{first_cipher:04X}"
                cipher_name = f"Offered ciphers (showing first: {cipher_hex})"
            except (ValueError, TypeError, IndexError) as e:
                cipher_name = f"ParseError ({type(e).__name__})"
                return cipher_name, None, "Unknown"

        if cipher_hex and cipher_hex in self.CIPHER_LOOKUP:
            entry = self.CIPHER_LOOKUP[cipher_hex]
            base_name = entry["description"]
            recommended = entry["recommended"]

            if hasattr(tls_layer, 'ciphers') and not hasattr(tls_layer, 'cipher'):
                cipher_name = f"Offered: {base_name}"
            else:
                cipher_name = base_name
        elif not cipher_hex:
            cipher_name = "Unknown"

        return cipher_name, cipher_hex, recommended

    def parse_layer_details(self) -> dict:
        """
        Extract TLS details: version, cipher suite, and message type.

        Return:
            dict: Parsed TLSInfo dictionary.
        """
        tls_layer, msg_type = self.get_tls_layer_and_type()
        if not tls_layer:
            return {}

        version = getattr(tls_layer, 'version', None)
        tls_version_str = self.TLS_VERSION_MAP.get(version, f"Unknown (0x{version:04X})" if version else "Unknown")

        cipher_name, cipher_hex, recommended = self.interpret_cipher_suite(tls_layer)

        info = TLSInfo(
            tls_version=tls_version_str,
            message_type=msg_type,
            cipher_suite=f"{cipher_name} ({cipher_hex})" if cipher_hex else cipher_name,
            recommended=recommended
        )
        return info.__dict__

    def get_summary(self) -> dict:
        """
        Generate short summary for TLS communication.

        Return:
            dict: Basic description with version and message type.
        """
        tls_layer, msg_type = self.get_tls_layer_and_type()
        version = getattr(tls_layer, 'version', None)
        protocol_name = self.TLS_VERSION_MAP.get(version, "TLS").replace(" ", "")

        return {
            "protocol": protocol_name,
            "src": None,
            "dst": None,
            "src_port": None,
            "dst_port": None,
            "summary": f"TLS {msg_type}" if msg_type else "TLS encrypted communication"
        }
