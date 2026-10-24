# 🔧 TOOL GUIDANCE — CONTRATOS, ESQUEMAS Y REGLAS DE HERRAMIENTAS (v4.50.0)
**Marco Metodológico:** Google Harness² Architecture ([arXiv:2610.14224](https://arxiv.org/abs/2610.14224))  
**Gobernanza:** Universal Best Practices Engineering Rule (Pilares I al IV)  

---

## 🛠️ 1. HERRAMIENTAS DEL SERVIDOR MCP HARNESS² (`mcp-harness2`)

| Herramienta | Entrada Requerida | Salida / Efecto Esperado | Regla Inviolable |
| :--- | :--- | :--- | :--- |
| **`harness_snapshot`** | `workspace_path: str` | Retorna el árbol $H = (c_1, \dots, c_K)$, hash SHA-256 de cada componente y hash global. | La ruta debe ser válida y no escapar a directorios prohibidos. |
| **`harness_propose`** | `candidate_name: str`, `rel_path: str`, `content: str` | Modifica o crea un componente en staging aplicando el contrato *omitted-is-inherited*. | Todo script `.py` propuesto debe pasar por `ast.parse()` con 0 SyntaxErrors. |
| **`harness_probe`** | `candidate_name: str`, `simulation_success: bool`, `log_output: str`, `deliverable: str` | Registra la ejecución empírica y aplica elisión automática a $<2.000$ caracteres. | Prohibido volcar logs sin elisión de contexto. |
| **`harness_compose`** | `supported_edits: List[Dict]` | Sintetiza el arnés sucesor $H'$ fusionando exclusivamente cambios con veredicto `helped`. | Prohibido incluir cambios con veredicto `hurt`, `confounded` o `no observed effect`. |
| **`harness_blind_select`** | `deliverables: Dict[str, str]`, `criteria: str` | Califica entregables anonimizados (A, B, C...) contra los requerimientos sin sesgo de arnés. | Los arneses de origen deben permanecer estrictamente ocultos al evaluador. |
| **`experience_query`** | `domain_or_pattern: str`, `library_path: Optional[str]` | Consulta patrones y lecciones en la biblioteca `EXPERIENCE.md`. | Obligatorio consultar antes de iniciar cualquier ciclo de autorreprogramación. |
| **`experience_commit`** | `task_id`, `cue`, `lesson`, `evidence`, `confidence` | Persiste aprendizajes causales contrastados en `EXPERIENCE.md`. | Solo se admite `confidence: high` si está respaldado por contraste de pruebas 100% PASS. |

---

## ⚡ 2. HERRAMIENTAS DE LOS MICROSERVICIOS DEL ECOSISTEMA

### 1. `SMPPGatewayClient` (`MODULO_OUTWHATSAPP`):
- **Propósito:** Comunicación carrier-grade directa con el SMSC de Movilnet.
- **Contrato:**
  - `dest_msisdn`: Prefijo obligatorio `0416` o `0426` (normalizado a 11 dígitos).
  - `short_message`: Longitud estricta $\le 160$ caracteres GSM-7.
  - `command_id`: `0x00000004` (`SUBMIT_SM`).

### 2. `WebPushService` (`MODULO_OUTWHATSAPP`):
- **Propósito:** Emisión de notificaciones push estándar W3C (RFC 8291).
- **Contrato:**
  - `endpoint`: URL HTTPS segura.
  - `keys`: `p256dh` (mínimo 40 caracteres base64url) y `auth` (mínimo 16 caracteres base64url).
  - `urgency`: `high`, `normal`, `low`, `very-low`.

### 3. `FastPathEngine` (`Movilnet_161026`):
- **Propósito:** Resolución determinista de consultas frecuentes en $<15\text{ ms}$ consumiendo 0 tokens de LLM.
- **Contrato:**
  - Precedencia de expresiones regulares precompiladas.
  - Inyección obligatoria del enlace PWA oficial con Zero-Rating.
