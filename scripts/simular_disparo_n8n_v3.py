"""
Script Autónomo para Simular y Ejecutar el Flujo N8N v3 sin WhatsApp.
Telecomunicaciones Movilnet C.A. — Gobernanza: Pilares I, II y VII.
Workflow: Viki_LPGTEC_v3_ids_Movilnet_Google_Suite_Full copy
"""
import sys
import json
import argparse
import urllib.request
import urllib.error

TEST_WEBHOOK_URL = "https://n8n.lpgtec.net/webhook-test/c8fff181-13b7-4514-9d4b-4612b5cd93e8"
PROD_WEBHOOK_URL = "https://n8n.lpgtec.net/webhook/c8fff181-13b7-4514-9d4b-4612b5cd93e8"


def construir_payload_soberano(
    msisdn: str = "584161234567",
    mensaje: str = "Hola, deseo consultar mi saldo y ver las ofertas de hoy",
    server_url: str = "http://127.0.0.1:8035",
    instance: str = "Movilnet_Sovereign"
) -> dict:
    """
    Construye el payload con el Patrón Fachada Adaptadora Transparente.
    Inyecta server_url para que N8N devuelva la respuesta a OUTWHATSAPP sin usar WhatsApp.
    """
    clean_num = msisdn.replace("+", "").replace("-", "").replace(".", "")
    if clean_num.startswith("04") and len(clean_num) == 11:
        clean_num = "58" + clean_num[1:]
    elif not clean_num.startswith("58") and len(clean_num) == 10:
        clean_num = "58" + clean_num

    return {
        "event": "messages.upsert",
        "server_url": server_url,
        "instance": instance,
        "apikey": "MOVILNET_SOVEREIGN_KEY_2026",
        "data": {
            "key": {
                "remoteJid": f"{clean_num}@s.whatsapp.net",
                "fromMe": False,
                "id": "SIM_TRIGGER_SOV_001"
            },
            "pushName": "Abonado Movilnet",
            "message": {
                "conversation": mensaje
            },
            "messageType": "conversation"
        }
    }


def disparar_webhook(url: str, payload: dict, timeout: int = 15) -> dict:
    """Envía el webhook a N8N mediante HTTP POST."""
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Movilnet-Sovereign-Trigger/3.0"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            body = response.read().decode("utf-8")
            return {
                "status_code": status_code,
                "success": status_code in (200, 201),
                "response": body
            }
    except urllib.error.HTTPError as e:
        return {
            "status_code": e.code,
            "success": False,
            "error": e.read().decode("utf-8")
        }
    except Exception as e:
        return {
            "status_code": 0,
            "success": False,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Disparador Soberano N8N v3 (Sin WhatsApp)")
    parser.add_argument("--msisdn", default="04161234567", help="Número de teléfono Movilnet")
    parser.add_argument("--mensaje", default="Consultar saldo y promociones", help="Mensaje del abonado")
    parser.add_argument("--prod", action="store_true", help="Usar webhook de producción en vez del webhook-test")
    parser.add_argument("--url", default=None, help="Sobrescribir URL del webhook de N8N")
    parser.add_argument("--server-url", default="http://127.0.0.1:8035", help="URL del microservicio OUTWHATSAPP")
    parser.add_argument("--test", action="store_true", help="Auto-verificación matemática del payload")

    args = parser.parse_args()

    if args.test:
        print("🔍 Verificando construcción del payload soberano...")
        p = construir_payload_soberano("0416-999.88.77", "Test de saldo")
        assert p["server_url"] == "http://127.0.0.1:8035"
        assert p["data"]["key"]["remoteJid"] == "584169998877@s.whatsapp.net"
        print("✅ Auto-test superado: Payload generado cumple con el Patrón Fachada.")
        sys.exit(0)

    url_target = args.url or (PROD_WEBHOOK_URL if args.prod else TEST_WEBHOOK_URL)
    payload = construir_payload_soberano(
        msisdn=args.msisdn,
        mensaje=args.mensaje,
        server_url=args.server_url
    )

    print("=" * 70)
    print("🚀 DISPARANDO WEBHOOK N8N v3 (SIN WHATSAPP)")
    print(f"Destino:    {url_target}")
    print(f"Abonado:    {args.msisdn}")
    print(f"Mensaje:    {args.mensaje}")
    print(f"server_url: {args.server_url} (Respuesta irá a OUTWHATSAPP :8035)")
    print("=" * 70)
    print("Payload JSON:")
    print(json.dumps(payload, indent=2))
    print("=" * 70)

    res = disparar_webhook(url_target, payload)
    print(f"Resultado HTTP: {res.get('status_code')}")
    if res.get("success"):
        print("✅ Webhook entregado exitosamente a N8N.")
        print("Respuesta:", res.get("response"))
    else:
        print("⚠️ Advertencia o Error al conectar con N8N:")
        print("Detalle:", res.get("error"))
        print("\n💡 Recuerda:")
        print("1. Si usas 'webhook-test', debes presionar primero 'Execute workflow' en el panel de n8n.")
        print("2. Si el workflow ya está 'Active', ejecuta con el parámetro '--prod'.")


if __name__ == "__main__":
    main()
