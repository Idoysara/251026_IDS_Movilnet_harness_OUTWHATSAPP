"""
Pruebas para el Orquestador Soberano (Sovereign Dispatcher).
Gobernanza: Universal Best Practices Engineering Rule (Pilar V).
"""
import pytest
from outwhatsapp.application.sovereign_dispatcher import SovereignDispatcher
from outwhatsapp.application.web_push_service import WebPushService
from outwhatsapp.application.smpp_gateway import SMPPGatewayClient
from outwhatsapp.domain.enums import SovereignChannel, DeliveryStatus
from outwhatsapp.domain.models import WebPushSubscription, WebPushKeys


def test_magic_link_generation():
    dispatcher = SovereignDispatcher()
    link = dispatcher.generar_magic_link("04161234567")
    assert "msisdn=04161234567" in link
    assert "sig=" in link
    assert "exp=" in link


def test_dispatch_selects_smpp_by_default():
    dispatcher = SovereignDispatcher()
    # Sin suscripción push, debe elegir SMS SMPP
    res = dispatcher.despachar(
        msisdn="04161234567",
        titulo="Pago Recibido",
        mensaje="Tu pago móvil C2P fue validado con éxito."
    )

    assert res.success is True
    assert res.channel_used == SovereignChannel.SMS_SMPP
    assert res.delivery_status == DeliveryStatus.DISPATCHED
    assert res.latency_ms < 50.0


def test_dispatch_selects_push_if_subscribed():
    push_svc = WebPushService(simulate=True)
    push_svc.registrar_suscripcion(
        WebPushSubscription(
            endpoint="https://fcm.googleapis.com/fcm/send/token123",
            keys=WebPushKeys(p256dh="BCVxsr7N_eNg62VoBlRA3GoRUKStMeAtA3LFgDzkrxZJjSgSnfckjZJuNn0W0_QdnFrnbfRHyED95BKA=", auth="tBHItJI5svbpez7KI4CCXg=="),
            user_msisdn="04261234567"
        )
    )

    dispatcher = SovereignDispatcher(push_service=push_svc)
    res = dispatcher.despachar(
        msisdn="04261234567",
        titulo="Alerta Push",
        mensaje="Bienvenido a tu portal PWA soberano."
    )

    assert res.success is True
    assert res.channel_used == SovereignChannel.PWA_PUSH
    assert res.delivery_status == DeliveryStatus.DISPATCHED


def test_dispatch_selects_telegram_webapp():
    dispatcher = SovereignDispatcher()
    res = dispatcher.despachar(
        msisdn="04161234567",
        titulo="Telegram WebApp",
        mensaje="Accede con un toque a Movilnet:",
        telegram_chat_id=987654321
    )

    assert res.success is True
    assert res.channel_used == SovereignChannel.TELEGRAM_WEBAPP
    assert "telegram_payload" in res.details
    assert res.details["telegram_payload"]["chat_id"] == 987654321
