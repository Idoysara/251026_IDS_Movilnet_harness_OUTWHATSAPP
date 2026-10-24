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
    parser = argparse.ArgumentParser(description="Disparador Soberano Multi-Operadora N8N v3 (Sin WhatsApp)")
    parser.add_argument("--msisdn", default="04161234567", help="Número de teléfono (0416, 0426, 0414, 0424, 0412, 0212 o Intl)")
    parser.add_argument("--mensaje", default="Consultar saldo y promociones", help="Mensaje del usuario")
    parser.add_argument("--prod", action="store_true", help="Usar webhook de producción en vez del webhook-test")
    parser.add_argument("--url", default=None, help="Sobrescribir URL del webhook de N8N")
    parser.add_argument(
        "--server-url",
        default="https://two51026-ids-movilnet-harness-outwhatsapp.onrender.com",
        help="URL del servidor OUTWHATSAPP receptor (por defecto: Render Cloud)"
    )
    parser.add_argument("--multi-carrier", action="store_true", help="Ejecutar batería de pruebas desde las 5 operadoras")
    parser.add_argument("--test", action="store_true", help="Auto-verificación matemática del payload")

    args = parser.parse_args()

    if args.test:
        print("🔍 Verificando construcción del payload soberano multi-operadora...")
        p1 = construir_payload_soberano("0416-999.88.77", "Test de saldo", server_url="http://127.0.0.1:8035")
        assert p1["server_url"] == "http://127.0.0.1:8035"
        assert p1["data"]["key"]["remoteJid"] == "584169998877@s.whatsapp.net"
        p2 = construir_payload_soberano("0412-300.11.55", "Portabilidad Digitel")
        assert p2["data"]["key"]["remoteJid"] == "584123001155@s.whatsapp.net"
        p3 = construir_payload_soberano("0414-255.45.90", "Portabilidad Movistar")
        assert p3["data"]["key"]["remoteJid"] == "584142554590@s.whatsapp.net"
        print("✅ Auto-test superado: Payload generado cumple con el Patrón Fachada para todas las operadoras.")
        sys.exit(0)

    url_target = args.url or (PROD_WEBHOOK_URL if args.prod else TEST_WEBHOOK_URL)

    if args.multi_carrier:
        casos = [
            ("MOVILNET (0416)", "04161234567", "Hola, deseo consultar mi saldo disponible"),
            ("DIGITEL (0412)", "04123001155", "Hola, llamo desde Digitel 0412 y quiero Portabilidad a Movilnet"),
            ("MOVISTAR (0414)", "04142554590", "Hola, soy Movistar 0414, quiero ver planes y Portabilidad eSIM"),
            ("MOVISTAR (0424)", "04241389058", "Quiero hacer una recarga C2P a un familiar Movilnet"),
            ("CANTV FIJO (0212)", "02125551234", "Buenas tardes, consulta de planes desde teléfono fijo CANTV"),
        ]
        print("=" * 70)
        print("🌐 BATERÍA MULTI-OPERADORA HACIA N8N v3 + RENDER CLOUD")
        print(f"Webhook N8N: {url_target}")
        print(f"Callback Render: {args.server_url}")
        print("=" * 70)
        for label, num, msg in casos:
            payload = construir_payload_soberano(msisdn=num, mensaje=msg, server_url=args.server_url)
            res = disparar_webhook(url_target, payload)
            print(f"[{label}] Número: {num} -> HTTP {res.get('status_code')} | OK={res.get('success')}")
        sys.exit(0)

    payload = construir_payload_soberano(
        msisdn=args.msisdn,
        mensaje=args.mensaje,
        server_url=args.server_url
    )

    print("=" * 70)
    print("🚀 DISPARANDO WEBHOOK N8N v3 (SIN WHATSAPP)")
    print(f"Destino:    {url_target}")
    print(f"Usuario:    {args.msisdn}")
    print(f"Mensaje:    {args.mensaje}")
    print(f"server_url: {args.server_url} (Respuesta irá a Render / OUTWHATSAPP)")
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
