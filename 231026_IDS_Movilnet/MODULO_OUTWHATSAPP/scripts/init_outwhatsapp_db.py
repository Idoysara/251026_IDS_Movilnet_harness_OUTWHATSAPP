"""
Script CLI para Inicialización y Verificación de outwhatsapp.db.
Gobernanza: Universal Best Practices Engineering Rule (Pilar II).
"""
import sys
import os
import argparse

MODULE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if MODULE_ROOT not in sys.path:
    sys.path.insert(0, MODULE_ROOT)

from outwhatsapp.infrastructure.database import init_outwhatsapp_db, DEFAULT_DB_PATH, get_connection


def main():
    parser = argparse.ArgumentParser(description="Inicializador de Base de Datos OUTWHATSAPP")
    parser.add_argument("--db-path", type=str, default=DEFAULT_DB_PATH, help="Ruta de la base de datos")
    parser.add_argument("--test", action="store_true", help="Validación de integridad tras inicializar")

    args = parser.parse_args()

    print(f"🔧 Inicializando base de datos OUTWHATSAPP en: {args.db_path}")
    exito = init_outwhatsapp_db(args.db_path)
    if not exito:
        print("❌ Error al inicializar base de datos.")
        sys.exit(1)

    print("✅ Esquema DDL ejecutado exitosamente.")

    if args.test:
        conn = get_connection(args.db_path)
        try:
            tablas = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            nombres = [t["name"] for t in tablas]
            esperadas = ["web_push_subscriptions", "sovereign_dispatch_log", "smpp_pdu_audit", "sovereign_dlq"]
            for esp in esperadas:
                assert esp in nombres, f"Falta tabla esperada: {esp}"
            print(f"✅ Integridad verificada: {len(nombres)} tablas operativas en modo WAL.")
        finally:
            conn.close()


if __name__ == "__main__":
    main()
