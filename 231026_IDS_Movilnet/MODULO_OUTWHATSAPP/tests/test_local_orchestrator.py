"""
Pruebas para el Orquestador Local Asíncrono (Sustitución de n8n).
Gobernanza: Universal Best Practices Engineering Rule (Pilar V).
"""
import pytest
from outwhatsapp.application.local_orchestrator import LocalAsyncOrchestrator
from outwhatsapp.application.sovereign_dispatcher import SovereignDispatcher
from outwhatsapp.domain.enums import SovereignChannel


def test_enqueue_and_process_batch():
    orchestrator = LocalAsyncOrchestrator()
    task_id1 = orchestrator.encolar_despacho("04161234567", "Aviso 1", "Contenido 1")
    task_id2 = orchestrator.encolar_despacho("04269876543", "Aviso 2", "Contenido 2")

    assert task_id1.startswith("TASK-")
    assert orchestrator.metricas()["pendientes_en_cola"] == 2

    resultados = orchestrator.procesar_cola(max_items=10)
    assert len(resultados) == 2
    assert all(r.success for r in resultados)
    assert orchestrator.metricas()["pendientes_en_cola"] == 0
    assert orchestrator.metricas()["procesados_exitosos"] == 2


def test_dlq_transfer_after_max_retries():
    # Simular un dispatcher que siempre falla
    class FailingDispatcher(SovereignDispatcher):
        def despachar(self, *args, **kwargs):
            from outwhatsapp.domain.models import DispatchResult
            from outwhatsapp.domain.enums import DeliveryStatus
            return DispatchResult(
                success=False,
                event_id="ERR-01",
                channel_used=SovereignChannel.SMS_SMPP,
                delivery_status=DeliveryStatus.FAILED,
                latency_ms=1.0,
                message="Error forzado de prueba de canal"
            )

    orchestrator = LocalAsyncOrchestrator(dispatcher=FailingDispatcher(), max_retries=2)
    orchestrator.encolar_despacho("04161234567", "Alerta", "Mensaje que fallará")

    # Ciclo 1: Primer intento (falla -> re-encolado con retry_count=1)
    orchestrator.procesar_cola(max_items=1)
    assert orchestrator.metricas()["pendientes_en_cola"] == 1
    assert orchestrator.metricas()["eventos_en_dlq"] == 0

    # Ciclo 2: Segundo intento (falla -> re-encolado con retry_count=2)
    orchestrator.procesar_cola(max_items=1)
    assert orchestrator.metricas()["pendientes_en_cola"] == 1
    assert orchestrator.metricas()["eventos_en_dlq"] == 0

    # Ciclo 3: Tercer intento (falla -> supera max_retries=2 -> transferido a DLQ)
    orchestrator.procesar_cola(max_items=1)
    assert orchestrator.metricas()["pendientes_en_cola"] == 0
    assert orchestrator.metricas()["eventos_en_dlq"] == 1

    dlq_items = orchestrator.obtener_dlq()
    assert len(dlq_items) == 1
    assert dlq_items[0].retry_count == 3
    assert dlq_items[0].recipient_msisdn == "04161234567"

    # Purgar DLQ
    purgados = orchestrator.purgar_dlq()
    assert purgados == 1
    assert orchestrator.metricas()["eventos_en_dlq"] == 0
