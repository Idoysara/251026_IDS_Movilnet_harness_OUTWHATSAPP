"""
Servidor Microservicio FastAPI y CLI Autónomo para OUTWHATSAPP (Puerto :8035).
Gobernanza: Universal Best Practices Engineering Rule (Pilares I y II).
"""
import os
import sys
import argparse
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Asegurar path de importación
MODULE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if MODULE_ROOT not in sys.path:
    sys.path.insert(0, MODULE_ROOT)

from outwhatsapp.domain.invariants import SovereignInvariantViolationError
from outwhatsapp.domain.fsm import IllegalDispatchStateTransitionError
from outwhatsapp.infrastructure.database import init_outwhatsapp_db
from outwhatsapp.infrastructure.routers.api import router as outwhatsapp_router

app = FastAPI(
    title="Movilnet OUTWHATSAPP Sovereign Core API",
    description="Motor de Despacho y Comunicación Soberana 100% Libre de WhatsApp (PWA Push, SMS SMPP v3.4 y Telegram WebApp)",
    version="1.0.0"
)

# CORS estricto
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8035", "http://127.0.0.1:8035", "http://localhost:3000", "http://localhost:8010"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Manejadores de excepciones de dominio
@app.exception_handler(SovereignInvariantViolationError)
async def invariant_handler(request: Request, exc: SovereignInvariantViolationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"success": False, "error_type": "SovereignInvariantViolation", "detail": str(exc)}
    )

@app.exception_handler(IllegalDispatchStateTransitionError)
async def fsm_handler(request: Request, exc: IllegalDispatchStateTransitionError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"success": False, "error_type": "IllegalDispatchFSMTransition", "detail": str(exc)}
    )

# Routers
app.include_router(outwhatsapp_router)

# Ring Buffer en memoria volátil (Pilar IV y VI: máximo 30 respuestas recientes)
_RECENT_REPLIES = []

@app.get("/health", tags=["Monitoreo"])
def health_check():
    return {
        "status": "ONLINE",
        "service": "modulo_outwhatsapp",
        "port": 8035,
        "sovereign_mode": "ACTIVE",
        "whatsapp_dependency": "ERRADICADA"
    }


@app.get("/api/v1/sovereign/recent-replies", tags=["Fachada Adaptadora N8N"])
def get_recent_replies():
    """Devuelve las últimas respuestas entregadas por n8n a este servidor Render."""
    return {"success": True, "count": len(_RECENT_REPLIES), "replies": _RECENT_REPLIES}


@app.get("/", tags=["Consola Soberana"])
def sovereign_web_console():
    """Consola Interactiva de Voz y Texto para pruebas en Render.com sin WhatsApp."""
    from fastapi.responses import HTMLResponse
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Movilnet 4GMAX — Consola Soberana OUTWHATSAPP (Render Cloud)</title>
  <style>
    :root { --bg: #0b1020; --card: #151e36; --accent: #ff6600; --text: #f0f4ff; --muted: #94a3b8; --ok: #10b981; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; }
    .container { max-width: 820px; margin: 0 auto; }
    .header { display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid var(--accent); padding-bottom: 16px; margin-bottom: 24px; }
    .badge { background: rgba(16,185,129,0.18); color: var(--ok); border: 1px solid var(--ok); padding: 6px 12px; border-radius: 999px; font-size: 13px; font-weight: 700; }
    .card { background: var(--card); border-radius: 14px; padding: 20px; margin-bottom: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.35); }
    label { display: block; font-size: 13px; color: var(--muted); margin-bottom: 6px; font-weight: 600; }
    input, select, textarea { width: 100%; box-sizing: border-box; background: #0d1428; border: 1px solid #2e3c64; color: var(--text); padding: 12px; border-radius: 8px; font-size: 15px; margin-bottom: 14px; }
    .btn-row { display: flex; gap: 12px; flex-wrap: wrap; }
    button { cursor: pointer; border: none; border-radius: 8px; padding: 12px 20px; font-size: 15px; font-weight: 700; transition: opacity 0.2s; }
    button:hover { opacity: 0.9; }
    .btn-primary { background: var(--accent); color: #fff; flex: 1; }
    .btn-voice { background: #2563eb; color: #fff; }
    .reply-box { background: #0d1428; border-left: 4px solid var(--accent); padding: 14px; border-radius: 8px; margin-top: 12px; white-space: pre-wrap; font-size: 14px; }
    .meta { font-size: 12px; color: var(--muted); margin-bottom: 6px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <h1 style="margin:0;font-size:22px;">🛡️ Movilnet 4GMAX — Sistema Soberano OUTWHATSAPP</h1>
        <p style="margin:4px 0 0;color:var(--muted);font-size:14px;">Pasarela Nube Render.com ⟷ n8n v3 (0% Dependencia de WhatsApp / Meta)</p>
      </div>
      <span class="badge">● ONLINE (SIN WHATSAPP)</span>
    </div>

    <div class="card">
      <h3 style="margin-top:0;">📞 1. Simulador de Llamada / Mensaje al Número Máster (00584241533712)</h3>
      <label>Número del Abonado (MSISDN):</label>
      <input id="msisdn" type="text" value="04161234567" />

      <label>Modo del Webhook de n8n (`eqxjnKshsIeO1vgR`):</label>
      <select id="mode">
        <option value="prod">PRODUCCIÓN (Workflow en Active: /webhook/c8fff181...)</option>
        <option value="test">TEST (Con botón 'Execute workflow' activo: /webhook-test/c8fff181...)</option>
      </select>

      <label>Consulta de Voz o Texto:</label>
      <textarea id="mensaje" rows="3">Hola, deseo consultar mi saldo disponible y ver las superofertas de hoy</textarea>

      <div class="btn-row">
        <button class="btn-voice" type="button" onclick="iniciarDictadoVoz()">🎙️ Hablar por Micrófono (STT)</button>
        <button class="btn-primary" type="button" onclick="dispararN8N()">🚀 Enviar a n8n sin WhatsApp</button>
      </div>
      <p id="statusMsg" style="font-size:13px;color:var(--muted);margin:10px 0 0;"></p>
    </div>

    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <h3 style="margin:0;">📥 2. Respuestas Recibidas desde n8n (`POST /message/sendText`)</h3>
        <button style="background:#334155;color:#fff;padding:8px 14px;font-size:13px;" onclick="cargarRespuestas(true)">🔄 Actualizar</button>
      </div>
      <div id="repliesContainer">
        <p style="color:var(--muted);font-size:14px;">Esperando respuestas de n8n...</p>
      </div>
    </div>
  </div>

  <script>
    let lastCount = 0;
    function hablarTexto(texto) {
      if (!('speechSynthesis' in window) || !texto) return;
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(texto);
      u.lang = 'es-VE';
      u.rate = 1.02;
      window.speechSynthesis.speak(u);
    }

    function iniciarDictadoVoz() {
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) { alert("Usa Chrome o Safari para dictado por voz."); return; }
      const rec = new SR();
      rec.lang = 'es-VE';
      document.getElementById('statusMsg').innerText = "🎙️ Escuchando tu voz... habla ahora.";
      rec.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        document.getElementById('mensaje').value = transcript;
        document.getElementById('statusMsg').innerText = "✅ Voz transcrita: " + transcript;
      };
      rec.start();
    }

    async function dispararN8N() {
      const msisdn = document.getElementById('msisdn').value;
      const mensaje = document.getElementById('mensaje').value;
      const mode = document.getElementById('mode').value;
      document.getElementById('statusMsg').innerText = "⏳ Enviando evento soberano a n8n...";
      try {
        const r = await fetch('/api/v1/sovereign/trigger-n8n', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({msisdn, mensaje, mode})
        });
        const data = await r.json();
        if (data.success) {
          document.getElementById('statusMsg').innerText = "✅ Entregado a n8n. Esperando respuesta en callback (" + data.callback_server_url + ")...";
          setTimeout(() => cargarRespuestas(true), 2000);
        } else {
          document.getElementById('statusMsg').innerText = "⚠️ Aviso n8n: " + (data.error || JSON.stringify(data));
        }
      } catch (err) {
        document.getElementById('statusMsg').innerText = "❌ Error de red: " + err;
      }
    }

    async function cargarRespuestas(speakLatest) {
      try {
        const r = await fetch('/api/v1/sovereign/recent-replies');
        const data = await r.json();
        const cont = document.getElementById('repliesContainer');
        if (!data.replies || data.replies.length === 0) return;
        cont.innerHTML = data.replies.map((item, idx) => `
          <div class="reply-box">
            <div class="meta">📱 Abonado: <b>${item.number}</b> | 🕒 ${item.timestamp} | Canal: ${item.channel}</div>
            <div>${item.text}</div>
            <div style="margin-top:10px;display:flex;gap:10px;flex-wrap:wrap;">
              <button style="background:#10b981;color:#fff;padding:6px 12px;font-size:12px;" onclick="hablarTexto(${JSON.stringify(item.tts_spoken_text)})">🔊 Escuchar Voz Limpia (TTS)</button>
              ${item.extracted_pwa_url ? `<a href="${item.extracted_pwa_url}" target="_blank" style="background:#ff6600;color:#fff;padding:6px 12px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:700;">🌐 Abrir Portal PWA 4GMAX</a>` : ''}
            </div>
          </div>
        `).join('');
        if (speakLatest && data.replies.length > lastCount) {
          lastCount = data.replies.length;
          hablarTexto(data.replies[0].tts_spoken_text);
        }
      } catch (e) {}
    }
    setInterval(() => cargarRespuestas(true), 4000);
    cargarRespuestas(false);
  </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


# ==============================================================================
# ENDPOINTS FACHADA ADAPTADORA N8N (Sustitución Transparente de Evolution/WhatsApp)
# ==============================================================================
@app.post("/message/sendText/{instance}", tags=["Fachada Adaptadora N8N"])
async def n8n_facade_send_text(instance: str, request: Request):
    """
    Endpoint Fachada Transparente para n8n (Sustitución de Evolution API / WhatsApp).
    Recibe la respuesta final procesada por n8n, separa el texto limpio para Voz (TTS)
    del enlace visual (PWA), y despacha soberanamente por PWA Push o SMS SMPP.
    """
    import time
    import re
    from datetime import datetime
    try:
        body = await request.json()
    except Exception:
        body = {}

    number = str(body.get("number", "")).strip()
    text = str(body.get("text", "")).strip()

    # Filtro Divisor Multimodal (Split-Channel Filter: Voz TTS vs Enlace Visual)
    urls_found = re.findall(r"https?://\S+", text)
    extracted_pwa_url = urls_found[0] if urls_found else ""

    # Eliminar bloque de portal PWA, URLs, asteriscos y viñetas para lectura fluida de Voz (TTS)
    tts_clean = re.sub(r"🌐\s*\*?Portal PWA.*$", "", text, flags=re.DOTALL | re.IGNORECASE)
    tts_clean = re.sub(r"https?://\S+", "", tts_clean)
    tts_clean = re.sub(r"[\*`_~👉🌐📶🚀✨💰📋🎯🎁💵•]", "", tts_clean)
    tts_clean = re.sub(r"\s+", " ", tts_clean).strip()

    from outwhatsapp.infrastructure.routers.api import _dispatcher
    res = _dispatcher.despachar(
        msisdn=number,
        titulo="Movilnet 4GMAX",
        mensaje=text
    )

    # Guardar en Ring Buffer para visualización y lectura de voz en tiempo real en Render
    _RECENT_REPLIES.insert(0, {
        "number": number,
        "text": text,
        "tts_spoken_text": tts_clean,
        "extracted_pwa_url": extracted_pwa_url,
        "channel": res.channel_used.value,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    if len(_RECENT_REPLIES) > 30:
        _RECENT_REPLIES.pop()

    return {
        "status": "SUCCESS",
        "key": {
            "remoteJid": f"{number}@s.whatsapp.net",
            "fromMe": True,
            "id": f"SOV-{int(time.time()*1000)}"
        },
        "message": {
            "conversation": text
        },
        "messageTimestamp": int(time.time()),
        "sovereign_dispatch": {
            "channel": res.channel_used.value,
            "latency_ms": res.latency_ms,
            "success": res.success,
            "tts_spoken_text": tts_clean,
            "extracted_pwa_url": extracted_pwa_url
        }
    }


@app.post("/chat/getBase64FromMediaMessage/{instance}", tags=["Fachada Adaptadora N8N"])
async def n8n_facade_get_media(instance: str, request: Request):
    """Endpoint Fachada para solicitudes de media de n8n."""
    return {"base64": ""}


@app.post("/api/v1/sovereign/trigger-n8n", tags=["Fachada Adaptadora N8N"])
async def trigger_n8n_cloud_bridge(request: Request):
    """
    Puente Nube para Render.com: Recibe un evento de llamada de voz transcrita o mensaje desde la PWA/SIP,
    lo empaqueta con la Fachada Soberana (respetando Edge Carrier Firewall) y lo dispara hacia n8n v3.
    """
    import time
    import json
    import urllib.request
    import urllib.error

    try:
        body = await request.json()
    except Exception:
        body = {}

    msisdn = str(body.get("msisdn", "04161234567")).strip()
    mensaje = str(body.get("mensaje", "Consulta de saldo y promociones")).strip()
    mode = str(body.get("mode", "prod")).lower()

    # Determinar la URL pública de este servidor (en Render.com o local) para que n8n responda aquí
    default_base = str(request.base_url).rstrip("/")
    server_url = str(body.get("server_url") or os.environ.get("RENDER_EXTERNAL_URL") or default_base)

    clean_num = msisdn.replace("+", "").replace("-", "").replace(".", "").replace(" ", "")
    if clean_num.startswith("04") and len(clean_num) == 11:
        clean_num = "58" + clean_num[1:]
    elif not clean_num.startswith("58") and len(clean_num) == 10:
        clean_num = "58" + clean_num

    n8n_payload = {
        "event": "messages.upsert",
        "server_url": server_url,
        "instance": "Viki_LPGTEC",
        "apikey": "MOVILNET_SOVEREIGN_KEY_2026",
        "data": {
            "key": {
                "remoteJid": f"{clean_num}@s.whatsapp.net",
                "fromMe": False,
                "id": f"SOV-RENDER-{int(time.time()*1000)}"
            },
            "pushName": str(body.get("pushName", "Abonado Movilnet")),
            "message": {
                "conversation": mensaje
            },
            "messageType": "conversation"
        }
    }

    webhook_url = (
        os.environ.get("N8N_WEBHOOK_TEST_URL", "https://n8n.lpgtec.net/webhook-test/c8fff181-13b7-4514-9d4b-4612b5cd93e8")
        if mode == "test"
        else os.environ.get("N8N_WEBHOOK_PROD_URL", "https://n8n.lpgtec.net/webhook/c8fff181-13b7-4514-9d4b-4612b5cd93e8")
    )

    data_bytes = json.dumps(n8n_payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data_bytes,
        headers={"Content-Type": "application/json", "User-Agent": "Movilnet-Render-Bridge/3.0"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp_body = resp.read().decode("utf-8")
            return {
                "success": True,
                "n8n_status": resp.getcode(),
                "webhook_used": webhook_url,
                "callback_server_url": server_url,
                "n8n_response": resp_body
            }
    except Exception as exc:
        return {
            "success": False,
            "webhook_used": webhook_url,
            "callback_server_url": server_url,
            "error": str(exc)
        }


def ejecutar_auto_test() -> bool:
    """Auto-verificación matemática y funcional autónoma (Pilar II)."""
    print("=" * 70)
    print("🔍 INICIANDO AUTO-TEST AUTÓNOMO DE OUTWHATSAPP (Pilar II)")
    print("=" * 70)

    # 1. Test DDL
    print("[1/4] Inicializando base de datos SQLite WAL...")
    assert init_outwhatsapp_db(), "Fallo al inicializar base de datos"
    print("  -> Base de datos inicializada OK.")

    # 2. Test Invariantes
    print("[2/4] Validando invariantes de dominio...")
    from outwhatsapp.domain.invariants import SovereignInvariants
    norm = SovereignInvariants.validar_msisdn_movilnet("0416-123.45.67")
    assert norm == "004161234567" or norm == "04161234567", f"Normalización errónea: {norm}"
    try:
        SovereignInvariants.validar_msisdn_movilnet("0414-9999999")  # Movistar debe fallar
        assert False, "Debió rechazar prefijo 0414"
    except SovereignInvariantViolationError:
        pass
    print("  -> Invariantes validadas OK.")

    # 3. Test SMPP PDU Codec
    print("[3/4] Validando codificación binaria SMPP v3.4...")
    from outwhatsapp.application.smpp_gateway import SMPPPduCodec, SMPPMessage
    msg = SMPPMessage(
        source_addr="MOVILNET",
        dest_addr="04161234567",
        short_message="Tu recarga ha sido exitosa.",
        sequence_number=101
    )
    pdu = SMPPPduCodec.encode_submit_sm(msg)
    assert len(pdu) >= 16, "PDU SMPP demasiado corta"
    total_len, cmd_id, stat, seq = SMPPPduCodec.decode_header(pdu[:16])
    assert cmd_id == 0x00000004, f"Command ID SMPP erróneo: {cmd_id}"
    assert seq == 101, f"Número de secuencia erróneo: {seq}"
    print("  -> Codificación binaria SMPP OK.")

    # 4. Test Orquestador Soberano
    print("[4/4] Validando despacho omnicanal soberano...")
    from outwhatsapp.application.sovereign_dispatcher import SovereignDispatcher
    dispatcher = SovereignDispatcher()
    res = dispatcher.despachar(
        msisdn="04161234567",
        titulo="Alerta Movilnet",
        mensaje="Tu plan 4GMAX fue renovado con éxito."
    )
    assert res.success, "Fallo en despacho soberano"
    assert res.latency_ms < 50.0, f"Latencia excesiva: {res.latency_ms}ms"
    print(f"  -> Despacho completado en {res.latency_ms:.2f}ms por canal {res.channel_used.value} OK.")

    print("=" * 70)
    print("✅ 100% AUTO-TEST SUPERADO CON ÉXITO — OUTWHATSAPP CERTIFICADO")
    print("=" * 70)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Microservicio Soberano OUTWHATSAPP")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8035)), help="Puerto de escucha (default: PORT env o 8035)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host de enlace")
    parser.add_argument("--test", action="store_true", help="Ejecutar suite de auto-verificación y salir")
    parser.add_argument("--demo", action="store_true", help="Demostración de despacho interactivo")

    args = parser.parse_args()

    if args.test:
        exito = ejecutar_auto_test()
        sys.exit(0 if exito else 1)

    if args.demo:
        ejecutar_auto_test()
        from outwhatsapp.application.sovereign_dispatcher import SovereignDispatcher
        d = SovereignDispatcher()
        link = d.generar_magic_link("04161234567")
        print("\n🎉 DEMO DE ENLACE MAGIC LINK GENERADO:")
        print(link)
        sys.exit(0)

    import uvicorn
    init_outwhatsapp_db()
    print(f"🚀 Iniciando Servidor OUTWHATSAPP en http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
