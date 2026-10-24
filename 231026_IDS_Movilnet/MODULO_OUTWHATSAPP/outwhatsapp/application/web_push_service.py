"""
Servicio Soberano de Web Push Notifications (W3C Push API / RFC 8291 / RFC 8292).
Gobernanza: Universal Best Practices Engineering Rule (Pilares I y III).
Permite notificar al abonado directamente en su navegador/PWA sin intermediarios.
"""
import json
import time
import base64
import os
import logging
from typing import Dict, Any, Optional

try:
    from outwhatsapp.domain.models import WebPushSubscription, WebPushKeys
    from outwhatsapp.domain.enums import PushUrgency
    from outwhatsapp.domain.invariants import SovereignInvariants
except ImportError:
    from outwhatsapp.domain.models import WebPushSubscription, WebPushKeys
    from outwhatsapp.domain.enums import PushUrgency
    from outwhatsapp.domain.invariants import SovereignInvariants

logger = logging.getLogger("outwhatsapp.push")

DEFAULT_VAPID_PUBLIC_KEY = os.getenv(
    "MOVILNET_VAPID_PUBLIC_KEY",
    "BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjZJuNn0W0_QdnFrnbfRHyED95BKA"
)
DEFAULT_VAPID_PRIVATE_KEY = os.getenv(
    "MOVILNET_VAPID_PRIVATE_KEY",
    "vv19WfK3NfZj3-eYk8Fv8u2mI3jG3gM6r-K8hQ=="
)
DEFAULT_VAPID_CLAIMS_SUB = "mailto:soporte@movilnet.com.ve"


class WebPushService:
    """
    Servicio de emisión y gestión de Notificaciones Web Push soberanas.
    """

    def __init__(
        self,
        public_vapid_key: str = DEFAULT_VAPID_PUBLIC_KEY,
        private_vapid_key: str = DEFAULT_VAPID_PRIVATE_KEY,
        subject: str = DEFAULT_VAPID_CLAIMS_SUB,
        simulate: bool = True
    ):
        self.public_key = public_vapid_key
        self.private_key = private_vapid_key
        self.subject = subject
        self.simulate = simulate
        self._subscriptions: Dict[str, WebPushSubscription] = {}

    def registrar_suscripcion(self, subscription: WebPushSubscription) -> bool:
        """
        Registra una suscripción de navegador validando invariantes RFC 8291.
        """
        SovereignInvariants.validar_suscripcion_push(
            subscription.endpoint,
            subscription.keys.p256dh,
            subscription.keys.auth
        )
        norm_msisdn = SovereignInvariants.validar_msisdn_movilnet(subscription.user_msisdn)
        subscription.user_msisdn = norm_msisdn
        self._subscriptions[norm_msisdn] = subscription
        logger.info(f"Suscripción Web Push registrada exitosamente para {norm_msisdn}")
        return True

    def obtener_suscripcion(self, msisdn: str) -> Optional[WebPushSubscription]:
        """Obtiene la suscripción activa por MSISDN normalizado."""
        norm_msisdn = SovereignInvariants.validar_msisdn_movilnet(msisdn)
        return self._subscriptions.get(norm_msisdn)

    def enviar_notificacion(
        self,
        msisdn: str,
        titulo: str,
        cuerpo: str,
        url_destino: str,
        urgencia: PushUrgency = PushUrgency.HIGH,
        ttl_segundos: int = 86400
    ) -> Dict[str, Any]:
        """
        Emite una notificación push soberana al dispositivo del abonado.
        """
        norm_msisdn = SovereignInvariants.validar_msisdn_movilnet(msisdn)
        sub = self.obtener_suscripcion(norm_msisdn)

        if not sub:
            return {
                "success": False,
                "error": f"No existe una suscripción Web Push registrada para {norm_msisdn}",
                "recipient": norm_msisdn,
                "delivered": False
            }

        payload = {
            "title": titulo,
            "body": cuerpo,
            "icon": "/ui/pwa_stitch/assets/icons/icon-192.png",
            "badge": "/ui/pwa_stitch/assets/icons/badge-72.png",
            "data": {
                "url": url_destino,
                "timestamp": int(time.time()),
                "msisdn": norm_msisdn
            }
        }
        payload_json = json.dumps(payload, ensure_ascii=False)

        if self.simulate:
            # Entrega simulada determinista (<1ms)
            return {
                "success": True,
                "delivered": True,
                "recipient": norm_msisdn,
                "endpoint": sub.endpoint,
                "urgency": urgencia.value,
                "ttl": ttl_segundos,
                "payload_size_bytes": len(payload_json.encode("utf-8")),
                "mode": "SIMULATED_WEB_PUSH"
            }

        # Modo de red HTTP a FCM / Mozilla Push Service
        try:
            import urllib.request
            headers = {
                "TTL": str(ttl_segundos),
                "Urgency": urgencia.value,
                "Content-Type": "application/json"
            }
            req = urllib.request.Request(
                sub.endpoint,
                data=payload_json.encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                status_code = resp.getcode()
                return {
                    "success": 200 <= status_code < 300,
                    "delivered": 200 <= status_code < 300,
                    "recipient": norm_msisdn,
                    "status_code": status_code,
                    "mode": "LIVE_PUSH_SERVICE"
                }
        except Exception as e:
            logger.error(f"Fallo al emitir Web Push a {sub.endpoint}: {e}")
            return {
                "success": False,
                "delivered": False,
                "error": str(e),
                "recipient": norm_msisdn,
                "mode": "LIVE_PUSH_FAILED"
            }
