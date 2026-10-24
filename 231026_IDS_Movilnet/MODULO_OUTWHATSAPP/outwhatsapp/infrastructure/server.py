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

@app.get("/health", tags=["Monitoreo"])
def health_check():
    return {
        "status": "ONLINE",
        "service": "modulo_outwhatsapp",
        "port": 8035,
        "sovereign_mode": "ACTIVE",
        "whatsapp_dependency": "ERRADICADA"
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
    parser.add_argument("--port", type=int, default=8035, help="Puerto de escucha (default: 8035)")
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
