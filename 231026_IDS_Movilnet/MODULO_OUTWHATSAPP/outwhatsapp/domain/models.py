"""
Modelos de Dominio Fuertemente Tipados para el Módulo Soberano OUTWHATSAPP.
Gobernanza: Universal Best Practices Engineering Rule (Pilares I y III).
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

try:
    from pydantic import BaseModel, Field
except ImportError:
    class _FieldInfo:
        def __init__(self, default: Any = ..., default_factory: Any = None, **kwargs: Any) -> None:
            self.default = default
            self.default_factory = default_factory

    def Field(default: Any = ..., *, default_factory: Any = None, **kwargs: Any) -> Any:  # type: ignore
        return _FieldInfo(default=default, default_factory=default_factory, **kwargs)

    class BaseModel:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            for cls in reversed(self.__class__.__mro__):
                for k, v in cls.__dict__.items():
                    if k.startswith("_") or callable(v):
                        continue
                    if isinstance(v, _FieldInfo):
                        if v.default_factory is not None:
                            setattr(self, k, v.default_factory())
                        elif v.default is not ...:
                            setattr(self, k, v.default)
                    else:
                        setattr(self, k, v)
            for k, v in kwargs.items():
                setattr(self, k, v)

        def dict(self) -> Dict[str, Any]:
            return dict(self.__dict__)

        def model_dump(self) -> Dict[str, Any]:
            return dict(self.__dict__)

from .enums import SovereignChannel, DeliveryStatus, PushUrgency


class WebPushKeys(BaseModel):
    """Claves criptográficas de la suscripción W3C Push."""
    p256dh: str = Field(..., description="Clave pública del cliente en base64url")
    auth: str = Field(..., description="Secreto de autenticación del cliente en base64url")


class WebPushSubscription(BaseModel):
    """Descriptor de suscripción Web Push RFC 8291."""
    endpoint: str = Field(..., description="URL única del Push Service del navegador")
    keys: WebPushKeys = Field(..., description="Par de claves criptográficas")
    user_msisdn: str = Field(..., description="Número de línea Movilnet asociado")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)


class SMPPMessage(BaseModel):
    """Mensaje SMS estructurado para entrega SMPP v3.4 al SMSC."""
    source_addr: str = Field(default="MOVILNET", description="Remitente alfanumérico o corto")
    dest_addr: str = Field(..., description="Número de destino E.164 (ej. 584161234567)")
    short_message: str = Field(..., max_length=160, description="Cuerpo del SMS (GSM 7-bit, máx 160 caracteres)")
    registered_delivery: int = Field(default=1, description="1 para solicitar Delivery Receipt")
    sequence_number: int = Field(default=1, description="Número de secuencia de la PDU")


class TelegramWebAppData(BaseModel):
    """Estructura de botón WebApp para bots de Telegram."""
    chat_id: int = Field(..., description="Identificador único del chat en Telegram")
    button_text: str = Field(default="🌐 Abrir Portal Movilnet 4GMAX", description="Etiqueta del botón nativo")
    webapp_url: str = Field(..., description="URL firmada con Magic Link y Zero-Rating")
    reply_text: str = Field(default="Accede a tu cuenta Movilnet sin costo de datos móviles:", description="Mensaje acompañante")


class SovereignDispatchEvent(BaseModel):
    """Evento inmutable de despacho por canales soberanos."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recipient_msisdn: str = Field(..., description="MSISDN del abonado")
    channel: SovereignChannel = Field(..., description="Canal soberano seleccionado")
    message_body: str = Field(..., description="Contenido textual del mensaje")
    magic_link: Optional[str] = Field(default=None, description="Enlace Zero-Rating firmado con HMAC")
    status: DeliveryStatus = Field(default=DeliveryStatus.QUEUED)
    latency_ms: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DLQEvent(BaseModel):
    """Registro de evento en Dead Letter Queue para reintentos con retroceso exponencial."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_channel: SovereignChannel = Field(...)
    recipient_msisdn: str = Field(...)
    payload: Dict[str, Any] = Field(...)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=5)
    last_error: str = Field(default="")
    next_retry_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DispatchResult(BaseModel):
    """Resultado unificado de despacho omnicanal."""
    success: bool
    event_id: str
    channel_used: SovereignChannel
    delivery_status: DeliveryStatus
    latency_ms: float
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
