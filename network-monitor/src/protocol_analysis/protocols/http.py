"""
Author: Petr Kalabis (kalabpe4)
File: src/protocol_analysis/protocols/http.py

Implements the HTTP protocol analyzer.
Supports parsing of HTTP requests and responses using Scapy's HTTP layers.
Extracts common metadata fields for higher-layer visibility.
"""

from dataclasses import dataclass

from scapy.layers.http import HTTPRequest, HTTPResponse
from scapy.packet import Raw

from src.protocol_analysis.protocols.protocol import Protocol


@dataclass
class HTTPInfo:
    """
    Structured data representation for HTTP messages.

    Attributes:
        method_or_status (str): HTTP method (e.g., GET) or status line (e.g., 200 OK).
        http_version (str): HTTP version string (e.g., 1.1).
        host (str): Host field from headers.
        path (str): Path from request line.
        user_agent (str): User-Agent header value.
        raw_http (str): Raw HTTP content as a decoded string.
    """
    method_or_status: str
    http_version: str
    host: str
    path: str
    user_agent: str
    raw_http: str


class HTTPProtocol(Protocol):
    """
    HTTP protocol analyzer.

    Identifies HTTP traffic and extracts request or response details,
    including common headers and raw content.
    """

    def identify(self) -> bool:
        """
        Check if the packet contains HTTP request or response.

        Return:
            bool: True if HTTP layer is detected.
        """
        return HTTPRequest in self.packet or HTTPResponse in self.packet

    def parse_layer_details(self) -> dict:
        """
        Parse and extract fields from HTTP request or response.

        Return:
            dict: Parsed HTTP metadata.
        """
        method_or_status = "Unknown"
        http_version = "Unknown"
        host = ""
        path = ""
        user_agent = ""
        raw_http = ""

        if HTTPRequest in self.packet:
            req = self.packet[HTTPRequest]
            method_or_status = req.Method.decode() if req.Method else "Unknown"
            path = req.Path.decode() if req.Path else ""
            host = req.Host.decode() if req.Host else ""
            user_agent = req.User_Agent.decode() if req.User_Agent else ""
            http_version = req.Http_Version.decode() if req.Http_Version else "Unknown"

        elif HTTPResponse in self.packet:
            res = self.packet[HTTPResponse]
            method_or_status = res.Status_Line.decode() if res.Status_Line else "HTTP Response"
            http_version = res.Http_Version.decode() if res.Http_Version else "Unknown"

        if Raw in self.packet:
            try:
                raw_bytes = self.packet[Raw].load
                raw_http = raw_bytes.decode("utf-8", errors="replace")
            except (AttributeError, UnicodeDecodeError, TypeError) as e:
                raw_http = f"[ParseError ({type(e).__name__})]"

        info = HTTPInfo(
            method_or_status=method_or_status,
            http_version=http_version,
            host=host,
            path=path,
            user_agent=user_agent,
            raw_http=raw_http
        )
        return info.__dict__

    def get_summary(self) -> dict:
        """
        Generate summary line for HTTP request or response.

        Return:
            dict: Summary of HTTP message.
        """
        summary = "HTTP traffic"
        if HTTPRequest in self.packet:
            req = self.packet[HTTPRequest]
            method = req.Method.decode() if req.Method else ""
            path = req.Path.decode() if req.Path else ""
            summary = f"{method} {path}"
        elif HTTPResponse in self.packet:
            res = self.packet[HTTPResponse]
            summary = res.Status_Line.decode() if res.Status_Line else "HTTP Response"

        return {
            "protocol": "HTTP",
            "src": None,
            "dst": None,
            "src_port": None,
            "dst_port": None,
            "summary": summary
        }
