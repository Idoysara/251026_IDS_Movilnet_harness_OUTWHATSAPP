"""
Pruebas de Protocolo SMPP v3.4 Carrier-Grade (Codec y Pasarela de SMSC).
Gobernanza: Universal Best Practices Engineering Rule (Pilar V).
"""
import pytest
from outwhatsapp.application.smpp_gateway import SMPPPduCodec, SMPPGatewayClient
from outwhatsapp.domain.models import SMPPMessage
from outwhatsapp.domain.enums import SMPPCommandId


def test_smpp_header_codec():
    # Codificar cabecera SUBMIT_SM (Command ID: 0x00000004)
    cmd_id = SMPPCommandId.SUBMIT_SM.value
    seq = 42
    body_len = 50
    header_bytes = SMPPPduCodec.encode_header(cmd_id, 0, seq, body_len)

    assert len(header_bytes) == 16
    total_len, dec_cmd, dec_stat, dec_seq = SMPPPduCodec.decode_header(header_bytes)

    assert total_len == 66  # 16 + 50
    assert dec_cmd == cmd_id
    assert dec_stat == 0
    assert dec_seq == seq


def test_submit_sm_pdu_encoding():
    msg = SMPPMessage(
        source_addr="MOVILNET",
        dest_addr="04161234567",
        short_message="Tu recarga de 10GB 4GMAX fue procesada.",
        registered_delivery=1,
        sequence_number=10
    )
    pdu = SMPPPduCodec.encode_submit_sm(msg)

    assert len(pdu) > 16
    total_len, cmd_id, status, seq = SMPPPduCodec.decode_header(pdu[:16])
    assert cmd_id == SMPPCommandId.SUBMIT_SM.value
    assert seq == 10
    assert b"Tu recarga de 10GB 4GMAX fue procesada." in pdu


def test_submit_sm_resp_pdu():
    pdu_resp = SMPPPduCodec.encode_submit_sm_resp(sequence_number=10, message_id="MOV-987654", command_status=0)
    assert len(pdu_resp) > 16
    total_len, cmd_id, status, seq = SMPPPduCodec.decode_header(pdu_resp[:16])
    assert cmd_id == SMPPCommandId.SUBMIT_SM_RESP.value
    assert status == 0
    assert seq == 10
    assert b"MOV-987654" in pdu_resp


def test_smpp_gateway_client_simulation():
    client = SMPPGatewayClient(simulate=True)
    res = client.submit_sms(
        dest_msisdn="04261112233",
        text="Aviso de saldo crítico: 5 Bs restantes.",
        source_id="MOVILNET"
    )

    assert res["success"] is True
    assert res["mode"] == "SIMULATED_CARRIER_SMSC"
    assert res["recipient"] == "04261112233"
    assert "message_id" in res
