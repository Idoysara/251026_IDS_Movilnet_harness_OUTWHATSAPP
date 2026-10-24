"""
Enumeraciones e Invariantes Tipadas para el Módulo Soberano OUTWHATSAPP.
Gobernanza: Universal Best Practices Engineering Rule (Pilares I y III).
"""
from enum import Enum


class SovereignChannel(str, Enum):
    """Canales de comunicación 100% soberanos libres de WhatsApp."""
    PWA_PUSH = "PWA_PUSH"             # Web Push Notifications estándar W3C (VAPID)
    SMS_SMPP = "SMS_SMPP"             # Mensajería SMS directa al SMSC Movilnet (SMPP v3.4)
    TELEGRAM_WEBAPP = "TELEGRAM_WEBAPP"# Bot oficial con apertura de Mini-App PWA
    PWA_DIRECT = "PWA_DIRECT"         # Interacción directa por WebSocket / HTTP en la PWA


class DeliveryStatus(str, Enum):
    """Estados del ciclo de vida de un despacho soberano."""
    QUEUED = "QUEUED"                 # En cola local en memoria / SQLite WAL
    DISPATCHED = "DISPATCHED"         # Emitido por el canal de salida
    DELIVERED_PWA = "DELIVERED_PWA"   # Notificación recibida en el dispositivo
    PWA_OPENED = "PWA_OPENED"         # Usuario abrió la PWA mediante el Magic Link
    COMPLETED = "COMPLETED"           # Trámite o consulta finalizada
    FAILED = "FAILED"                 # Fallo en el canal (deriva a DLQ)


class SMPPCommandId(int, Enum):
    """Identificadores canónicos de PDU del protocolo SMPP v3.4."""
    GENERIC_NACK = 0x80000000
    BIND_TRANSMITTER = 0x00000002
    BIND_TRANSMITTER_RESP = 0x80000002
    SUBMIT_SM = 0x00000004
    SUBMIT_SM_RESP = 0x80000004
    DELIVER_SM = 0x00000005
    DELIVER_SM_RESP = 0x80000005
    ENQUIRE_LINK = 0x00000015
    ENQUIRE_LINK_RESP = 0x80000015


class PushUrgency(str, Enum):
    """Nivel de urgencia RFC 8030 para notificaciones Web Push."""
    VERY_LOW = "very-low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
