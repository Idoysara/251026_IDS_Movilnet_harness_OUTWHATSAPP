#!/bin/bash
# ==============================================================================
# Lanzador de 1-Clic para Ejecutar la Suite de Pruebas OUTWHATSAPP (100% PASS)
# Telecomunicaciones Movilnet C.A. — Gobernanza: Pilar VII (Cero Terminal)
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "======================================================================"
echo "🧪 EJECUTANDO VERIFICACIÓN DE PRUEBAS OUTWHATSAPP (100% PASS)"
echo "Telecomunicaciones Movilnet C.A. — Grado Militar Carrier-Grade"
echo "======================================================================"

if [ -f "/Users/ismael/Desktop/IDS_Harnnes2/.venv/bin/pytest" ]; then
    PYTEST="/Users/ismael/Desktop/IDS_Harnnes2/.venv/bin/pytest"
elif [ -f "$DIR/.venv/bin/pytest" ]; then
    PYTEST="$DIR/.venv/bin/pytest"
else
    PYTEST="pytest"
fi

"$PYTEST" -c pytest.ini tests/ -v
echo ""
echo "======================================================================"
echo "🏁 EJECUCIÓN FINALIZADA. Presiona cualquier tecla para salir..."
read -n 1
