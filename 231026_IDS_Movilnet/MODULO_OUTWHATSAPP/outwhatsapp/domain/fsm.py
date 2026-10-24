"""
Máquina de Estados Finitos (FSM) para el Ciclo de Despacho Soberano OUTWHATSAPP.
Gobernanza: Universal Best Practices Engineering Rule (Pilares I y III).
"""
from typing import Set, Dict
from .enums import DeliveryStatus


class IllegalDispatchStateTransitionError(Exception):
    """Excepción al intentar una transición no permitida en la FSM."""
    pass


class SovereignDispatchFSM:
    """Controlador formal de transiciones de estado para eventos de despacho."""

    TRANSICIONES_LEGALES: Dict[DeliveryStatus, Set[DeliveryStatus]] = {
        DeliveryStatus.QUEUED: {
            DeliveryStatus.DISPATCHED,
            DeliveryStatus.FAILED
        },
        DeliveryStatus.DISPATCHED: {
            DeliveryStatus.DELIVERED_PWA,
            DeliveryStatus.PWA_OPENED,
            DeliveryStatus.COMPLETED,
            DeliveryStatus.FAILED
        },
        DeliveryStatus.DELIVERED_PWA: {
            DeliveryStatus.PWA_OPENED,
            DeliveryStatus.COMPLETED,
            DeliveryStatus.FAILED
        },
        DeliveryStatus.PWA_OPENED: {
            DeliveryStatus.COMPLETED
        },
        DeliveryStatus.COMPLETED: set(),  # Estado terminal
        DeliveryStatus.FAILED: {
            DeliveryStatus.QUEUED  # Reintento permitido vía DLQ
        }
    }

    @classmethod
    def validar_transicion(cls, estado_actual: DeliveryStatus, nuevo_estado: DeliveryStatus) -> None:
        """
        Garantiza que la transición entre estados sea matemáticamente válida.
        """
        if estado_actual == nuevo_estado:
            return  # Idempotente

        destinos_validos = cls.TRANSICIONES_LEGALES.get(estado_actual, set())
        if nuevo_estado not in destinos_validos:
            raise IllegalDispatchStateTransitionError(
                f"Transición prohibida en FSM de Despacho: No se puede transicionar de "
                f"'{estado_actual.value}' a '{nuevo_estado.value}'. "
                f"Transiciones permitidas: {[e.value for e in destinos_validos]}."
            )
