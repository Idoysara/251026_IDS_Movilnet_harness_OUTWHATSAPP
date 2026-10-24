"""
Pruebas Unitarias para Invariantes y Reglas de Dominio de OUTWHATSAPP.
Gobernanza: Universal Best Practices Engineering Rule (Pilar V).
"""
import time
import pytest
from outwhatsapp.domain.invariants import SovereignInvariants, SovereignInvariantViolationError


def test_valid_movilnet_msisdn():
    # Rango 0416
    assert SovereignInvariants.validar_msisdn_movilnet("04161234567") == "04161234567"
    assert SovereignInvariants.validar_msisdn_movilnet("+58 416-123.45.67") == "04161234567"
    assert SovereignInvariants.validar_msisdn_movilnet("584161234567") == "04161234567"

    # Rango 0426
    assert SovereignInvariants.validar_msisdn_movilnet("04269876543") == "04269876543"
    assert SovereignInvariants.validar_msisdn_movilnet("+584269876543") == "04269876543"


def test_invalid_carrier_rejected():
    # 0414 (Movistar) debe ser rechazado
    with pytest.raises(SovereignInvariantViolationError, match="no pertenece a Movilnet"):
        SovereignInvariants.validar_msisdn_movilnet("04141234567")

    # 0412 (Digitel) debe ser rechazado
    with pytest.raises(SovereignInvariantViolationError, match="no pertenece a Movilnet"):
        SovereignInvariants.validar_msisdn_movilnet("04121234567")

    # Longitud inválida
    with pytest.raises(SovereignInvariantViolationError, match="Longitud de MSISDN inválida"):
        SovereignInvariants.validar_msisdn_movilnet("041612")


def test_sms_length_limit():
    # 160 caracteres es válido
    texto_160 = "A" * 160
    SovereignInvariants.validar_longitud_sms_smpp(texto_160)

    # 161 caracteres debe fallar
    texto_161 = "A" * 161
    with pytest.raises(SovereignInvariantViolationError, match="excede el límite SMPP de 160"):
        SovereignInvariants.validar_longitud_sms_smpp(texto_161)


def test_magic_link_hmac_valid_and_expired():
    secret = b"TEST_SECRET_KEY_12345"
    msisdn = "04161234567"
    exp = int(time.time()) + 3600  # 1 hora adelante

    import hmac, hashlib
    datos = f"{msisdn}:{exp}".encode("utf-8")
    firma = hmac.new(secret, datos, hashlib.sha256).hexdigest()[:32]

    # Válido
    valido, msg = SovereignInvariants.validar_magic_link_hmac(msisdn, exp, firma, secret)
    assert valido is True

    # Expirado
    exp_pasado = int(time.time()) - 100
    valido_exp, msg_exp = SovereignInvariants.validar_magic_link_hmac(msisdn, exp_pasado, firma, secret)
    assert valido_exp is False
    assert "expirado" in msg_exp

    # Manipulado (firma falsa)
    valido_falso, msg_falso = SovereignInvariants.validar_magic_link_hmac(msisdn, exp, "FIRMA_FALSA_123", secret)
    assert valido_falso is False
    assert "inválida" in msg_falso
