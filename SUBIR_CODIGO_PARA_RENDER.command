#!/bin/bash
# ==============================================================================
# LANZADOR DE 1-CLIC: SINCRONIZAR CÓDIGO A GITHUB PARA RENDER.COM
# Proyecto: Sistema Soberano Movilnet OUTWHATSAPP
# Cuenta Render Destino: Shioishi Sara (shioishisara@gmail.com)
# ==============================================================================
set -e

REPO_DIR="/Users/ismael/251026_IDS_Movilnet_harness_OUTWHATSAPP/241026_IDS_MOVILNET_HARNESS_OUTWHATSAPP"

echo "======================================================================"
echo " 🚀 SUBIENDO CÓDIGO SOBERANO A GITHUB PARA RENDER.COM"
echo " 📁 Repositorio: $REPO_DIR"
echo " 🌐 Destino Git: https://github.com/Idoysara/251026_IDS_Movilnet_harness_OUTWHATSAPP"
echo "======================================================================"

cd "$REPO_DIR"

# Asegurar que los archivos clave estén agregados y confirmados
git add render.yaml \
        231026_IDS_Movilnet/MODULO_OUTWHATSAPP/outwhatsapp/infrastructure/server.py \
        scripts/simular_disparo_n8n_v3.py \
        BITACORA_SISTEMA_SOBERANO_OUTWHATSAPP.md \
        DOCUMENTO_ARQUITECTURA_Y_CONFIGURACION_SISTEMA_SOBERANO_OUTWHATSAPP.md \
        EVALUACION_FORENSE_Y_VIABILIDAD_PROMPT_SUPERAPP_N8N_V3.md \
        DISPARAR_N8N_SIN_WHATSAPP.command 2>/dev/null || true

if ! git diff --cached --quiet; then
    git commit -m "feat(render-cloud): add Render blueprint, voice/text sovereign console and n8n v3 bridge"
    echo "✅ Commit local generado exitosamente."
else
    echo "ℹ️ El commit local ya estaba preparado."
fi

echo "⏳ Enviando cambios a GitHub (git push origin main)..."
git push origin main

echo ""
echo "======================================================================"
echo " ✅ ¡CÓDIGO ACTUALIZADO EN GITHUB CON ÉXITO!"
echo " 👉 Ahora ve a tu pantalla de Render.com (shioishisara@gmail.com)"
echo "    y despliega desde: https://github.com/Idoysara/251026_IDS_Movilnet_harness_OUTWHATSAPP"
echo "======================================================================"
read -n 1 -s -r -p "Presiona cualquier tecla para cerrar esta ventana..."
echo ""
