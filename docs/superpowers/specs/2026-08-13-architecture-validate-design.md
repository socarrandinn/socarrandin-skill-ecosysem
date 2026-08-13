# Diseño: architecture-validate (validateTierContinuity)

Fecha: 2026-08-13
Estado: aprobado
Base: 2026-08-13-architecture-clone-design.md

## Propósito

Cerrar las discontinuidades de continuidad del contrato `state.json` en el pipeline architecture-clone. Nuevo skill `architecture-validate` que vigila la continuidad entre tiers (schema → analyze → generate → orquestador) antes de cada paso, auto-sana lo derivable de disco y aborta ante bloqueantes. Además corrige los 6 bugs de continuidad encontrados en el análisis del pipeline.

## Discontinuidades halladas (fuente del diseño)

| # | Bug | Archivo afectado |
|---|---|---|
| D1 | `paso:"generate"` es valor muerto: nadie lo escribe; orquestador condiciona a él | agent/architecture-clone.md:20, state.schema.json |
| D2 | generate lee summary hardcodeado, ignora `state.json.resumen` | skills/architecture-generate/SKILL.md:12 |
| D3 | `skillGenerada` guarda 1 ruta para 2 copias espejo | state.schema.json, skills/architecture-generate/SKILL.md |
| D4 | Sin ruta de re-análisis con `paso:"listo"` | agent/architecture-clone.md:20 |
| D5 | Reanudar análisis a medias = re-analizar todo (sin checkpoint) | skills/architecture-analyze/SKILL.md, README.md:60 |
| D6 | `resumen` no es requerido en schema | state.schema.json:6 |

## Decisiones (brainstorming)

| Decisión | Elección |
|---|---|
| Forma | Skill nuevo `architecture-validate` (sin scripts; agente usa herramientas de lectura) |
| Alcance | Validar + corregir las 6 discontinuidades del pipeline |
| Cadencia | Al inicio de cada paso (validate → analyze → generate → validate final) |
| Ante fallo | Reportar + auto-sanear campos derivables de disco; abortar ante bloqueantes/ambigüedad |

## Archivos del cambio

```
architecture-clone-plugins/
  skills/architecture-validate/SKILL.md   # NUEVO
  agent/architecture-clone.md             # MOD — cargar validate al inicio de cada paso
  skills/architecture-analyze/SKILL.md    # MOD — fix D5 (checkpoint progreso)
  skills/architecture-generate/SKILL.md   # MOD — fix D2 (resumen vía state.json), D3 (skillEspejo)
  state.schema.json                       # MOD — D1 (enum), D3 (skillEspejo), D6 (resumen requerido)
  README.md                               # MOD — pipeline 3 skills, tabla actualizada
```

## Flujo del orquestador (3 fases)

```
"clona la arquitectura"
  → orquestador
    1. carga architecture-validate → reporte V1-V7 + auto-sanado
       - si ✗ bloqueante: detener, reportar, pedir decisión
    2. carga architecture-analyze (si paso="analyze")
       - analiza, escribe state.json + summary + progreso (checkpoint D5)
    3. carga architecture-validate (estado fresco)
    4. carga architecture-generate (si summary listo)
       - lee state.json.resumen (D2), escribe skill .claude + .opencode
       - registra skillGenerada + skillEspejo (D3)
    5. carga architecture-validate (final) → paso="listo" verificado
```

Reanudación: `paso:"analyze"` → retoma analyze; `paso:"analyze"` con summary + skill → ofrecer generate; `paso:"listo"` → ofrecer regenerar o re-analizar (D4: tras confirmación del usuario, forzar `paso:"analyze"`).

## Checks de architecture-validate (V1-V7)

| Check | Detecta | Severidad | Auto-sanado |
|---|---|---|---|
| V1 | state.json falta o JSON inválido | ✗ bloqueante | no — sugerir analyze |
| V2 | campos requeridos ausentes (`proyecto, nombre, paso, fecha, resumen`) | ✗ bloqueante | fecha=ahora si falta; el resto no |
| V3 | `paso` fuera de enum `["analyze","listo"]` | ✗ bloqueante | no — decisión humana |
| V4 | `state.json.resumen` no existe en disco | ✗ bloqueante (si paso≥analyze) | único `architecture-summary.md` en `.architecture-clone/` → corregir ruta; 0 o 2+ → abortar |
| V5 | `paso` incoherente con artefactos en disco (ej. "listo" sin skill, "analyze" con summary) | ⚠ aviso | recalcular paso derivable; rellenar skillGenerada/skillEspejo desde disco |
| V6 | `skillGenerada`/`skillEspejo` apuntan a nada | ⚠ aviso | escanear `.claude/skills/*-convenciones/` y `.opencode/skills/`; match único → corregir; parcial → sanear lo faltante |
| V7 | `fecha` ausente o formato no ISO | ⚠ aviso | reescribir con fecha actual |

## Fixes de pipeline

| Fix | Archivo | Cambio |
|---|---|---|
| F1 | agent + schema | Orquestador decide por artefactos (summary/skill en disco), no por valor `"generate"`. Schema: `paso` enum `["analyze","listo"]` |
| F2 | generate | Leer summary vía `state.json.resumen` |
| F3 | generate + schema | `skillGenerada` = ruta principal (`.claude/`); campo nuevo `skillEspejo` = ruta `.opencode/` |
| F4 | agent | `paso:"listo"` + pedido "re-analiza" → confirmar → forzar `paso:"analyze"` |
| F5 | analyze | Campo nuevo `progreso` en state.json; analyze retoma desde el último checkpoint (ej. "estructura", "stack", "testing", "resumen") |
| F6 | schema | `resumen` pasa a required |

## Reglas de seguridad del auto-sanado

- Solo toca `state.json` (archivo que el agente escribe). Nunca crea/borra artefactos.
- Solo sana campos derivables de disco. Ambigüedad → abortar con reporte.
- Cada saneo registrado en el reporte con evidencia (`V6: skillEspejo corregido → ruta (encontrado en disco)`).
- `state.json` inexistente → no crear vacío; falla limpio y el pipeline arranca desde analyze.

## Errores

| Caso | Comportamiento |
|---|---|
| state.json corrupto | ✗ V1, abortar, sugerir re-analyze |
| summary muerto, 1 candidato | sana ruta, continúa |
| summary muerto, 0 o 2+ | ✗ V4, abortar, pedir analyze |
| skill parcial (1 de 2 espejos) | ⚠ V6, sana desde disco, continúa |
| `paso:"listo"` + skill borrada | ⚠ V5, orquestador ofrece regenerar skill (generate sin re-analizar) |

## Testing (writing-skills Iron Law)

Fixture: repo de prueba con `state.json` manipulado + summary/skills en estados variados.

| Escenario | Estado inicial | Esperado |
|---|---|---|
| T1 | state.json no existe | V1 ✗, reporte limpio, no crea archivo, sugiere analyze |
| T2 | state válido, todo sano | V1-V7 ✓, no toca nada |
| T3 | resumen ruta muerta, 1 summary en disco | V4 sana ruta, reporte "corregido", continúa |
| T4 | resumen muerto, 0 summaries | V4 ✗, aborta, sugiere analyze |
| T5 | paso:"listo" + falta espejo, existe en disco | V6 sana skillEspejo, continúa |
| T6 | paso:"listo" + ambas skills borradas | V5 ⚠, orquestador ofrece regenerar |
| T7 | fecha formato malo | V7 sana con fecha actual |
| T8 | paso valor inválido ("generar") | V3 ✗, aborta, decisión humana |
| T9 | analyze interrumpido con progreso:"estructura" | F5: retoma desde estructura, no re-escanea |
| T10 | "re-analiza" con paso:"listo" | F4: validate marca desincronía, confirma, fuerza analyze |

Verificación adicional:
- Reporte de validate legible: una línea por check, severidad, evidencia (`ruta:linea`).
- `state.json` sano al final de cada escenario (parsea + cumple schema).
- El orquestador nunca avanza con ✗ pendiente.

## Fuera de alcance

- Scripts Python/runtime (validación la hace el agente con herramientas de lectura, igual que el análisis)
- Validación runtime del state.json por máquina
- Cambios en ebook-studio-plugins