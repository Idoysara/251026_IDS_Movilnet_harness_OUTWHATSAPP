"""
Capa de Persistencia y Base de Datos SQLite WAL para OUTWHATSAPP.
Gobernanza: Universal Best Practices Engineering Rule (Pilares I y III).
"""
import sqlite3
import os
from typing import Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "../outwhatsapp.db")

DDL_OUTWHATSAPP = """
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;

-- Tabla 1: web_push_subscriptions (Suscripciones W3C Push de la PWA)
CREATE TABLE IF NOT EXISTS web_push_subscriptions (
    msisdn_hash VARCHAR(64) PRIMARY KEY,
    phone_display VARCHAR(20) NOT NULL,
    endpoint TEXT NOT NULL,
    p256dh_key TEXT NOT NULL,
    auth_secret TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_push_active ON web_push_subscriptions(is_active);

-- Tabla 2: sovereign_dispatch_log (Bitácora de Despachos Libres de WhatsApp)
CREATE TABLE IF NOT EXISTS sovereign_dispatch_log (
    event_id VARCHAR(64) PRIMARY KEY,
    recipient_hash VARCHAR(64) NOT NULL,
    channel VARCHAR(30) NOT NULL,
    message_length INTEGER NOT NULL,
    magic_link_issued INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(20) NOT NULL,
    latency_ms REAL NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dispatch_recipient ON sovereign_dispatch_log(recipient_hash);
CREATE INDEX IF NOT EXISTS idx_dispatch_channel ON sovereign_dispatch_log(channel);
CREATE INDEX IF NOT EXISTS idx_dispatch_created ON sovereign_dispatch_log(created_at DESC);

-- Tabla 3: smpp_pdu_audit (Auditoría de Tráfico SMSC SMPP v3.4)
CREATE TABLE IF NOT EXISTS smpp_pdu_audit (
    pdu_id VARCHAR(64) PRIMARY KEY,
    sequence_number INTEGER NOT NULL,
    command_name VARCHAR(30) NOT NULL,
    dest_msisdn_hash VARCHAR(64) NOT NULL,
    char_count INTEGER NOT NULL,
    status_code INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_smpp_seq ON smpp_pdu_audit(sequence_number);

-- Tabla 4: sovereign_dlq (Dead Letter Queue Persistente)
CREATE TABLE IF NOT EXISTS sovereign_dlq (
    event_id VARCHAR(64) PRIMARY KEY,
    original_channel VARCHAR(30) NOT NULL,
    recipient_hash VARCHAR(64) NOT NULL,
    payload_json TEXT NOT NULL,
    retry_count INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Crea una conexión con SQLite optimizada con WAL y soporte de Row."""
    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_outwhatsapp_db(db_path: str = DEFAULT_DB_PATH) -> bool:
    """Ejecuta el DDL de creación de tablas de forma idempotente."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.executescript(DDL_OUTWHATSAPP)
        return True
    finally:
        conn.close()
