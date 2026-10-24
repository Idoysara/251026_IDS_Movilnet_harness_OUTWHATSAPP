"""
Invariantes Matemáticas y Reglas de Negocio Inviolables para OUTWHATSAPP.
Gobernanza: Universal Best Practices Engineering Rule (Pilares I, III y VI).
"""
import hmac
import hashlib
import time
import re
from typing import Tuple, Optional


class SovereignInvariantViolationError(Exception):
    """Excepción específica cuando se vulnera una regla invariante de soberanía."""
    pass


class SovereignInvariants:
    """Validador estricto de invariantes en la frontera del dominio."""

    @staticmethod
    def validar_msisdn_movilnet(msisdn: str) -> str:
        """
        Valida que el número pertenezca al rango oficial de Movilnet (0416 / 0426).
        Retorna el número normalizado a 11 dígitos nacionales (ej. 04161234567).
        """
        if not msisdn:
            raise SovereignInvariantViolationError("El número telefónico no puede ser nulo o vacío.")
        
        # Limpieza de caracteres no numéricos
        clean = re.sub(r"[^\d]", "", msisdn)
        
        # Manejo de prefijo internacional +58
        if clean.startswith("58") and len(clean) in (12, 13):
            clean = clean[2:]
        elif clean.startswith("0") and len(clean) == 11:
            clean = clean[1:]  # Quitar 0 inicial temporalmente
        
        # Ahora clean debe tener 10 dígitos (ej. 4161234567)
        if len(clean) != 10:
            raise SovereignInvariantViolationError(
                f"Longitud de MSISDN inválida: '{msisdn}' tiene {len(clean)} dígitos efectivos (esperado 10 u 11)."
            )
        
        prefix = clean[:3]
        if prefix not in ("416", "426"):
            raise SovereignInvariantViolationError(
                f"El número '{msisdn}' no pertenece a Movilnet (prefijo esperado 0416 o 0426, recibido {prefix})."
            )
        
        return f"0{clean}"

    @staticmethod
    def validar_longitud_sms_smpp(texto: str) -> None:
        """
        Garantiza que el mensaje para SMS SMPP no supere el límite de 160 caracteres GSM-7.
        Evita costos de fragmentación de SMS y fallos en el SMSC.
        """
        if not texto:
            raise SovereignInvariantViolationError("El texto del SMS no puede estar vacío.")
        if len(texto) > 160:
            raise SovereignInvariantViolationError(
                f"El texto SMS excede el límite SMPP de 160 caracteres: longitud actual = {len(texto)}."
            )

    @staticmethod
    def validar_magic_link_hmac(
        msisdn: str,
        exp_timestamp: int,
        firma: str,
        secret_key: bytes
    ) -> Tuple[bool, str]:
        """
        Verifica criptográficamente la validez e inmutabilidad de un Magic Link.
        """
        try:
            norm_msisdn = SovereignInvariants.validar_msisdn_movilnet(msisdn)
        except SovereignInvariantViolationError as e:
            return False, f"MSISDN inválido: {str(e)}"

        now = int(time.time())
        if exp_timestamp < now:
            return False, f"El enlace ha expirado (expiró hace {now - exp_timestamp} segundos)."

        # Recalcular firma esperada: msisdn:exp
        datos = f"{norm_msisdn}:{exp_timestamp}".encode("utf-8")
        firma_esperada = hmac.new(secret_key, datos, hashlib.sha256).hexdigest()[:32]

        if not hmac.compare_digest(firma, firma_esperada):
            return False, "Firma criptográfica inválida (posible manipulación de URL)."

        return True, "Enlace válido y autenticado."

    @staticmethod
    def validar_suscripcion_push(endpoint: str, p256dh: str, auth: str) -> None:
        """
        Valida que los metadatos de la suscripción W3C Push cumplan los estándares RFC 8291.
        """
        if not endpoint or not endpoint.startswith(("https://", "http://localhost")):
            raise SovereignInvariantViolationError("El endpoint de Push debe ser una URL HTTPS segura.")
        if not p256dh or len(p256dh) < 40:
            raise SovereignInvariantViolationError("Clave pública p256dh inválida o corrupta.")
        if not auth or len(auth) < 16:
            raise SovereignInvariantViolationError("Secreto de autenticación auth inválido o corrupto.")
