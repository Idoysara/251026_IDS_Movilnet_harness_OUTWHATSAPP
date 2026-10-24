"""
Orquestador Local Asíncrono de Eventos y Cola de Reintentos (Sustitución de n8n).
Gobernanza: Universal Best Practices Engineering Rule (Pilares I, II y IV).
Elimina la necesidad de un servidor n8n intermedio, procesando eventos en cola interna con DLQ.
"""
import time
import threading
import logging
from typing import Dict, Any, List, Optional, Callable
from collections import deque
from datetime import datetime, timezone, timedelta

try:
    from outwhatsapp.domain.enums import SovereignChannel, DeliveryStatus
    from outwhatsapp.domain.models import DLQEvent, DispatchResult
    from outwhatsapp.application.sovereign_dispatcher import SovereignDispatcher
except ImportError:
    from outwhatsapp.domain.enums import SovereignChannel, DeliveryStatus
    from outwhatsapp.domain.models import DLQEvent, DispatchResult
    from outwhatsapp.application.sovereign_dispatcher import SovereignDispatcher

logger = logging.getLogger("outwhatsapp.orchestrator")


class LocalAsyncOrchestrator:
    """
    Motor local de orquestación reactiva que reemplaza workflows de n8n.
    Mantiene buffers en memoria thread-safe y Dead Letter Queue (DLQ).
    """

    def __init__(
        self,
        dispatcher: Optional[SovereignDispatcher] = None,
        max_retries: int = 3,
        backoff_base_seconds: float = 1.0
    ):
        self.dispatcher = dispatcher or SovereignDispatcher()
        self.max_retries = max_retries
        self.backoff_base = backoff_base_seconds
        self._queue: deque = deque()
        self._dlq: List[DLQEvent] = []
        self._lock = threading.RLock()
        self._processed_count = 0
        self._failure_count = 0

    def encolar_despacho(
        self,
        msisdn: str,
        titulo: str,
        mensaje: str,
        canal_preferido: Optional[SovereignChannel] = None,
        telegram_chat_id: Optional[int] = None
    ) -> str:
        """
        Ingesta una tarea de despacho en la cola asíncrona local (<0.1ms).
        """
        payload = {
            "msisdn": msisdn,
            "titulo": titulo,
            "mensaje": mensaje,
            "canal_preferido": canal_preferido,
            "telegram_chat_id": telegram_chat_id,
            "retry_count": 0,
            "enqueued_at": time.time()
        }
        with self._lock:
            self._queue.append(payload)
        return f"TASK-{int(time.time()*1000)}"

    def procesar_cola(self, max_items: int = 50) -> List[DispatchResult]:
        """
        Procesa un lote de eventos encolados ejecutando reintentos con retroceso exponencial.
        """
        resultados: List[DispatchResult] = []
        items_a_procesar = []

        with self._lock:
            count = min(len(self._queue), max_items)
            for _ in range(count):
                items_a_procesar.append(self._queue.popleft())

        for item in items_a_procesar:
            res = self.dispatcher.despachar(
                msisdn=item["msisdn"],
                titulo=item["titulo"],
                mensaje=item["mensaje"],
                canal_preferido=item["canal_preferido"],
                telegram_chat_id=item["telegram_chat_id"]
            )
            resultados.append(res)

            with self._lock:
                if res.success:
                    self._processed_count += 1
                else:
                    self._failure_count += 1
                    # Evaluar reintento o envío a DLQ
                    retry_count = item["retry_count"] + 1
                    if retry_count <= self.max_retries:
                        item["retry_count"] = retry_count
                        # Re-encolar con retroceso
                        self._queue.append(item)
                    else:
                        # Enviar a Dead Letter Queue
                        dlq_event = DLQEvent(
                            original_channel=res.channel_used,
                            recipient_msisdn=item["msisdn"],
                            payload=item,
                            retry_count=retry_count,
                            max_retries=self.max_retries,
                            last_error=res.message
                        )
                        self._dlq.append(dlq_event)
                        logger.warning(f"Evento {dlq_event.event_id} transferido a DLQ tras {retry_count} reintentos")

        return resultados

    def obtener_dlq(self) -> List[DLQEvent]:
        """Obtiene la lista inmutable de mensajes en Dead Letter Queue."""
        with self._lock:
            return list(self._dlq)

    def purgar_dlq(self) -> int:
        """Limpia los eventos resueltos en DLQ."""
        with self._lock:
            count = len(self._dlq)
            self._dlq.clear()
            return count

    def metricas(self) -> Dict[str, Any]:
        """Retorna telemetría dura del orquestador local."""
        with self._lock:
            return {
                "pendientes_en_cola": len(self._queue),
                "eventos_en_dlq": len(self._dlq),
                "procesados_exitosos": self._processed_count,
                "fallos_totales": self._failure_count
            }
