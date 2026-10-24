"""
Orquestador Omnicanal Soberano de Despacho (Sovereign Dispatcher).
Gobernanza: Universal Best Practices Engineering Rule (Pilares I, III y IV).
Enruta las comunicaciones a través de canales propios de Movilnet erradicando la dependencia de WhatsApp.
"""
import time
import os
import hmac
import hashlib
import urllib.parse
from typing import Dict, Any, Optional

try:
    from outwhatsapp.domain.enums import SovereignChannel, DeliveryStatus, PushUrgency
    from outwhatsapp.domain.models import SovereignDispatchEvent, DispatchResult
    from outwhatsapp.domain.invariants import SovereignInvariants
    from outwhatsapp.domain.fsm import SovereignDispatchFSM
    from outwhatsapp.application.smpp_gateway import SMPPGatewayClient
    from outwhatsapp.application.web_push_service import WebPushService
    from outwhatsapp.application.telegram_webapp_service import TelegramWebAppService
except ImportError:
    from outwhatsapp.domain.enums import SovereignChannel, DeliveryStatus, PushUrgency
    from outwhatsapp.domain.models import SovereignDispatchEvent, DispatchResult
    from outwhatsapp.domain.invariants import SovereignInvariants
    from outwhatsapp.domain.fsm import SovereignDispatchFSM
    from outwhatsapp.application.smpp_gateway import SMPPGatewayClient
    from outwhatsapp.application.web_push_service import WebPushService
    from outwhatsapp.application.telegram_webapp_service import TelegramWebAppService

DEFAULT_SECRET = os.getenv("SOVEREIGN_MAGIC_SECRET", "MOVILNET_OUTWHATSAPP_SOVEREIGN_KEY_2026").encode("utf-8")
DEFAULT_BASE_PWA = os.getenv("SOVEREIGN_PWA_URL", "https://one21026-ids-movilnet-pwa.onrender.com/ui/pwa_stitch/index.html")


class SovereignDispatcher:
    """
    Orquestador principal que selecciona el canal más eficiente y soberano
    para comunicar al abonado sin depender de WhatsApp.
    """

    def __init__(
        self,
        smpp_client: Optional[SMPPGatewayClient] = None,
        push_service: Optional[WebPushService] = None,
        secret_key: bytes = DEFAULT_SECRET,
        base_pwa_url: str = DEFAULT_BASE_PWA
    ):
        self.smpp = smpp_client or SMPPGatewayClient()
        self.push = push_service or WebPushService()
        self.secret = secret_key
        self.base_pwa_url = base_pwa_url

    def generar_magic_link(self, msisdn: str, duracion_segundos: int = 86400) -> str:
        """
        Genera un Magic Link criptográfico firmado con HMAC-SHA256 para auto-login en la PWA.
        """
        norm_msisdn = SovereignInvariants.validar_msisdn_movilnet(msisdn)
        exp_timestamp = int(time.time()) + duracion_segundos
        datos = f"{norm_msisdn}:{exp_timestamp}".encode("utf-8")
        firma = hmac.new(self.secret, datos, hashlib.sha256).hexdigest()[:32]

        params = urllib.parse.urlencode({
            "msisdn": norm_msisdn,
            "exp": str(exp_timestamp),
            "sig": firma
        })
        base = self.base_pwa_url.split("?")[0]
        return f"{base}?{params}"

    def despachar(
        self,
        msisdn: str,
        titulo: str,
        mensaje: str,
        canal_preferido: Optional[SovereignChannel] = None,
        telegram_chat_id: Optional[int] = None
    ) -> DispatchResult:
        """
        Orquesta el despacho inteligente por el mejor canal disponible.
        Prioridad automática:
        1. PWA Push (si el usuario tiene token de navegador activo).
        2. SMS SMPP Telco (canal carrier directo y gratuito para Movilnet).
        3. Telegram WebApp (si se provee chat_id).
        """
        t0 = time.time()
        norm_msisdn = SovereignInvariants.validar_msisdn_movilnet(msisdn)
        magic_link = self.generar_magic_link(norm_msisdn)

        # 1. Determinación de canal
        canal_elegido = canal_preferido
        if not canal_elegido:
            if self.push.obtener_suscripcion(norm_msisdn) is not None:
                canal_elegido = SovereignChannel.PWA_PUSH
            elif telegram_chat_id is not None:
                canal_elegido = SovereignChannel.TELEGRAM_WEBAPP
            else:
                canal_elegido = SovereignChannel.SMS_SMPP

        event = SovereignDispatchEvent(
            recipient_msisdn=norm_msisdn,
            channel=canal_elegido,
            message_body=mensaje,
            magic_link=magic_link,
            status=DeliveryStatus.QUEUED
        )

        # 2. Ejecución según canal
        resultado_detalle: Dict[str, Any] = {}
        exito = False

        try:
            if canal_elegido == SovereignChannel.PWA_PUSH:
                res_push = self.push.enviar_notificacion(
                    msisdn=norm_msisdn,
                    titulo=titulo,
                    cuerpo=mensaje,
                    url_destino=magic_link,
                    urgencia=PushUrgency.HIGH
                )
                exito = res_push.get("success", False)
                resultado_detalle = res_push
                if not exito:
                    # Fallback automático a SMS SMPP
                    canal_elegido = SovereignChannel.SMS_SMPP
                    sms_text = f"{titulo}: {mensaje}\nPortal: {magic_link}"[:160]
                    res_smpp = self.smpp.submit_sms(norm_msisdn, sms_text)
                    exito = res_smpp.get("success", False)
                    resultado_detalle = {"push_fallback": res_push, "smpp_result": res_smpp}

            elif canal_elegido == SovereignChannel.SMS_SMPP:
                # Construir SMS que quepa en 160 caracteres con el enlace
                sms_text = f"{titulo}: {mensaje} Entra: {magic_link}"
                if len(sms_text) > 160:
                    sms_text = f"{titulo}. Ver: {magic_link}"[:160]
                
                res_smpp = self.smpp.submit_sms(norm_msisdn, sms_text)
                exito = res_smpp.get("success", False)
                resultado_detalle = res_smpp

            elif canal_elegido == SovereignChannel.TELEGRAM_WEBAPP:
                if telegram_chat_id is None:
                    raise ValueError("Se requiere telegram_chat_id para canal TELEGRAM_WEBAPP")
                payload_tg = TelegramWebAppService.construir_payload_webapp(
                    chat_id=telegram_chat_id,
                    webapp_url=magic_link,
                    mensaje_texto=f"<b>{titulo}</b>\n{mensaje}"
                )
                exito = True
                resultado_detalle = {"telegram_payload": payload_tg, "mode": "TELEGRAM_WEBAPP_READY"}

            nuevo_estado = DeliveryStatus.DISPATCHED if exito else DeliveryStatus.FAILED
            SovereignDispatchFSM.validar_transicion(event.status, nuevo_estado)
            event.status = nuevo_estado

        except Exception as e:
            exito = False
            resultado_detalle = {"error": str(e)}
            event.status = DeliveryStatus.FAILED

        latency_ms = (time.time() - t0) * 1000.0
        event.latency_ms = latency_ms

        return DispatchResult(
            success=exito,
            event_id=event.id,
            channel_used=canal_elegido,
            delivery_status=event.status,
            latency_ms=latency_ms,
            message="Despacho soberano exitoso" if exito else "Fallo en despacho soberano",
            details=resultado_detalle
        )
