"""
Pasarela de Telecomunicaciones SMPP v3.4 Carrier-Grade para el SMSC de Movilnet.
Gobernanza: Universal Best Practices Engineering Rule (Pilares I, II y III).
Implementa codificación/decodificación binaria de PDUs SMPP v3.4 en Python puro.
"""
import struct
import socket
import logging
from typing import Dict, Any, Tuple, Optional

try:
    from outwhatsapp.domain.enums import SMPPCommandId
    from outwhatsapp.domain.models import SMPPMessage
    from outwhatsapp.domain.invariants import SovereignInvariants
except ImportError:
    from outwhatsapp.domain.enums import SMPPCommandId
    from outwhatsapp.domain.models import SMPPMessage
    from outwhatsapp.domain.invariants import SovereignInvariants

logger = logging.getLogger("outwhatsapp.smpp")


class SMPPPduCodec:
    """Codificador y decodificador binario de PDUs SMPP v3.4 estándar."""

    HEADER_FORMAT = ">IIII"  # length (4B), command_id (4B), command_status (4B), sequence_number (4B)
    HEADER_SIZE = 16

    @classmethod
    def encode_header(cls, command_id: int, command_status: int, sequence_number: int, body_length: int) -> bytes:
        total_length = cls.HEADER_SIZE + body_length
        return struct.pack(cls.HEADER_FORMAT, total_length, command_id, command_status, sequence_number)

    @classmethod
    def decode_header(cls, header_bytes: bytes) -> Tuple[int, int, int, int]:
        if len(header_bytes) < cls.HEADER_SIZE:
            raise ValueError(f"Cabecera SMPP truncada: se recibieron {len(header_bytes)} bytes (mínimo 16)")
        return struct.unpack(cls.HEADER_FORMAT, header_bytes[:cls.HEADER_SIZE])

    @classmethod
    def encode_submit_sm(cls, message: SMPPMessage) -> bytes:
        """
        Codifica una PDU SUBMIT_SM para entregar al SMSC de Movilnet.
        """
        SovereignInvariants.validar_longitud_sms_smpp(message.short_message)

        # Body SMPP v3.4:
        # service_type (C-Octet String)
        body = b"\x00"
        # source_addr_ton (1B), source_addr_npi (1B), source_addr (C-Octet String)
        source_bytes = message.source_addr.encode("ascii", errors="replace") + b"\x00"
        body += struct.pack(">BB", 5, 0) + source_bytes  # TON=5 (Alphanumeric), NPI=0
        # dest_addr_ton (1B), dest_addr_npi (1B), destination_addr (C-Octet String)
        dest_bytes = message.dest_addr.encode("ascii", errors="replace") + b"\x00"
        body += struct.pack(">BB", 1, 1) + dest_bytes    # TON=1 (International), NPI=1 (ISDN)
        # esm_class, protocol_id, priority_flag
        body += struct.pack(">BBB", 0, 0, 1)
        # schedule_delivery_time (C-Octet), validity_period (C-Octet)
        body += b"\x00\x00"
        # registered_delivery, replace_if_present_flag, data_coding, sm_default_msg_id
        body += struct.pack(">BBBB", message.registered_delivery, 0, 0, 0)  # data_coding=0 (GSM 7-bit)
        # sm_length (1B) + short_message (N bytes)
        msg_bytes = message.short_message.encode("utf-8")
        body += struct.pack(">B", len(msg_bytes)) + msg_bytes

        header = cls.encode_header(
            command_id=SMPPCommandId.SUBMIT_SM.value,
            command_status=0,
            sequence_number=message.sequence_number,
            body_length=len(body)
        )
        return header + body

    @classmethod
    def encode_submit_sm_resp(cls, sequence_number: int, message_id: str, command_status: int = 0) -> bytes:
        """Codifica una respuesta SUBMIT_SM_RESP del SMSC."""
        body = message_id.encode("ascii") + b"\x00"
        header = cls.encode_header(
            command_id=SMPPCommandId.SUBMIT_SM_RESP.value,
            command_status=command_status,
            sequence_number=sequence_number,
            body_length=len(body)
        )
        return header + body


class SMPPGatewayClient:
    """
    Cliente de Pasarela SMPP v3.4 para conexión directa con el SMSC de Movilnet.
    Soporta modo Carrier en vivo y modo Simulación Hermética para CI/CD.
    """

    def __init__(
        self,
        smsc_host: str = "127.0.0.1",
        smsc_port: int = 2775,
        system_id: str = "MOVILNET_APP",
        password: str = "sovereign_smpp_2026",
        system_type: str = "TELCO",
        simulate: bool = True
    ):
        self.host = smsc_host
        self.port = smsc_port
        self.system_id = system_id
        self.password = password
        self.system_type = system_type
        self.simulate = simulate
        self._seq = 1

    def _next_seq(self) -> int:
        s = self._seq
        self._seq = (self._seq + 1) & 0x7FFFFFFF
        return s

    def submit_sms(self, dest_msisdn: str, text: str, source_id: str = "MOVILNET") -> Dict[str, Any]:
        """
        Despacha un SMS directo vía protocolo SMPP v3.4.
        """
        # Validaciones de dominio
        norm_dest = SovereignInvariants.validar_msisdn_movilnet(dest_msisdn)
        SovereignInvariants.validar_longitud_sms_smpp(text)

        seq = self._next_seq()
        message = SMPPMessage(
            source_addr=source_id,
            dest_addr=norm_dest,
            short_message=text,
            registered_delivery=1,
            sequence_number=seq
        )

        pdu_bytes = SMPPPduCodec.encode_submit_sm(message)

        if self.simulate:
            # Simulación determinista carrier-grade (<1ms)
            msg_id = f"MOV-SMPP-{seq:08d}"
            return {
                "success": True,
                "message_id": msg_id,
                "sequence_number": seq,
                "recipient": norm_dest,
                "char_count": len(text),
                "pdu_bytes_count": len(pdu_bytes),
                "mode": "SIMULATED_CARRIER_SMSC"
            }

        # Conexión real TCP con socket SMPP
        try:
            with socket.create_connection((self.host, self.port), timeout=3.0) as sock:
                sock.sendall(pdu_bytes)
                resp_header = sock.recv(SMPPPduCodec.HEADER_SIZE)
                if len(resp_header) >= SMPPPduCodec.HEADER_SIZE:
                    total_len, cmd_id, status, resp_seq = SMPPPduCodec.decode_header(resp_header)
                    body_len = total_len - SMPPPduCodec.HEADER_SIZE
                    body = sock.recv(body_len) if body_len > 0 else b""
                    msg_id = body.decode("ascii", errors="ignore").rstrip("\x00")
                    return {
                        "success": status == 0,
                        "command_status": status,
                        "message_id": msg_id or f"MOV-{resp_seq}",
                        "sequence_number": resp_seq,
                        "recipient": norm_dest,
                        "mode": "LIVE_SMSC_TCP"
                    }
                raise IOError("Respuesta SMPP incompleta del servidor SMSC")
        except Exception as e:
            logger.error(f"Fallo de comunicación con SMSC Movilnet ({self.host}:{self.port}): {e}")
            return {
                "success": False,
                "error": str(e),
                "recipient": norm_dest,
                "mode": "LIVE_SMSC_FAILED"
            }
