"""
Script Autónomo de Verificación de Integridad de Harness² y Pureza AST.
Telecomunicaciones Movilnet C.A. — Gobernanza: Pilar II & Invariante III.
"""
import os
import sys
import ast
import argparse
from pathlib import Path


def audit_ast_directory(target_dir: str) -> int:
    """Audita la pureza sintáctica de todos los archivos Python."""
    errors = 0
    scanned = 0
    for root, dirs, files in os.walk(target_dir):
        if any(p in root for p in ['.pytest_cache', '__pycache__', '.git']):
            continue
        for f in files:
            if f.endswith('.py'):
                scanned += 1
                p = os.path.join(root, f)
                try:
                    with open(p, 'r', encoding='utf-8') as fp:
                        content = fp.read()
                    ast.parse(content, filename=p)
                except SyntaxError as e:
                    print(f"❌ SyntaxError en {p}: {e}")
                    errors += 1
    print(f"✅ AST Audit completado: {scanned} archivos analizados, {errors} errores sintácticos.")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Verificador de Integridad de Harness2")
    parser.add_argument("--test", action="store_true", help="Ejecutar autoverificación completa")
    parser.add_argument("--audit-ast", action="store_true", help="Auditar sintaxis AST")

    args = parser.parse_args()
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    print("=" * 70)
    print("🔍 VERIFICADOR DE INTEGRIDAD HARNESS² — IDS_MOVILNET (v4.50.0)")
    print(f"Directorio de Trabajo: {workspace}")
    print("=" * 70)

    errs = audit_ast_directory(workspace)
    assert errs == 0, f"Se detectaron {errs} errores de sintaxis AST en el espacio de trabajo"

    print("✅ Todos los archivos de script satisfacen el Invariante III de Pureza AST.")
    print("=" * 70)


if __name__ == "__main__":
    main()
