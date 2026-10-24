#!/bin/bash
# ==============================================================================
# Lanzador de 1-Clic para Disparar el Flujo N8N v3 Sin WhatsApp
# Telecomunicaciones Movilnet C.A. — Gobernanza: Pilar VII (Cero Terminal)
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "======================================================================"
echo "🚀 DISPARADOR SOBERANO N8N v3 (SIN WHATSAPP)"
echo "Workflow: Viki_LPGTEC_v3_ids_Movilnet_Google_Suite_Full copy"
echo "======================================================================"
echo ""
echo "Selecciona el modo de ejecución:"
echo "1) Modo TEST (requiere presionar 'Execute workflow' en N8N antes)"
echo "2) Modo PRODUCCIÓN (si el workflow ya está en 'Active')"
echo ""
read -p "Ingresa tu opción (1 o 2, default: 1): " OPCION

if [ "$OPCION" == "2" ]; then
    python3 scripts/simular_disparo_n8n_v3.py --prod
else
    python3 scripts/simular_disparo_n8n_v3.py
fi

echo ""
echo "======================================================================"
echo "🏁 Ejecución finalizada. Presiona cualquier tecla para cerrar..."
read -n 1
