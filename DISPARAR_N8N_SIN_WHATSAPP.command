#!/bin/bash
# ==============================================================================
# LANZADOR DE 1-CLIC: PRUEBAS REALES MULTI-OPERADORA SIN WHATSAPP (N8N + RENDER)
# Soporta: Movilnet (0416/0426), Digitel (0412), Movistar (0414/0424), CANTV e Intl
# ==============================================================================
SCRIPT_PY="/Users/ismael/251026_IDS_Movilnet_harness_OUTWHATSAPP/241026_IDS_MOVILNET_HARNESS_OUTWHATSAPP/scripts/simular_disparo_n8n_v3.py"
RENDER_URL="https://two51026-ids-movilnet-harness-outwhatsapp.onrender.com"

clear
echo "======================================================================"
echo " 🛡️ MOVILNET 4GMAX — SIMULADOR MULTI-OPERADORA SIN WHATSAPP"
echo " 🌐 Servidor Cloud Render: $RENDER_URL"
echo " 🔗 Workflow N8N v3:       eqxjnKshsIeO1vgR"
echo "======================================================================"
echo ""
echo "Selecciona qué prueba deseas ejecutar:"
echo "  1) 🟠 Abonado Movilnet (0416-1234567) -> Consulta de Saldo"
echo "  2) 🟣 Usuario Digitel  (0412-3001155) -> Solicitud de Portabilidad eSIM"
echo "  3) 🔵 Usuario Movistar (0414-2554590) -> Planes y Portabilidad"
echo "  4) 🔵 Usuario Movistar (0424-1389058) -> Recarga C2P a Tercero Movilnet"
echo "  5) 🌐 Batería Automática de las 5 Operadoras (0416, 0412, 0414, 0424, 0212)"
echo "  6) ✍️  Ingresar manualmente CUALQUIER número y mensaje"
echo ""
read -p "Opción [1-6, Enter=5]: " OPCION
OPCION=${OPCION:-5}

case "$OPCION" in
  1)
    python3 "$SCRIPT_PY" --prod --msisdn "04161234567" --mensaje "Hola, deseo consultar mi saldo disponible" --server-url "$RENDER_URL"
    ;;
  2)
    python3 "$SCRIPT_PY" --prod --msisdn "04123001155" --mensaje "Hola, llamo desde Digitel 0412 y quiero Portabilidad a Movilnet" --server-url "$RENDER_URL"
    ;;
  3)
    python3 "$SCRIPT_PY" --prod --msisdn "04142554590" --mensaje "Hola, soy Movistar 0414, quiero ver planes y Portabilidad eSIM" --server-url "$RENDER_URL"
    ;;
  4)
    python3 "$SCRIPT_PY" --prod --msisdn "04241389058" --mensaje "Quiero recargar con Pago Movil C2P a un familiar Movilnet" --server-url "$RENDER_URL"
    ;;
  5)
    python3 "$SCRIPT_PY" --prod --multi-carrier --server-url "$RENDER_URL"
    ;;
  6)
    read -p "Escribe el número de cualquier operadora (ej. 04129998877): " NUM_CUSTOM
    read -p "Escribe la consulta o mensaje: " MSG_CUSTOM
    python3 "$SCRIPT_PY" --prod --msisdn "$NUM_CUSTOM" --mensaje "$MSG_CUSTOM" --server-url "$RENDER_URL"
    ;;
esac

echo ""
echo "👉 Abre la Consola en vivo para ver y escuchar las respuestas:"
echo "   $RENDER_URL"
echo ""
read -n 1 -s -r -p "Presiona cualquier tecla para cerrar..."
echo ""
