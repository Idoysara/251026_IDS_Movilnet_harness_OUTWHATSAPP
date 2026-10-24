"""
Repositorio Tipado de Persistencia para OUTWHATSAPP con Principio Zero-PII.
Gobernanza: Universal Best Practices Engineering Rule (Pilares I, III y VI).
"""
import hmac
import hashlib
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

try:
    from outwhatsapp.infrastructure.database import get_connection, DEFAULT_DB_PATH
    from outwhatsapp.domain.models import WebPushSubscription, WebPushKeys, SovereignDispatchEvent, DLQEvent
    from outwhatsapp.domain.enums import SovereignChannel, DeliveryStatus
    from outwhatsapp.domain.invariants import SovereignInvariants
except ImportError:
    from outwhatsapp.infrastructure.database import get_connection, DEFAULT_DB_PATH
    from outwhatsapp.domain.models import WebPushSubscription, WebPushKeys, SovereignDispatchEvent, DLQEvent
    from outwhatsapp.domain.enums import SovereignChannel, DeliveryStatus
    from outwhatsapp.domain.invariants import SovereignInvariants

BLIND_SECRET = os.getenv("OUTWHATSAPP_BLIND_SECRET", "MOVILNET_BLIND_INDEX_ZERO_PII_2026").encode("utf-8")


class OutWhatsAppRepository:
    """Acceso a datos SQLite WAL con hashing ciego de MSISDN para cumplimiento Zero-PII."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path

    @staticmethod
    def _blind_hash(msisdn: str) -> str:
        clean = SovereignInvariants.validar_msisdn_movilnet(msisdn)
        return hmac.new(BLIND_SECRET, clean.encode("utf-8"), hashlib.sha256).hexdigest()

    def guardar_suscripcion(self, sub: WebPushSubscription) -> bool:
        """Persiste una suscripción Web Push en la base de datos."""
        m_hash = self._blind_hash(sub.user_msisdn)
        display = f"+58 {sub.user_msisdn[:4]}-***{sub.user_msisdn[-3:]}"
        conn = get_connection(self.db_path)
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO web_push_subscriptions 
                    (msisdn_hash, phone_display, endpoint, p256dh_key, auth_secret, is_active, updated_at)
                    VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT(msisdn_hash) DO UPDATE SET
                        endpoint=excluded.endpoint,
                        p256dh_key=excluded.p256dh_key,
                        auth_secret=excluded.auth_secret,
                        is_active=1,
                        updated_at=CURRENT_TIMESTAMP
                    """,
                    (m_hash, display, sub.endpoint, sub.keys.p256dh, sub.keys.auth)
                )
            return True
        finally:
            conn.close()

    def obtener_suscripcion(self, msisdn: str) -> Optional[WebPushSubscription]:
        """Recupera la suscripción activa por número de teléfono."""
        m_hash = self._blind_hash(msisdn)
        conn = get_connection(self.db_path)
        try:
            row = conn.execute(
                "SELECT endpoint, p256dh_key, auth_secret FROM web_push_subscriptions WHERE msisdn_hash = ? AND is_active = 1",
                (m_hash,)
            ).fetchone()
            if not row:
                return None
            return WebPushSubscription(
                endpoint=row["endpoint"],
                keys=WebPushKeys(p256dh=row["p256dh_key"], auth=row["auth_secret"]),
                user_msisdn=msisdn
            )
        finally:
            conn.close()

    def registrar_despacho(self, event: SovereignDispatchEvent) -> bool:
        """Registra la métrica y estatus de un despacho en la bitácora inmutable."""
        m_hash = self._blind_hash(event.recipient_msisdn)
        conn = get_connection(self.db_path)
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO sovereign_dispatch_log
                    (event_id, recipient_hash, channel, message_length, magic_link_issued, status, latency_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event.id,
                        m_hash,
                        event.channel.value,
                        len(event.message_body),
                        1 if event.magic_link else 0,
                        event.status.value,
                        event.latency_ms
                    )
                )
            return True
        finally:
            conn.close()

    def registrar_dlq(self, dlq_event: DLQEvent) -> bool:
        """Guarda un evento fallido en la Dead Letter Queue."""
        m_hash = self._blind_hash(dlq_event.recipient_msisdn)
        conn = get_connection(self.db_path)
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO sovereign_dlq
                    (event_id, original_channel, recipient_hash, payload_json, retry_count, last_error)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        dlq_event.event_id,
                        dlq_event.original_channel.value,
                        m_hash,
                        json.dumps(dlq_event.payload),
                        dlq_event.retry_count,
                        dlq_event.last_error
                    )
                )
            return True
        finally:
            conn.close()

    def obtener_resumen_metricas(self) -> Dict[str, Any]:
        """Calcula agregados estadísticos sin comprometer la privacidad."""
        conn = get_connection(self.db_path)
        try:
            total_despachos = conn.execute("SELECT COUNT(*) FROM sovereign_dispatch_log").fetchone()[0]
            total_push_subs = conn.execute("SELECT COUNT(*) FROM web_push_subscriptions WHERE is_active = 1").fetchone()[0]
            total_dlq = conn.execute("SELECT COUNT(*) FROM sovereign_dlq").fetchone()[0]
            
            # Conteo por canal
            canales = {}
            for r in conn.execute("SELECT channel, COUNT(*) as cnt FROM sovereign_dispatch_log GROUP BY channel").fetchall():
                canales[r["channel"]] = r["cnt"]

            return {
                "total_despachos_soberanos": total_despachos,
                "suscripciones_pwa_push_activas": total_push_subs,
                "eventos_en_dlq": total_dlq,
                "despachos_por_canal": canales
            }
        finally:
            conn.close()
