#!/bin/bash
# ==============================================================================
# Lanzador de 1-Clic para Iniciar el Microservicio OUTWHATSAPP (:8035)
# Telecomunicaciones Movilnet C.A. — Gobernanza: Pilar VII (Cero Terminal)
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "======================================================================"
echo "🚀 INICIANDO MICROSERVICIO SOBERANO OUTWHATSAPP (PUERTO :8035)"
echo "Telecomunicaciones Movilnet C.A. — Soberanía Libre de WhatsApp"
echo "======================================================================"

# Buscar interprete python disponible
if [ -f "/Users/ismael/Desktop/IDS_Harnnes2/.venv/bin/python" ]; then
    PY="/Users/ismael/Desktop/IDS_Harnnes2/.venv/bin/python"
elif [ -f "$DIR/.venv/bin/python" ]; then
    PY="$DIR/.venv/bin/python"
else
    PY="python3"
fi

echo "Usando intérprete: $PY"
"$PY" infrastructure/server.py --port 8035
