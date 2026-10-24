#!/usr/bin/env python3
"""
Entrypoint Raíz Soberano para Render.com y Despliegue Cloud
Repositorio: https://github.com/Idoysara/251026_IDS_Movilnet_harness_OUTWHATSAPP
Permite desplegar directamente desde la raíz del repositorio en Render.com
sin necesidad de configurar subdirectorios manuales.
"""
import argparse
import os
import sys
from pathlib import Path

# Inyectar la ruta del módulo soberano OUTWHATSAPP en sys.path
REPO_ROOT = Path(__file__).resolve().parent
MODULO_DIR = REPO_ROOT / "231026_IDS_Movilnet" / "MODULO_OUTWHATSAPP"
if str(MODULO_DIR) not in sys.path:
    sys.path.insert(0, str(MODULO_DIR))

from outwhatsapp.infrastructure.server import app  # noqa: E402


def run_self_test() -> int:
    """Verifica que la aplicación FastAPI y sus rutas soberanas carguen correctamente."""
    routes = [getattr(r, "path", "") for r in app.routes]
    required = [
        "/",
        "/health",
        "/message/sendText/{instance}",
        "/api/v1/sovereign/trigger-n8n",
        "/api/v1/sovereign/recent-replies",
    ]
    for req in required:
        assert req in routes, f"Ruta crítica faltante: {req}"
    print("✅ Auto-test superado: Entrypoint raíz main.py y rutas FastAPI verificadas.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrypoint Raíz Render — Movilnet OUTWHATSAPP")
    parser.add_argument("--test", action="store_true", help="Ejecuta auto-verificación de rutas")
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Host de escucha (por defecto 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 8035)),
        help="Puerto HTTP (usa variable PORT en Render.com)",
    )
    args = parser.parse_args()

    if args.test:
        sys.exit(run_self_test())

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
