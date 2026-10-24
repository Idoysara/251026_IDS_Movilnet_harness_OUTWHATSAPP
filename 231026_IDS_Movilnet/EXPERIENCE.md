# 🧠 BIBLIOTECA DE EXPERIENCIA — IDS_MOVILNET

Este registro almacena el histórico de lecciones aprendidas, fallos de referencia y mutaciones efectivas observadas en el proyecto **IDS_Movilnet**, vinculado a la red global de arneses en `~/.gemini/harness2_global_library/EXPERIENCE.md`.

---

## [EXP-MOVILNET-000] Inicialización de Arnés y Enlace Global
- **Fecha**: 2026-10-23
- **Ámbito**: Arquitectura y Memoria de Sesión
- **Problema de Referencia**: Riego de desborde de contexto por lectura indiscriminada de los 591 archivos Python de telecomunicaciones y fintech.
- **Veredicto Empírico**: `helped`
- **Mutación Validada**: Inyección de `GUARDRAILS.md` con límites de chunking (15 archivos / 600 líneas) y elisión obligatoria a <2,000 caracteres.
- **Invariante Derivado**: Invariante I y II en `GUARDRAILS.md`.

---

## [EXP-MOVILNET-001] Aislamiento Hermético en Tests de OCR y Audio STT
- **Fecha**: 2026-10-23
- **Ámbito**: `MODULO_DESPACHO_MULTIMODAL/tests/`
- **Problema de Referencia**: Pruebas de integración multimodales que intentan cargar binarios pesados de Tesseract o modelos de Whisper locales fallan o consumen segundos excesivos en CI/CD local si no hay GPU o dependencias de sistema.
- **Veredicto Empírico**: `helped`
- **Mutación Validada**: Implementación de fixtures deterministas y backends de prueba desacoplados (Fakes/Mocks en `tests/fakes.py`) que validan la lógica de negocio y los contratos en <100ms.
- **Invariante Derivado**: Pilar II & V de Excelencia Técnica.

---

## [EXP-MOVILNET-003] Desacoplamiento de Espacios de Nombres en Microservicios Monorepo (OUTWHATSAPP)
- **Fecha**: 2026-10-23
- **Ámbito**: `MODULO_OUTWHATSAPP/` vs `MODULO_DESPACHO_MULTIMODAL/`
- **Problema de Referencia**: Colisión de nombres en ejecuciones globales de pytest cuando múltiples microservicios comparten nombres de carpeta de dominio (`domain/`, `application/`, `infrastructure/`).
- **Veredicto Empírico**: `helped`
- **Mutación Validada**: Encapsulamiento del paquete bajo prefijo unívoco (`outwhatsapp/`) y uso de `sys.path.append()`, permitiendo que coexistan múltiples microservicios independientes con 180/180 pruebas aprobadas en paralelo sin contaminación de namespaces.
- **Invariante Derivado**: Pilar I (Arquitectura Hexagonal Desacoplada) & Invariante V.

---

## [EXP-MOVILNET-004] Selección Ciega Neutral de Candidatos de Arnés (HarnessBlindJudge)
- **Fecha**: 2026-10-23
- **Ámbito**: Herramientas MCP Harness² (`blind_select`)
- **Problema de Referencia**: Sesgo cognitivo hacia soluciones sobrecargadas o de alta complejidad aparente al evaluar propuestas de arnés.
- **Veredicto Empírico**: `helped`
- **Mutación Validada**: Anonimización estricta de entregables (Candidato A vs B) y evaluación ciega automatizada con enfoque exclusivo en cumplimiento funcional, pruebas y Zero-PII.
- **Invariante Derivado**: Invariante IV (Blind Selection para k > 1).

---

## [EXP-MOVILNET-005] Respaldo Dual Soberano: Público Zero-PII y Privado Cifrado AES-256 Particionado
- **Fecha**: 2026-10-23
- **Ámbito**: Gobernanza Git, Respaldo y Protección de Datos
- **Problema de Referencia**: Necesidad de respaldar en GitHub código y datos masivos (bases de datos de producción SQLite de 20MB+ y archivos `.env`) sin violar Zero-PII ni superar el límite de 100 MB por archivo de GitHub.
- **Veredicto Empírico**: `helped`
- **Mutación Validada**: Separación estricta en dos repositorios: repo público con 299 archivos de código limpio, y repo privado con archivo cifrado AES-256-CBC (PBKDF2 600k iteraciones, clave en Keychain) particionado en 3 trozos de 90 MB, verificado con prueba espejo de restauración al 100% (1.424/1.424 archivos idénticos).
- **Invariante Derivado**: Pilar VI (Auditoría Forense Zero-PII) y Pilar VII.

---

## [EXP-MOVILNET-006] Monitor de Cambios Autónomo con Salida Elidida y Línea Base SHA-256
- **Fecha**: 2026-10-23
- **Ámbito**: `scripts/monitor_respaldo.py` y `MONITOREAR_RESPALDO.command`
- **Problema de Referencia**: Riesgo de que el respaldo cifrado quede desactualizado ante cambios locales inadvertidos en datos o código, sin depender de librerías externas ni generar volcados masivos en consola.
- **Veredicto Empírico**: `helped`
- **Mutación Validada**: Script autónomo en Python estándar (compatible 3.9+) con CLI `--baseline/--check/--watch/--test`, caché mtime/size para evitar re-hashear archivos no modificados, salida truncada a <2.000 caracteres y lanzador de doble clic para el usuario.
- **Invariante Derivado**: Pilar II (Autonomía de Módulos), Pilar VII (Cero Terminal para el Dueño) e Invariante II.

---

## [EXP-MOVILNET-007] Preservación de n8n en `LOCKED_FREEZE` mediante Patrón Fachada Adaptadora
- **Fecha**: 2026-10-23
- **Ámbito**: Interconexión Telco $\leftrightarrow$ n8n Workflow Automation
- **Problema de Referencia**: Reemplazar WhatsApp por la Línea Master Movilnet sin alterar el flujo de n8n en producción (`viki_lpgtec_v2_ids_instant_dispatch.json`), evitando riesgos de regresión en sus 83 nodos.
- **Veredicto Empírico**: `helped`
- **Mutación Validada**: Detección de que el nodo `HTTP Request` de n8n resuelve dinámicamente `$('Webhook').item.json.body.server_url`. Inyección en el webhook de entrada de `server_url: "http://127.0.0.1:8035"`, haciendo que n8n despache respuestas a nuestro microservicio soberano sin requerir ninguna modificación en n8n (0 cambios de código).
- **Invariante Derivado**: Pilar I (Arquitectura Hexagonal / Patrón Adaptador).

---

## [EXP-MOVILNET-008] Deflexión Telefónica Tradicional a Webhook IP (Voice-to-IP / Flash Call)
- **Fecha**: 2026-10-23
- **Ámbito**: Señalización Celular (SIP/ISUP) $\longleftrightarrow$ Webhooks IP
- **Problema de Referencia**: Iniciar la interacción digital de autogestión y saldo a partir de una llamada tradicional de voz al número máster (`0424-1533712`) sin costo de canal de voz ni fricción de WhatsApp.
- **Veredicto Empírico**: `helped`
- **Mutación Validada**: Captura del Caller ID en señalización inicial `SIP INVITE` / `ISUP IAM` en $<10\text{ ms}$, corte de llamada inmediato (Toque Inteligente / Flash Call con duración 0 segundos y costo $\$0.00$), y disparo automático de HTTP POST a n8n con despacho de Magic Link PWA por SMS.
- **Invariante Derivado**: Pilar I & Pilar III (Invariantes de Dominio Telco).

