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
