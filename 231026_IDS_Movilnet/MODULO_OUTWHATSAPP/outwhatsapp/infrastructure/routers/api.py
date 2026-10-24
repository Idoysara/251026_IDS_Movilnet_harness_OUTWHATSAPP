"""
Enrutador RESTful de FastAPI para el Módulo Soberano OUTWHATSAPP (Puerto :8035).
Gobernanza: Universal Best Practices Engineering Rule (Pilares I y III).
"""
from typing import Dict, Any, Optional

try:
    from pydantic import BaseModel, Field
except ImportError:
    from outwhatsapp.domain.models import BaseModel, Field  # type: ignore

try:
    from fastapi import APIRouter, HTTPException, status
except ImportError:
    class _Status:
        HTTP_200_OK = 200
        HTTP_201_CREATED = 201
        HTTP_409_CONFLICT = 409
        HTTP_422_UNPROCESSABLE_CONTENT = 422
        HTTP_500_INTERNAL_SERVER_ERROR = 500
    status = _Status()  # type: ignore

    class HTTPException(Exception):  # type: ignore
        def __init__(self, status_code: int, detail: str = "") -> None:
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class _Route:
        def __init__(self, path: str) -> None:
            self.path = path

    class APIRouter:  # type: ignore
        def __init__(self, prefix: str = "", tags: Any = None) -> None:
            self.prefix = prefix
            self.routes = []

        def get(self, path: str, **kwargs: Any) -> Any:
            self.routes.append(_Route(self.prefix + path))
            return lambda fn: fn

        def post(self, path: str, **kwargs: Any) -> Any:
            self.routes.append(_Route(self.prefix + path))
            return lambda fn: fn

try:
    from outwhatsapp.domain.enums import SovereignChannel, DeliveryStatus
    from outwhatsapp.domain.models import WebPushSubscription, DispatchResult
    from outwhatsapp.domain.invariants import SovereignInvariantViolationError
    from outwhatsapp.domain.fsm import IllegalDispatchStateTransitionError
    from outwhatsapp.application.sovereign_dispatcher import SovereignDispatcher
    from outwhatsapp.application.web_push_service import WebPushService
    from outwhatsapp.application.smpp_gateway import SMPPGatewayClient
    from outwhatsapp.application.telegram_webapp_service import TelegramWebAppService
    from outwhatsapp.application.local_orchestrator import LocalAsyncOrchestrator
    from outwhatsapp.infrastructure.repository import OutWhatsAppRepository
except ImportError:
    from outwhatsapp.domain.enums import SovereignChannel, DeliveryStatus
    from outwhatsapp.domain.models import WebPushSubscription, DispatchResult
    from outwhatsapp.domain.invariants import SovereignInvariantViolationError
    from outwhatsapp.domain.fsm import IllegalDispatchStateTransitionError
    from outwhatsapp.application.sovereign_dispatcher import SovereignDispatcher
    from outwhatsapp.application.web_push_service import WebPushService
    from outwhatsapp.application.smpp_gateway import SMPPGatewayClient
    from outwhatsapp.application.telegram_webapp_service import TelegramWebAppService
    from outwhatsapp.application.local_orchestrator import LocalAsyncOrchestrator
    from ..repository import OutWhatsAppRepository

router = APIRouter(prefix="/api/v1", tags=["OUTWHATSAPP Soberano"])

# Dependencias singleton
_repo = OutWhatsAppRepository()
_smpp = SMPPGatewayClient(simulate=True)
_push = WebPushService(simulate=True)
_dispatcher = SovereignDispatcher(smpp_client=_smpp, push_service=_push)
_orchestrator = LocalAsyncOrchestrator(dispatcher=_dispatcher)


class DispatchRequestDTO(BaseModel):
    msisdn: str = Field(..., description="MSISDN Movilnet (0416 / 0426)")
    titulo: str = Field(..., description="Título de la notificación")
    mensaje: str = Field(..., description="Cuerpo del mensaje")
    canal_preferido: Optional[SovereignChannel] = None
    telegram_chat_id: Optional[int] = None


class SMPPSendRequestDTO(BaseModel):
    msisdn: str = Field(..., description="MSISDN destino")
    mensaje: str = Field(..., max_length=160, description="Texto SMS (máx 160 chars)")
    remitente: str = Field(default="MOVILNET", description="Nombre del remitente")


class TelegramDeflectRequestDTO(BaseModel):
    chat_id: int
    msisdn: str
    titulo: str = "Movilnet 4GMAX"
    mensaje: str = "Ingresa a tu cuenta sin consumir megas:"


@router.post("/sovereign/dispatch", response_model=DispatchResult, status_code=status.HTTP_200_OK)
def despachar_mensaje(dto: DispatchRequestDTO):
    """Despacha un mensaje por el canal más óptimo libre de WhatsApp."""
    try:
        resultado = _dispatcher.despachar(
            msisdn=dto.msisdn,
            titulo=dto.titulo,
            mensaje=dto.mensaje,
            canal_preferido=dto.canal_preferido,
            telegram_chat_id=dto.telegram_chat_id
        )
        return resultado
    except SovereignInvariantViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/push/subscribe", status_code=status.HTTP_201_CREATED)
def suscribir_web_push(sub: WebPushSubscription):
    """Registra una suscripción de navegador W3C Push para la PWA."""
    try:
        _push.registrar_suscripcion(sub)
        _repo.guardar_suscripcion(sub)
        return {"success": True, "message": "Suscripción Web Push registrada exitosamente", "msisdn": sub.user_msisdn}
    except SovereignInvariantViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))


@router.post("/smpp/send", status_code=status.HTTP_200_OK)
def enviar_sms_directo(dto: SMPPSendRequestDTO):
    """Envío directo de SMS al SMSC de Movilnet mediante protocolo SMPP v3.4."""
    try:
        res = _smpp.submit_sms(dto.msisdn, dto.mensaje, dto.remitente)
        return res
    except SovereignInvariantViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))


@router.post("/telegram/deflect", status_code=status.HTTP_200_OK)
def generar_deflexion_telegram(dto: TelegramDeflectRequestDTO):
    """Genera el payload con botón nativo WebApp para Telegram Bot API."""
    try:
        magic_link = _dispatcher.generar_magic_link(dto.msisdn)
        payload = TelegramWebAppService.construir_payload_webapp(
            chat_id=dto.chat_id,
            webapp_url=magic_link,
            mensaje_texto=f"<b>{dto.titulo}</b>\n{dto.mensaje}",
            texto_boton="🚀 Abrir Portal 4GMAX"
        )
        return {"success": True, "payload": payload, "magic_link": magic_link}
    except SovereignInvariantViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))


@router.get("/metrics", status_code=status.HTTP_200_OK)
def obtener_metricas():
    """Retorna telemetría dura del repositorio y orquestador local."""
    m_repo = _repo.obtener_resumen_metricas()
    m_orch = _orchestrator.metricas()
    return {
        "modulo": "OUTWHATSAPP",
        "puerto": 8035,
        "soberania": "100% LIBRE DE WHATSAPP / META",
        "metricas_persistencia": m_repo,
        "metricas_orquestador": m_orch
    }
