#!/bin/bash
# Lanzador de doble clic: vigila cambios de datos/código que dejan desactualizado el respaldo cifrado.
cd "$(dirname "$0")" || exit 1
PY=python3
[ -x /Users/ismael/Desktop/IDS_Harnnes2/.venv/bin/python3 ] && PY=/Users/ismael/Desktop/IDS_Harnnes2/.venv/bin/python3
echo "=== Monitor de respaldo IDS Movilnet ==="
"$PY" scripts/monitor_respaldo.py --check
echo
echo "Vigilando cada 60 s (Ctrl-C para salir)..."
"$PY" scripts/monitor_respaldo.py --watch 60
read -r -p "Presione Enter para cerrar..."
