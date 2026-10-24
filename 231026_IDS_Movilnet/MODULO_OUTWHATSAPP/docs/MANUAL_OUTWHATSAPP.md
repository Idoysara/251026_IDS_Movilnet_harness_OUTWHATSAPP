# 📘 MANUAL DE OPERACIÓN Y ARQUITECTURA SOBERANA — MÓDULO OUTWHATSAPP
**Telecomunicaciones Movilnet C.A. — Core PWA 4GMAX**  
**Gobernanza:** Universal Best Practices Engineering Rule (Pilares I al VII) & Protocolo Decagonal  
**Clasificación:** Grado Militar Carrier-Grade (4.000.000 Abonados)  

---

## 🎯 1. ¿Qué es OUTWHATSAPP?

**OUTWHATSAPP** es el subsistema de software soberano diseñado para **erradicar por completo la dependencia de WhatsApp, Meta, n8n y LLMs en la nube**, otorgando a Telecomunicaciones Movilnet C.A. autonomía tecnológica total e invulnerabilidad operativa frente a baneos arbitrarios o caídas de servicios extranjeros.

### Los 3 Pilares de Canales Soberanos:
1. **Canal Primario — Super-App PWA Soberana (Web Push Notifications W3C):**
   - Notificaciones push emitidas directamente al sistema operativo del dispositivo móvil (Android / iOS) vía estándar RFC 8291 / RFC 8292.
   - Costo: **$0.00**.
   - Dependencia de Meta: **0%**.
2. **Canal Carrier — SMS SMPP v3.4 Directo al SMSC Movilnet:**
   - Conector carrier-grade binario que interactúa directamente con el Centro de Mensajería Corta (SMSC) de la red celular de Movilnet.
   - Despacho de mensajes concisos ($\le 160$ caracteres) con **Magic Links firmados con HMAC-SHA256** para auto-login sin contraseña.
   - Costo interbancario/Meta: **$0.00** (infraestructura interna de Movilnet).
3. **Canal Alternativo — Telegram WebApp:**
   - Entrega de teclados en línea con botones `web_app` que abren la PWA embebida en Telegram con un solo toque.

---

## 🏛️ 2. Topología Hexagonal y Aislamiento de Puertos

El módulo corre de forma autónoma en el puerto canónico **`:8035`**, conviviendo en armonía con los demás servicios sin colisión de puertos:
- `:8010`: Core Movilnet API (TM Forum ODA REST).
- `:8025`: Módulo de Despacho Multimodal (OCR Apple Vision/Tesseract + Whisper STT + Bóvedas $1 \leftrightarrow N$).
- `:8030`: Cazador de Ofertas Movilnet (Radar Geoespacial + TOTP 60s + Carrier Billing Split 20/80).
- **`:8035`**: **Módulo Soberano OUTWHATSAPP** (SMPP v3.4 + VAPID Push + Orquestador Local).

---

## ⚡ 3. Endpoints RESTful (:8035)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/health` | Monitoreo en vivo y confirmación de soberanía |
| `POST` | `/api/v1/sovereign/dispatch` | Despacho inteligente unificado (PWA Push > SMS SMPP > Telegram) |
| `POST` | `/api/v1/push/subscribe` | Registro de suscripciones W3C Push de la PWA |
| `POST` | `/api/v1/smpp/send` | Envío directo de SMS al SMSC vía binario SMPP v3.4 |
| `POST` | `/api/v1/telegram/deflect` | Construcción de payload Telegram con botón WebApp |
| `GET` | `/api/v1/metrics` | Telemetría agregada Zero-PII y estado de Dead Letter Queue (DLQ) |

---

## 🚀 4. Inicio Rápido (Cero Terminal — Pilar VII)

### Para Ejecutar las Pruebas y Certificar (100% Pass):
Haz doble clic en:
`PROBAR_MODULO_OUTWHATSAPP.command`

### Para Iniciar el Microservicio Soberano (:8035):
Haz doble clic en:
`INICIAR_MODULO_OUTWHATSAPP.command`

---

## 🔒 5. Cumplimiento de Invariantes y Principio Zero-PII
- **Cero Datos Sensibles en Claro:** Los números telefónicos se indexan exclusivamente mediante funciones hash irreversibles `HMAC-SHA256(msisdn, secret)` (Blind Index en tiempo $O(1)$).
- **Control Estricto de Prefijos:** Rechazo inmediato de prefijos ajenos (`0414`, `0424`, `0412`), permitiendo únicamente `0416` y `0426`.
- **Límite de Longitud SMPP:** Restricción matemática estricta a $\le 160$ caracteres GSM-7.
- **Firma Criptográfica Inmutable:** Magic Links protegidos contra manipulación con firma HMAC-SHA256 y expiración temporal.
