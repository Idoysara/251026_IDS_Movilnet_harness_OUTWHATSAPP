"""
Pruebas para el Servicio de Web Push Notifications (W3C Push API / RFC 8291).
Gobernanza: Universal Best Practices Engineering Rule (Pilar V).
"""
import pytest
from outwhatsapp.application.web_push_service import WebPushService
from outwhatsapp.domain.models import WebPushSubscription, WebPushKeys
from outwhatsapp.domain.enums import PushUrgency


def test_register_and_retrieve_push_subscription():
    service = WebPushService(simulate=True)
    sub = WebPushSubscription(
        endpoint="https://fcm.googleapis.com/fcm/send/fake-device-token-12345",
        keys=WebPushKeys(
            p256dh="BCVxsr7N_eNg62VoBlRA3GoRUKStMeAtA3LFgDzkrxZJjSgSnfckjZJuNn0W0_QdnFrnbfRHyED95BKA=",
            auth="tBHItJI5svbpez7KI4CCXg=="
        ),
        user_msisdn="04161234567"
    )

    assert service.registrar_suscripcion(sub) is True
    recup = service.obtener_suscripcion("04161234567")
    assert recup is not None
    assert recup.endpoint == sub.endpoint


def test_send_push_notification_success():
    service = WebPushService(simulate=True)
    sub = WebPushSubscription(
        endpoint="https://updates.push.services.mozilla.com/wpush/v2/fake-sub",
        keys=WebPushKeys(
            p256dh="BCVxsr7N_eNg62VoBlRA3GoRUKStMeAtA3LFgDzkrxZJjSgSnfckjZJuNn0W0_QdnFrnbfRHyED95BKA=",
            auth="tBHItJI5svbpez7KI4CCXg=="
        ),
        user_msisdn="04265554433"
    )
    service.registrar_suscripcion(sub)

    res = service.enviar_notificacion(
        msisdn="04265554433",
        titulo="Oferta 4GMAX",
        cuerpo="Tienes 20% de descuento en tu recarga hoy.",
        url_destino="https://pwa.movilnet.com.ve/?oferta=OF-01",
        urgencia=PushUrgency.HIGH
    )

    assert res["success"] is True
    assert res["delivered"] is True
    assert res["recipient"] == "04265554433"
    assert res["mode"] == "SIMULATED_WEB_PUSH"


def test_send_push_notification_without_subscription():
    service = WebPushService(simulate=True)
    res = service.enviar_notificacion(
        msisdn="04169999999",
        titulo="Aviso",
        cuerpo="Mensaje",
        url_destino="https://pwa.movilnet.com.ve/"
    )

    assert res["success"] is False
    assert res["delivered"] is False
    assert "No existe una suscripción" in res["error"]
