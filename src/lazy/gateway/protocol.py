"""WebSocket protocol framing and HUD message contracts (RFC 6455)."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import struct
from typing import Any, Dict, Optional, Tuple

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def compute_ws_accept(sec_websocket_key: str) -> str:
    """Compute Sec-WebSocket-Accept header per RFC 6455."""
    sha1 = hashlib.sha1((sec_websocket_key.strip() + WS_GUID).encode("utf-8")).digest()
    return base64.b64encode(sha1).decode("utf-8")


def encode_ws_frame(message: str | bytes, is_text: bool = True) -> bytes:
    """Encode a payload into an unmasked server-to-client RFC 6455 WebSocket frame."""
    payload = message.encode("utf-8") if isinstance(message, str) else message
    length = len(payload)
    opcode = 0x1 if is_text else 0x2
    first_byte = 0x80 | opcode  # FIN bit set

    if length <= 125:
        header = bytes([first_byte, length])
    elif length <= 65535:
        header = bytes([first_byte, 126]) + struct.pack("!H", length)
    else:
        header = bytes([first_byte, 127]) + struct.pack("!Q", length)

    return header + payload


def decode_ws_frame(data: bytes) -> Tuple[Optional[str], bytes, int]:
    """Decode a client-to-server masked RFC 6455 WebSocket frame.

    Returns (decoded_text, remaining_buffer, opcode).
    """
    if len(data) < 2:
        return None, data, 0

    first_byte = data[0]
    opcode = first_byte & 0x0F
    second_byte = data[1]
    is_masked = bool(second_byte & 0x80)
    payload_len = second_byte & 0x7F

    offset = 2
    if payload_len == 126:
        if len(data) < 4:
            return None, data, opcode
        payload_len = struct.unpack("!H", data[2:4])[0]
        offset = 4
    elif payload_len == 127:
        if len(data) < 10:
            return None, data, opcode
        payload_len = struct.unpack("!Q", data[2:10])[0]
        offset = 10

    mask_key = None
    if is_masked:
        if len(data) < offset + 4:
            return None, data, opcode
        mask_key = data[offset:offset + 4]
        offset += 4

    if len(data) < offset + payload_len:
        return None, data, opcode

    raw_payload = bytearray(data[offset:offset + payload_len])
    remaining = data[offset + payload_len:]

    if is_masked and mask_key:
        for i in range(len(raw_payload)):
            raw_payload[i] ^= mask_key[i % 4]

    text = raw_payload.decode("utf-8", errors="replace")
    return text, remaining, opcode


class GatewayProtocolMessage:
    """Encapsulates a typed Lazy OS HUD/Gateway message."""

    def __init__(self, msg_type: str, payload: Optional[Dict[str, Any]] = None):
        self.type = msg_type
        self.payload = payload or {}

    def to_json(self) -> str:
        data = {"type": self.type, **self.payload}
        return json.dumps(data)

    @classmethod
    def from_json(cls, raw: str) -> GatewayProtocolMessage:
        parsed = json.loads(raw)
        if not isinstance(parsed, dict) or "type" not in parsed:
            raise ValueError("Protocol message must be a JSON object with 'type'")
        msg_type = parsed["type"]
        payload = {k: v for k, v in parsed.items() if k != "type"}
        return cls(msg_type, payload)
