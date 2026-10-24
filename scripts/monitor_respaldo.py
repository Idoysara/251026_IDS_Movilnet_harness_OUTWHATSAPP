#!/usr/bin/env python3
"""Monitor de cambios del respaldo cifrado y del repositorio publico (IDS Movilnet).

Detecta que el respaldo cifrado de datos quedo desactualizado:
  * DATOS  : archivos ignorados por git (bases de datos, .env, secretos, exportes, logs)
             que fueron agregados, modificados o eliminados desde la linea base.
  * CODIGO : archivos versionados con cambios sin commit y commits sin push al repo publico.

Zero-PII: el manifiesto guarda solo ruta relativa, tamano, mtime y SHA-256. Nunca contenido.
Solo biblioteca estandar (Python >= 3.9).

Uso:
  python3 scripts/monitor_respaldo.py --baseline          # crea la linea base (tras respaldar)
  python3 scripts/monitor_respaldo.py --check             # exit 0 sin cambios, 1 con cambios, 2 error
  python3 scripts/monitor_respaldo.py --watch 60          # vigila cada 60 s y notifica en macOS
  python3 scripts/monitor_respaldo.py --test              # autoverificacion
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import logging.handlers
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

MANIFEST_VERSION = 1
HASH_CHUNK = 1024 * 1024
REPORT_LIMIT_CHARS = 2000  # Invariante II de Harness2: elision de salidas largas
PATHS_PER_CATEGORY = 12
DEFAULT_BACKUP_DIR = Path.home() / "Backups_IDS_Movilnet_Cifrados"
DEFAULT_MANIFEST = DEFAULT_BACKUP_DIR / "manifest_respaldo.json"
DEFAULT_LOG = DEFAULT_BACKUP_DIR / "monitor_respaldo.log"

EXCLUDED_DIR_NAMES = frozenset({".venv", "venv", "__pycache__", ".pytest_cache", ".cache", "node_modules"})
EXCLUDED_PREFIXES = ("231026_IDS_Movilnet/I231026_IDS_Movilnet_Harness2/",)
EXCLUDED_SEGMENTS = ("/_ARCHIVO_DUPLICADOS_181026/",)

EXIT_OK, EXIT_CHANGES, EXIT_ERROR = 0, 1, 2

log = logging.getLogger("monitor_respaldo")


class MonitorError(Exception):
    """Error operativo del monitor (git ausente, manifiesto corrupto, etc.)."""


# --------------------------------------------------------------------------- dominio
@dataclass(frozen=True)
class FileRecord:
    size: int
    mtime_ns: int
    sha256: str


@dataclass
class ChangeSet:
    added: List[str] = field(default_factory=list)
    modified: List[str] = field(default_factory=list)
    deleted: List[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not (self.added or self.modified or self.deleted)

    @property
    def total(self) -> int:
        return len(self.added) + len(self.modified) + len(self.deleted)

    def signature(self) -> str:
        """Huella estable del conjunto de cambios (evita notificar lo mismo dos veces)."""
        joined = "|".join(["A:" + p for p in self.added] + ["M:" + p for p in self.modified] + ["D:" + p for p in self.deleted])
        return hashlib.sha256(joined.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CodeStatus:
    dirty_files: Tuple[str, ...]
    unpushed_commits: Optional[int]  # None = sin rama remota configurada


def is_excluded(rel: str) -> bool:
    """Misma regla que se uso al generar el respaldo cifrado."""
    norm = rel.replace("\\", "/")
    parts = norm.split("/")
    if any(p in EXCLUDED_DIR_NAMES for p in parts[:-1]):
        return True
    if parts[-1] == ".DS_Store" or norm.endswith(".pyc"):
        return True
    if norm.startswith(EXCLUDED_PREFIXES):
        return True
    return any(seg in "/" + norm for seg in EXCLUDED_SEGMENTS)


def diff_manifests(old: Dict[str, FileRecord], new: Dict[str, FileRecord]) -> ChangeSet:
    added = sorted(p for p in new if p not in old)
    deleted = sorted(p for p in old if p not in new)
    modified = sorted(p for p in new if p in old and new[p].sha256 != old[p].sha256)
    return ChangeSet(added=added, modified=modified, deleted=deleted)


def elide(text: str, limit: int = REPORT_LIMIT_CHARS) -> str:
    if len(text) <= limit:
        return text
    head, tail = 500, limit - 500 - 80
    omitted = len(text) - head - tail
    return f"{text[:head]}\n...[{omitted} caracteres omitidos]...\n{text[-tail:]}"


def render_report(changes: ChangeSet, code: CodeStatus) -> str:
    lines: List[str] = []
    lines.append("DATOS (respaldo cifrado): " + ("sin cambios" if changes.is_empty else f"{changes.total} cambio(s)"))
    for label, items in (("agregados", changes.added), ("modificados", changes.modified), ("eliminados", changes.deleted)):
        if items:
            lines.append(f"  {label}: {len(items)}")
            lines.extend(f"    - {p}" for p in items[:PATHS_PER_CATEGORY])
            if len(items) > PATHS_PER_CATEGORY:
                lines.append(f"    ... y {len(items) - PATHS_PER_CATEGORY} mas")
    code_clean = not code.dirty_files and not code.unpushed_commits
    lines.append("CODIGO (repo publico): " + ("sin cambios" if code_clean else "pendiente"))
    if code.dirty_files:
        lines.append(f"  archivos sin commit: {len(code.dirty_files)}")
        lines.extend(f"    - {p}" for p in code.dirty_files[:PATHS_PER_CATEGORY])
        if len(code.dirty_files) > PATHS_PER_CATEGORY:
            lines.append(f"    ... y {len(code.dirty_files) - PATHS_PER_CATEGORY} mas")
    if code.unpushed_commits:
        lines.append(f"  commits sin push: {code.unpushed_commits}")
    if code.unpushed_commits is None:
        lines.append("  (sin rama remota configurada)")
    if not changes.is_empty:
        lines.append("ACCION: regenerar el respaldo cifrado, subirlo y ejecutar --baseline --force.")
    return elide("\n".join(lines))


# ----------------------------------------------------------------------- infraestructura
def run_git(root: Path, args: List[str]) -> bytes:
    try:
        proc = subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=str(root),
                              capture_output=True, check=True, timeout=120)
    except FileNotFoundError as exc:
        raise MonitorError("git no esta instalado") from exc
    except subprocess.CalledProcessError as exc:
        raise MonitorError(f"git {' '.join(args)} fallo: {exc.stderr.decode('utf-8', 'replace').strip()[:200]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise MonitorError(f"git {' '.join(args)} excedio el tiempo limite") from exc
    return proc.stdout


def list_data_files(root: Path) -> List[str]:
    raw = run_git(root, ["ls-files", "-z", "-o", "-i", "--exclude-standard"])
    rels = [r.decode("utf-8") for r in raw.split(b"\0") if r]
    return sorted(r for r in rels if not is_excluded(r))


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(HASH_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(root: Path, cache: Optional[Dict[str, FileRecord]] = None) -> Dict[str, FileRecord]:
    """Reutiliza el hash previo si tamano y mtime no cambiaron (vigilancia barata)."""
    cache = cache or {}
    manifest: Dict[str, FileRecord] = {}
    for rel in list_data_files(root):
        path = root / rel
        try:
            stat = path.stat()
            prev = cache.get(rel)
            if prev and prev.size == stat.st_size and prev.mtime_ns == stat.st_mtime_ns:
                manifest[rel] = prev
            else:
                manifest[rel] = FileRecord(stat.st_size, stat.st_mtime_ns, hash_file(path))
        except OSError as exc:
            log.warning("no se pudo leer %s: %s", rel, exc)
    return manifest


def save_manifest(path: Path, root: Path, manifest: Dict[str, FileRecord]) -> None:
    payload = {
        "version": MANIFEST_VERSION,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "root": str(root),
        "files": {k: {"size": v.size, "mtime_ns": v.mtime_ns, "sha256": v.sha256} for k, v in manifest.items()},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".manifest_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=1, sort_keys=True)
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, path)
    except OSError:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise


def load_manifest(path: Path) -> Dict[str, FileRecord]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("version") != MANIFEST_VERSION:
            raise MonitorError(f"version de manifiesto no soportada: {data.get('version')}")
        return {k: FileRecord(int(v["size"]), int(v["mtime_ns"]), str(v["sha256"])) for k, v in data["files"].items()}
    except FileNotFoundError as exc:
        raise MonitorError(f"no existe la linea base ({path}); ejecute --baseline") from exc
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise MonitorError(f"manifiesto corrupto ({path}): {exc}") from exc


def code_status(root: Path) -> CodeStatus:
    porcelain = run_git(root, ["status", "--porcelain", "-z"]).split(b"\0")
    dirty = tuple(sorted(e[3:].decode("utf-8") for e in porcelain if len(e) > 3))
    try:
        ahead: Optional[int] = int(run_git(root, ["rev-list", "--count", "@{u}..HEAD"]).strip() or 0)
    except MonitorError:
        ahead = None
    return CodeStatus(dirty_files=dirty, unpushed_commits=ahead)


def notify_macos(title: str, message: str) -> None:
    safe = message.replace('"', "'")[:180]
    try:
        subprocess.run(["osascript", "-e", f'display notification "{safe}" with title "{title}"'],
                       check=True, capture_output=True, timeout=10)
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        log.warning("notificacion de macOS no disponible: %s", exc)


# --------------------------------------------------------------------------- casos de uso
def cmd_baseline(root: Path, manifest_path: Path, force: bool) -> int:
    if manifest_path.exists() and not force:
        raise MonitorError("ya existe una linea base; use --force solo despues de regenerar el respaldo cifrado")
    manifest = build_manifest(root)
    save_manifest(manifest_path, root, manifest)
    log.info("linea base creada: %d archivos -> %s", len(manifest), manifest_path)
    print(f"Linea base creada: {len(manifest)} archivos en {manifest_path}")
    return EXIT_OK


def evaluate(root: Path, manifest_path: Path, cache: Optional[Dict[str, FileRecord]] = None
             ) -> Tuple[ChangeSet, CodeStatus, Dict[str, FileRecord]]:
    baseline = load_manifest(manifest_path)
    current = build_manifest(root, cache if cache is not None else baseline)
    return diff_manifests(baseline, current), code_status(root), current


def cmd_check(root: Path, manifest_path: Path) -> int:
    changes, code, _ = evaluate(root, manifest_path)
    print(render_report(changes, code))
    pending = not changes.is_empty or bool(code.dirty_files) or bool(code.unpushed_commits)
    log.info("check: datos=%d codigo_sin_commit=%d sin_push=%s", changes.total, len(code.dirty_files), code.unpushed_commits)
    return EXIT_CHANGES if pending else EXIT_OK


def cmd_watch(root: Path, manifest_path: Path, interval: int) -> int:
    log.info("vigilancia iniciada (cada %d s)", interval)
    print(f"Vigilando cada {interval} s. Ctrl-C para salir.")
    cache = load_manifest(manifest_path)
    last_sig = ""
    try:
        while True:
            try:
                changes, code, cache = evaluate(root, manifest_path, cache)
                sig = changes.signature() + "|" + ",".join(code.dirty_files) + f"|{code.unpushed_commits}"
                pending = not changes.is_empty or bool(code.dirty_files) or bool(code.unpushed_commits)
                if pending and sig != last_sig:
                    print(f"\n[{time.strftime('%H:%M:%S')}]\n{render_report(changes, code)}")
                    log.warning("cambios detectados: datos=%d codigo=%d", changes.total, len(code.dirty_files))
                    notify_macos("Respaldo IDS Movilnet", f"{changes.total} cambio(s) de datos, "
                                 f"{len(code.dirty_files)} archivo(s) sin commit")
                elif not pending and last_sig:
                    log.info("sin cambios pendientes")
                last_sig = sig if pending else ""
            except MonitorError as exc:
                log.error("ciclo de vigilancia fallo: %s", exc)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nVigilancia detenida.")
        return EXIT_OK


# ------------------------------------------------------------------------ autoverificacion
def run_self_test() -> int:
    assert is_excluded(".venv/lib/x.py") and is_excluded("a/__pycache__/b.pyc") and is_excluded("a/.DS_Store")
    assert is_excluded("231026_IDS_Movilnet/I231026_IDS_Movilnet_Harness2/x.db")
    assert is_excluded("231026_IDS_Movilnet/_ARCHIVO_DUPLICADOS_181026/c/.env.example")
    assert not is_excluded("231026_IDS_Movilnet/Movilnet_161026/local_movilnet.db")
    r1, r2 = FileRecord(1, 1, "a"), FileRecord(2, 2, "b")
    cs = diff_manifests({"x": r1, "y": r1, "z": r1}, {"x": r1, "y": r2, "n": r1})
    assert (cs.added, cs.modified, cs.deleted) == (["n"], ["y"], ["z"]) and cs.total == 3
    assert diff_manifests({"x": r1}, {"x": r1}).is_empty
    assert cs.signature() != ChangeSet().signature()
    assert len(elide("x" * 10000)) < REPORT_LIMIT_CHARS and elide("corto") == "corto"
    big = ChangeSet(added=[f"f{i}.db" for i in range(500)])
    assert len(render_report(big, CodeStatus((), 0))) <= REPORT_LIMIT_CHARS
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "m.json"
        save_manifest(target, Path(tmp), {"a/b.db": r1})
        assert load_manifest(target) == {"a/b.db": r1} and oct(target.stat().st_mode & 0o777) == "0o600"
        target.write_text("{no json", encoding="utf-8")
        try:
            load_manifest(target)
        except MonitorError:
            pass
        else:
            raise AssertionError("manifiesto corrupto debio fallar")
    print("autoverificacion OK")
    return EXIT_OK


# ------------------------------------------------------------------------------- CLI
def configure_logging(log_path: Path) -> None:
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handler: logging.Handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=512_000, backupCount=3,
                                                                       encoding="utf-8")
    except OSError:
        handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(fmt)
    log.addHandler(handler)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Monitor de cambios del respaldo cifrado IDS Movilnet")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent, help="raiz del repositorio")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--baseline", action="store_true", help="crear linea base")
    group.add_argument("--check", action="store_true", help="comparar contra la linea base")
    group.add_argument("--watch", type=int, metavar="SEG", help="vigilar cada SEG segundos (minimo 5)")
    group.add_argument("--test", action="store_true", help="autoverificacion")
    parser.add_argument("--force", action="store_true", help="permite sobrescribir la linea base")
    args = parser.parse_args(argv)

    if args.test:
        return run_self_test()
    configure_logging(args.log)
    try:
        if args.baseline:
            return cmd_baseline(args.root, args.manifest, args.force)
        if args.check:
            return cmd_check(args.root, args.manifest)
        if args.watch < 5:
            raise MonitorError("--watch requiere un intervalo >= 5 segundos")
        return cmd_watch(args.root, args.manifest, args.watch)
    except MonitorError as exc:
        log.error("%s", exc)
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
