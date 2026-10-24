"""
Pruebas de Integración para los Endpoints RESTful de OUTWHATSAPP.
Gobernanza: Universal Best Practices Engineering Rule (Pilar V).
"""
import pytest
from starlette.testclient import TestClient
from outwhatsapp.infrastructure.server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ONLINE"
    assert data["service"] == "modulo_outwhatsapp"
    assert data["whatsapp_dependency"] == "ERRADICADA"


def test_sovereign_dispatch_endpoint(client):
    payload = {
        "msisdn": "04161234567",
        "titulo": "Confirmación C2P",
        "mensaje": "Tu recarga ha sido acreditada exitosamente."
    }
    resp = client.post("/api/v1/sovereign/dispatch", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["channel_used"] == "SMS_SMPP"
    assert "event_id" in data


def test_push_subscribe_endpoint(client):
    sub_payload = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/fake-test-token",
        "keys": {
            "p256dh": "BCVxsr7N_eNg62VoBlRA3GoRUKStMeAtA3LFgDzkrxZJjSgSnfckjZJuNn0W0_QdnFrnbfRHyED95BKA=",
            "auth": "tBHItJI5svbpez7KI4CCXg=="
        },
        "user_msisdn": "04161234567"
    }
    resp = client.post("/api/v1/push/subscribe", json=sub_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert "msisdn" in data


def test_smpp_send_endpoint(client):
    payload = {
        "msisdn": "04269988776",
        "mensaje": "Aviso SMS directo por el SMSC de Movilnet.",
        "remitente": "MOVILNET"
    }
    resp = client.post("/api/v1/smpp/send", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["recipient"] == "04269988776"


def test_telegram_deflect_endpoint(client):
    payload = {
        "chat_id": 123456789,
        "msisdn": "04161234567",
        "titulo": "Movilnet PWA",
        "mensaje": "Ingresa sin consumir megas:"
    }
    resp = client.post("/api/v1/telegram/deflect", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "payload" in data
    assert "magic_link" in data


def test_metrics_endpoint(client):
    resp = client.get("/api/v1/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["modulo"] == "OUTWHATSAPP"
    assert "metricas_persistencia" in data
    assert "metricas_orquestador" in data


def test_invalid_msisdn_returns_422(client):
    payload = {
        "msisdn": "04149999999",  # Prefijo Movistar inválido para Movilnet
        "titulo": "Aviso",
        "mensaje": "Mensaje de prueba"
    }
    resp = client.post("/api/v1/sovereign/dispatch", json=payload)
    assert resp.status_code == 422
    data = resp.json()
    assert "detail" in data
    assert "no pertenece a Movilnet" in data["detail"]


def test_n8n_facade_send_text_endpoint(client):
    """Verifica que N8N pueda entregar su respuesta a OUTWHATSAPP sin usar WhatsApp."""
    payload = {
        "number": "584161234567",
        "text": "Estimado abonado, su saldo actual es de 250.00 VES. Recargue en https://pwa.movilnet.com.ve",
        "linkPreview": False,
        "options": {
            "delay": 1200,
            "presence": "composing"
        }
    }
    resp = client.post("/message/sendText/Viki_LPGTEC", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert "key" in data
    assert "584161234567" in data["key"]["remoteJid"]
    assert "sovereign_dispatch" in data
    assert data["sovereign_dispatch"]["success"] is True


def test_n8n_facade_get_media_endpoint(client):
    """Verifica el endpoint de captura de media para N8N."""
    resp = client.post("/chat/getBase64FromMediaMessage/Viki_LPGTEC", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert "base64" in data

