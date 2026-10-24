---
name: agy-outwhatsapp-orchestrator
description: Habilidad operativa para el enrutamiento, deflexión y despacho de comunicaciones de Telecomunicaciones Movilnet C.A. libres de WhatsApp mediante la tríada PWA Web Push (VAPID), SMS SMPP v3.4 directo y Telegram WebApp.
---

# 🛡️ agy-outwhatsapp-orchestrator: Orquestación Soberana OUTWHATSAPP

Esta habilidad guía y ejecuta las operaciones de despacho y deflexión sin intermediarios de terceros para los 4.000.000 de abonados de Movilnet.

## 🎯 Capacidades Principales
1. **Despacho Omnicanal Soberano:** Prioriza Web Push en la PWA si existe suscripción activa; de lo contrario, envía SMS SMPP directo al SMSC celular o construye el botón WebApp para Telegram.
2. **Generación de Magic Links HMAC:** Crea URLs con Zero-Rating firmadas criptográficamente (`msisdn`, `exp`, `sig`) para acceso 1-Tap a la PWA sin contraseñas.
3. **Manejo de Reintentos y DLQ Local:** Encola tareas asíncronas en memoria con retroceso exponencial, derivando fallos persistentes a la Dead Letter Queue en SQLite WAL sin requerir n8n.
