"""
Capa de Dominio Puro para el Módulo OUTWHATSAPP.
"""
from .enums import SovereignChannel, DeliveryStatus, SMPPCommandId, PushUrgency
from .models import (
    WebPushKeys,
    WebPushSubscription,
    SMPPMessage,
    TelegramWebAppData,
    SovereignDispatchEvent,
    DLQEvent,
    DispatchResult
)
from .invariants import SovereignInvariants, SovereignInvariantViolationError
from .fsm import SovereignDispatchFSM, IllegalDispatchStateTransitionError

__all__ = [
    "SovereignChannel",
    "DeliveryStatus",
    "SMPPCommandId",
    "PushUrgency",
    "WebPushKeys",
    "WebPushSubscription",
    "SMPPMessage",
    "TelegramWebAppData",
    "SovereignDispatchEvent",
    "DLQEvent",
    "DispatchResult",
    "SovereignInvariants",
    "SovereignInvariantViolationError",
    "SovereignDispatchFSM",
    "IllegalDispatchStateTransitionError"
]
