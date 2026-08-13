# architecture-validate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear el skill `architecture-validate` que verifica la continuidad del contrato `state.json` entre tiers del pipeline architecture-clone, y corregir las 6 discontinuidades detectadas.

**Architecture:** Skill nuevo (V1-V7 checks + auto-sanado de state.json) + orquestador de 3 fases (validate → analyze → generate) + fixes en analyze (checkpoint `progreso`), generate (lee `resumen`, escribe `skillEspejo`) y schema (resumen required, enum sin "generate", skillEspejo).

**Tech Stack:** Markdown (SKILL.md), JSON (state.schema.json). Sin scripts: la validación la ejecuta el agente con herramientas de lectura.

## Global Constraints

- Los checks y fixes deben trazar a la tabla V1-V7 / F1-F6 del spec `docs/superpowers/specs/2026-08-13-architecture-validate-design.md`
- Lenguaje de órdenes concretas ("Siempre X", "Nunca Y"), igual que los SKILL.md existentes
- Contenido del plugin en español; nombres técnicos, comandos y código en su idioma original
- Auto-sanado: SOLO toca `state.json`, nunca crea/borra summary ni skills
- `state.schema.json` sigue siendo informativo (sin validación runtime)
- No agregar scripts Python ni runtime (fuera de alcance del spec)
- Nombre del skill generado: `<slug>-convenciones` (no cambia)
- Todos los archivos viven en `E:\MY\_TOOLS\socarrandin-skills-ecosysem\architecture-clone-plugins\`

---

### Task 1: Contrato — state.schema.json (F1, F3, F6)

**Files:**
- Modify: `architecture-clone-plugins/state.schema.json`

**Interfaces:**
- Consumes: nada (contrato base)
- Produces: enum `paso = ["analyze","listo"]`, `resumen` requerido, propiedad `skillEspejo`, propiedad `progreso` — nombres exactos que usan Tasks 2-5

- [ ] **Step 1: Escribir el contrato nuevo**

Contenido final completo de `state.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "architecture-clone state.json",
  "description": "Contrato del estado intermedio entre architecture-analyze, architecture-validate y architecture-generate. Informativo: no hay validación en runtime.",
  "type": "object",
  "required": ["proyecto", "nombre", "paso", "fecha", "resumen"],
  "properties": {
    "proyecto": {
      "type": "string",
      "description": "Ruta absoluta del proyecto analizado"
    },
    "nombre": {
      "type": "string",
      "description": "Slug kebab-case del proyecto; base del nombre del skill generado"
    },
    "paso": {
      "type": "string",
      "enum": ["analyze", "listo"],
      "description": "Etapa actual del pipeline. 'generate' ya no es un paso: el orquestador decide por artefactos en disco"
    },
    "resumen": {
      "type": "string",
      "description": "Ruta al architecture-summary.md. Requerido: architecture-analyze siempre lo escribe"
    },
    "progreso": {
      "type": "string",
      "enum": ["estructura", "stack", "testing", "resumen"],
      "description": "Checkpoint del análisis (Task 4). 'resumen' significa análisis completo; permite retomar pasadas a medias"
    },
    "skillGenerada": {
      "type": "string",
      "description": "Ruta principal al SKILL.md de convenciones generado (.claude/skills/...)"
    },
    "skillEspejo": {
      "type": "string",
      "description": "Ruta de la copia espejo (.opencode/skills/...)"
    },
    "fecha": {
      "type": "string",
      "format": "date-time",
      "description": "Fecha ISO de la última actualización"
    }
  }
}
```

- [ ] **Step 2: Verificar que el contrato parsea y cumple lo requerido**

Run (PowerShell, workdir `architecture-clone-plugins`):

```powershell
$s = Get-Content state.schema.json -Raw | ConvertFrom-Json
$s.required -contains 'resumen'      # esperado: True
$s.properties.paso.enum -join ','    # esperado: analyze,listo
$s.properties.skillEspejo.type       # esperado: string
$s.properties.progreso.enum -join ',' # esperado: estructura,stack,testing,resumen
```

Expected: `True`, `analyze,listo`, `string`, `estructura,stack,testing,resumen` — sin errores de parseo.

- [ ] **Step 3: Commit**

```bash
git add state.schema.json
git commit -m "feat: state contract - resumen required, paso sin generate, skillEspejo y progreso"
```

---

### Task 2: Skill architecture-validate (nuevo, V1-V7)

**Files:**
- Create: `architecture-clone-plugins/skills/architecture-validate/SKILL.md`
- Test: fixture en `architecture-clone-plugins/tests/fixture/` (crear en Step 1)

**Interfaces:**
- Consumes: Task 1 (enum `paso`, campos `resumen`, `skillEspejo`, `progreso`)
- Produces: reporte con formato fijo (`V{n} <severidad> <detalle>` + `Resultado: CONTINUAR|DETENER`) que Task 3 consume para decidir

- [ ] **Step 1: Crear fixture base de prueba**

Crear `tests/fixture/` con un mini-repo de proyecto para los escenarios:

```
tests/fixture/proyecto-prueba/.architecture-clone/
  state.json                       # vacío, cada escenario lo rellena
  architecture-summary.md          # contenido de ejemplo
tests/fixture/proyecto-prueba/.claude/skills/
tests/fixture/proyecto-prueba/.opencode/skills/
tests/SCENARIOS.md                 # tabla T1-T10 (crear en Task 6)
```

Crear `tests/fixture/proyecto-prueba/.architecture-clone/architecture-summary.md`:

```markdown
# Resumen de arquitectura: proyecto-prueba
## 1. Estructura y convenciones de nombres
Fixture de prueba. Carpeta src/ con archivos kebab-case.
## 2. Tech stack y versiones
Node.js 22, TypeScript 5.6.
## 3. Dependencias y gestión de paquetes
npm. Express, zod, vitest.
## 4. Patrones de diseño del sistema
Capas: routes → controllers → services.
## 5. Manejo de estado
No aplica.
## 6. API y servicios
Prefijo /api/v1. Envoltura { data }.
## 7. Datos y validación
zod en cada endpoint.
## 8. Testing y convenciones
vitest, tests colocado junto al fuente (<archivo>.test.ts).
## 9. Config, CI/CD y entorno
.env.example validado con zod.
## 10. Reglas de oro (no negociables)
Todo endpoint valida con zod antes de tocar el servicio.
Toda feature nueva lleva test.
```

- [ ] **Step 2: Escribir el skill**

Contenido final completo de `skills/architecture-validate/SKILL.md`:

```markdown
---
name: architecture-validate
description: Use cuando hay que verificar la continuidad del estado del pipeline architecture-clone antes de analizar o generar: "valida el estado", "revisa la continuidad", "¿está todo en orden?". Comprueba state.json contra el contrato y contra los artefactos en disco.
---

# architecture-validate

## Misión
Verificar que `<proyecto>/.architecture-clone/state.json` y los artefactos del tier anterior (architecture-summary.md, SKILL.md de convenciones) sean coherentes entre sí antes de que otra skill actúe. NO analiza ni genera: solo vigila continuidad.

## Entrada
- `<proyecto>/.architecture-clone/state.json`
- `<proyecto>/.architecture-clone/architecture-summary.md`
- `<proyecto>/.claude/skills/*-convenciones/SKILL.md`
- `<proyecto>/.opencode/skills/*-convenciones/SKILL.md`
- Contrato: `state.schema.json` del plugin

## Procedimiento — checks V1 a V7, en orden
Correr TODOS los checks y producir UN reporte. Severidades: ✗ bloqueante (detener pipeline), ⚠ aviso (saneable), ✓ ok.

### V1 — state.json existe y parsea
- No existe → ✗: "no hay state.json; correr architecture-analyze". Nunca crear archivo vacío.
- JSON inválido → ✗: reportar el error de parseo.

### V2 — campos requeridos presentes
- Requeridos: `proyecto`, `nombre`, `paso`, `fecha`, `resumen`.
- Falta `fecha` → sanear con fecha actual ISO.
- Falta cualquier otro requerido → ✗.

### V3 — paso válido
- Valores válidos: `analyze`, `listo`.
- Otro valor → ✗: decisión humana, nunca adivinar.

### V4 — resumen existe en disco
- `state.json.resumen` no existe en disco (y paso es `analyze` o `listo`) → buscar `architecture-summary.md` en `<proyecto>/.architecture-clone/`:
  - exactamente 1 → sanear la ruta en state.json; reportar "V4: resumen corregido → <ruta> (encontrado en disco)".
  - 0 o 2+ → ✗: "resumen ilegible; correr architecture-analyze".

### V5 — paso coherente con artefactos
- `paso:"listo"` y no existe ningún `*-convenciones/SKILL.md` → ⚠: si el summary existe en disco, recalcular `paso:"analyze"` y reportar "V5: paso recalculado a analyze (skills ausentes); regenerar skill con architecture-generate".
- `paso:"analyze"` y existe `*-convenciones/SKILL.md` → ⚠: recalcular a `paso:"listo"` y rellenar `skillGenerada`/`skillEspejo` desde disco (ver V6).

### V6 — rutas de skill viven en disco
- `skillGenerada` no existe o apunta a nada → escanear `<proyecto>/.claude/skills/*-convenciones/SKILL.md`:
  - exactamente 1 → sanear `skillGenerada`; reportar con evidencia.
  - 0 → dejar, reportar ⚠ "skill principal ausente".
- `skillEspejo` no existe o apunta a nada → escanear `<proyecto>/.opencode/skills/*-convenciones/SKILL.md`:
  - exactamente 1 → sanear `skillEspejo`; reportar con evidencia.
  - 0 → ⚠ "skill parcial: falta espejo; completar con architecture-generate".

### V7 — fecha
- `fecha` falta o no parsea ISO → sanear con fecha actual.

## Auto-sanado — reglas
- Solo tocar `state.json`. Nunca crear ni borrar summary ni skills.
- Solo sanar campos derivables de disco. Ambigüedad → DETENER con reporte.
- Registrar cada saneo en el reporte con evidencia: "V6: skillEspejo corregido → <ruta> (encontrado en disco)".

## Reporte — formato obligatorio
```
architecture-validate: <proyecto>
V1 ✓ state.json parsea
V2 ✓ campos requeridos presentes
V3 ✓ paso="analyze" válido
V4 ✓ resumen en disco: <ruta>
V5 ✓ paso coherente con artefactos
V6 ⚠ skillEspejo corregido → <ruta> (encontrado en disco)
V7 ✓ fecha ISO
Resultado: CONTINUAR
```
Una línea por check, con severidad y evidencia. Resultado final: `CONTINUAR` (sin ✗) o `DETENER` (con ✗ pendientes).

## Regla de oro
- Nunca adivinar: si hay ambigüedad, DETENER y reportar. El orquestador decide.
```

- [ ] **Step 3: Verificar escenarios T1-T8 contra el fixture**

Ejecutar cada escenario manualmente: escribir el `state.json` indicado en `tests/fixture/proyecto-prueba/.architecture-clone/state.json`, cargar el skill architecture-validate, correr los checks con herramientas de lectura, y comparar el reporte contra lo esperado:

| Escenario | state.json inicial | Esperado |
|---|---|---|
| T1 | archivo no existe | V1 ✗, Resultado DETENER, no se crea archivo |
| T2 | `{"proyecto":"...","nombre":"proyecto-prueba","paso":"analyze","fecha":"2026-08-13T10:00:00Z","resumen":"<abs>\\architecture-summary.md"}` con summary presente | V1-V7 ✓, Resultado CONTINUAR, state.json sin cambios |
| T3 | igual a T2 pero `resumen` apunta a ruta muerta; summary único en `.architecture-clone/` | V4 sana ruta, Resultado CONTINUAR, state.json con resumen corregido |
| T4 | igual a T3 pero sin summary en disco | V4 ✗, Resultado DETENER |
| T5 | `paso:"listo"`, `skillGenerada` ruta muerta, `skillEspejo` ausente; `.claude/skills/proyecto-prueba-convenciones/SKILL.md` y `.opencode/skills/proyecto-prueba-convenciones/SKILL.md` en disco | V6 sana ambos, Resultado CONTINUAR |
| T6 | `paso:"listo"`, ambas skills borradas, summary en disco | V5 recalcula a "analyze", ⚠, Resultado CONTINUAR (orquestador ofrecerá regenerar) |
| T7 | `fecha:"2026/13/08"` (no ISO) | V7 sana con fecha actual ISO |
| T8 | `paso:"generar"` | V3 ✗, Resultado DETENER, state.json sin tocar |

Para T1: `Remove-Item tests/fixture/proyecto-prueba/.architecture-clone/state.json -ErrorAction SilentlyContinue`.
Para cada escenario: tras la verificación, restaurar `state.json` de T2 como base.

- [ ] **Step 4: Commit**

```bash
git add skills/architecture-validate/SKILL.md tests/fixture/
git commit -m "feat: skill architecture-validate - checks V1-V7 de continuidad + auto-sanado"
```

---

### Task 3: Orquestador — flujo de 3 fases (F1, F4)

**Files:**
- Modify: `architecture-clone-plugins/agent/architecture-clone.md`

**Interfaces:**
- Consumes: Task 2 (reporte de validate: `Resultado: CONTINUAR|DETENER`), Task 1 (enum sin "generate")
- Produces: secuencia validate → analyze → generate; decisión por artefactos en disco; ruta de re-análisis

- [ ] **Step 1: Reescribir el flujo del orquestador**

Contenido final completo de `agent/architecture-clone.md`:

```markdown
---
description: Arquitecto de software senior: analiza la arquitectura de un proyecto y genera un skill de convenciones para que el código nuevo siga el mismo patrón. Respuesta a "clona la arquitectura", "analiza la arquitectura de", "genera el skill de convenciones", "re-analiza".
mode: primary
---

Eres arquitecto de software senior especializado en ingeniería inversa de codebases. Trabajas con el sistema architecture-clone.

## Comportamiento (crítico)
- Habla como arquitecto con años de experiencia: directo, técnico pero claro, cero jerga innecesaria
- Una pregunta por turno, con opciones concretas
- Confirmas antes de cada fase ("¿Analizo la estructura y el stack?")
- Justificas decisiones como humano ("patrón por capas porque este dominio exige separación estricta")
- Ante pedido vago ("clona la arquitectura"), pides el proyecto concreto antes de empezar

## Flujo (3 fases: validate → analyze → generate)
1. SIEMPRE cargar skill architecture-validate al inicio de CADA fase (validate antes de analyze, validate antes de generate, validate al final)
2. Determinar proyecto objetivo: el proyecto actual si el usuario no da ruta explícita
3. Si el reporte de validate dice `Resultado: DETENER` → no avanzar: mostrar el reporte, explicar qué falta y pedir decisión
4. Si `Resultado: CONTINUAR`, decidir la skill del paso según state.json.paso Y los artefactos en disco (nunca por un valor "generate"):
   - sin state.json o `paso:"analyze"` sin summary → architecture-analyze
   - `paso:"analyze"` con summary en disco → architecture-generate (el análisis ya está completo)
   - `paso:"listo"` → el pipeline está terminado; ofrecer:
     - "regenerar el skill" (architecture-generate, sin re-analizar) si el summary sigue válido
     - "re-analizar" si la arquitectura cambió: confirmar con el usuario y forzar `paso:"analyze"` en state.json antes de cargar architecture-analyze
5. Cargar y ejecutar una skill a la vez; nunca dos simultáneas
6. Reportar avance en lenguaje humano

## Límites
- No inventar convenciones: todo lo que entra en el skill generado debe venir del análisis real del código
- No analizar carpetas de dependencias (node_modules, vendor, .git…) salvo que aporten decisiones de arquitectura
- No prometer que el skill generado se cargará solo: explicar al usuario dónde quedó y que OpenCode lo detecta en la siguiente sesión del proyecto
- Nunca avanzar con un ✗ bloqueante pendiente del reporte de validate
```

- [ ] **Step 2: Verificar escenario T10**

Simular: `state.json` con `paso:"listo"` y skills en disco (fixture T5). Pedido del usuario: "re-analiza la arquitectura".
Esperado según el orquestador: validate corre, reporta CONTINUAR; orquestador ofrece "re-analizar"; tras confirmación, `paso` se fuerza a `"analyze"` y se carga architecture-analyze. Verificar que el flujo descrito en el markdown produce esa secuencia.

- [ ] **Step 3: Commit**

```bash
git add agent/architecture-clone.md
git commit -m "feat: orquestador 3 fases - validate al inicio de cada paso, decisión por artefactos, re-análisis"
```

---

### Task 4: architecture-analyze — checkpoint progreso (F5)

**Files:**
- Modify: `architecture-clone-plugins/skills/architecture-analyze/SKILL.md`

**Interfaces:**
- Consumes: Task 1 (campo `progreso`, enum `["estructura","stack","testing","resumen"]`)
- Produces: `state.json.progreso` actualizado en cada hito; lectura del checkpoint al retomar

- [ ] **Step 1: Actualizar el skill**

Cambios exactos en `skills/architecture-analyze/SKILL.md`:

1. Reemplazar el bloque "Destino y estado" (líneas 11-14 actuales):

```markdown
## Destino y estado
- Carpeta de estado: `<proyecto>/.architecture-clone/` (crear si falta)
- Escribir `state.json` al terminar con: `proyecto` (ruta absoluta), `nombre` (slug kebab-case), `paso: "analyze"`, `resumen` (ruta al summary), `fecha` (ISO). Respetar `state.schema.json` del plugin.
- Checkpoint `progreso`: actualizarlo en CADA hito del análisis — `estructura` (dimensiones 1-3), `stack` (4-6), `testing` (7-8), `resumen` (9 + escritura del summary). Si una pasada se interrumpe, retomar desde el checkpoint: NO re-analizar dimensiones ya completadas.
- Si `state.json` existe con `paso: "listo"` o con `progreso: "resumen"` → el análisis está completo; NO ejecutar análisis completo; devolver control al orquestador.
```

2. En "Procedimiento", insertar tras el paso 1:

```markdown
0. Si `state.json.progreso` existe, retomar desde ahí: saltar dimensiones ya completadas y continuar en la siguiente.
```

(El paso 1 existente "Raíz del proyecto" pasa a ser el paso 1 normal; el nuevo paso 0 es el checkpoint.)

- [ ] **Step 2: Verificar escenario T9**

Fixture: `state.json` con `progreso:"estructura"` (dimensiones 1-3 completadas), summary aún no escrito. Esperado: al cargar architecture-analyze, NO re-escanea estructura; arranca en dimensiones 4-6 (stack); al terminar, `progreso:"resumen"` y summary escrito. Verificar que las instrucciones del markdown lo permiten explícitamente.

- [ ] **Step 3: Commit**

```bash
git add skills/architecture-analyze/SKILL.md
git commit -m "feat: analyze checkpoint - retomar pasadas a medias desde state.json.progreso"
```

---

### Task 5: architecture-generate — resumen vía state.json + skillEspejo (F2, F3)

**Files:**
- Modify: `architecture-clone-plugins/skills/architecture-generate/SKILL.md`

**Interfaces:**
- Consumes: Task 1 (`resumen` requerido, `skillEspejo`), Task 4 (`progreso:"resumen"`)
- Produces: `state.json` final con `paso:"listo"`, `skillGenerada`, `skillEspejo`, `fecha`

- [ ] **Step 1: Actualizar el skill**

Cambios exactos en `skills/architecture-generate/SKILL.md`:

1. Reemplazar la sección "Entradas y estado" (líneas 11-14 actuales):

```markdown
## Entradas y estado
- Leer `<proyecto>/.architecture-clone/state.json`; el summary se lee desde la ruta `state.json.resumen` (NUNCA hardcodear la ruta)
- Si no existe `state.json`, o `state.json.resumen` no existe en disco, o `state.json.progreso` no es `"resumen"` → NO ejecutar; decir al usuario que primero corre architecture-analyze (o architecture-validate)
- Slug del proyecto: `state.json.nombre`
```

2. Reemplazar el bloque de actualización final en "Destino" (líneas 21 actuales):

```markdown
Crear carpetas si faltan. Actualizar `state.json` al final: `paso: "listo"`, `skillGenerada` (ruta `.claude/skills/<slug>-convenciones/SKILL.md`), `skillEspejo` (ruta `.opencode/skills/<slug>-convenciones/SKILL.md`), `fecha` ISO.
```

3. En "Checklist de validación", reemplazar la línea de copia espejo:

```markdown
- [ ] Copia espejo escrita en `.claude/skills/` Y `.opencode/skills/`; ambas rutas registradas en `state.json` (`skillGenerada` + `skillEspejo`)
```

- [ ] **Step 2: Verificar escenarios T5/T6 completos**

T5: fixture con `paso:"listo"` y skill espejo faltante → generate completado normal (ambas copias escritas). T6: ambas skills borradas con summary válido → orquestador llama generate directo; generate escribe ambas copias y state.json queda `paso:"listo"` con `skillGenerada` + `skillEspejo` correctos. Verificar contra el fixture.

- [ ] **Step 3: Commit**

```bash
git add skills/architecture-generate/SKILL.md
git commit -m "feat: generate usa state.json.resumen y registra skillEspejo"
```

---

### Task 6: README + suite final (T1-T10)

**Files:**
- Modify: `architecture-clone-plugins/README.md`
- Create: `tests/SCENARIOS.md`

**Interfaces:**
- Consumes: Tasks 1-5 completas
- Produces: documentación del pipeline de 3 fases y suite de escenarios verificable

- [ ] **Step 1: Actualizar README**

Cambios exactos en `README.md`:

1. Línea 5, pipeline:

```markdown
Pipeline: `validar → analizar → resumir → generar skill de convenciones → validar`.
```

2. Tabla del pipeline (líneas 24-28):

```markdown
| Skill | Salida |
|---|---|
| architecture-validate | Reporte V1-V7 de continuidad + auto-sanado de `state.json` |
| architecture-analyze | `<proyecto>/.architecture-clone/state.json` + `architecture-summary.md` |
| architecture-generate | `<proyecto>/.claude/skills/<slug>-convenciones/SKILL.md` + espejo en `.opencode/skills/` |
```

3. Sección "Estado intermedio" (línea 54): añadir mención a `progreso`:

```markdown
`<proyecto>/.architecture-clone/` guarda `state.json` (contrato en `state.schema.json`), `architecture-summary.md` y el checkpoint `progreso`. Versionable con el repo; permite retomar análisis a medias y validar continuidad antes de cada paso.
```

- [ ] **Step 2: Crear suite de escenarios**

`tests/SCENARIOS.md` — checklist T1-T10 para ejecución futura (cada línea checkbox):

```markdown
# Escenarios architecture-validate (T1-T10)

Fixture: `tests/fixture/proyecto-prueba/`. Para cada escenario: escribir el state.json indicado, cargar architecture-validate, correr checks, comparar reporte.

- [ ] T1 state.json no existe → V1 ✗, DETENER, no crea archivo
- [ ] T2 estado sano → V1-V7 ✓, CONTINUAR, sin cambios
- [ ] T3 resumen ruta muerta + 1 summary en disco → V4 sana ruta
- [ ] T4 resumen muerto + 0 summaries → V4 ✗, DETENER
- [ ] T5 paso:"listo" + falta espejo existente en disco → V6 sana skillEspejo
- [ ] T6 paso:"listo" + skills borradas + summary válido → V5 recalcula, orquestador ofrece regenerar
- [ ] T7 fecha no ISO → V7 sana
- [ ] T8 paso inválido → V3 ✗, DETENER, state intacto
- [ ] T9 analyze interrumpido con progreso:"estructura" → retoma desde stack (F5)
- [ ] T10 re-analiza con paso:"listo" → confirmar y forzar analyze (F4)
```

- [ ] **Step 3: Correr suite T1-T10 completa contra el fixture**

Ejecutar los 10 escenarios en orden sobre `tests/fixture/proyecto-prueba/`, usando la verificación manual descrita en Task 2 Step 3 para T1-T8 y Task 4/5 para T9-T10. Cada escenario: reporte de validate registrado en `tests/SCENARIOS.md` como completado. Restaurar el fixture a estado sano (T2) al terminar.

- [ ] **Step 4: Commit**

```bash
git add README.md tests/SCENARIOS.md
git commit -m "docs: README pipeline 3 fases + suite de escenarios T1-T10"
```

---

### Self-Review del plan

**1. Cobertura del spec:**
- V1-V7 (checks) → Task 2 ✓
- F1 (paso sin "generate") → Task 1 + Task 3 ✓
- F2 (resumen vía state.json) → Task 5 ✓
- F3 (skillEspejo) → Task 1 + Task 5 ✓
- F4 (re-análisis) → Task 3 ✓
- F5 (checkpoint) → Task 1 + Task 4 ✓
- F6 (resumen requerido) → Task 1 ✓
- Errores/auto-sanado → Task 2 (reglas) ✓
- T1-T10 → Task 2 (T1-T8), Task 3 (T10), Task 4 (T9), Task 5 (T5/T6), Task 6 (suite completa) ✓
- Fuera de alcance respetado: sin scripts ✓

**2. Placeholders:** sin TBD/TODO; todo paso con contenido completo (SKILL.md enteros, schema entero, fixture con contenido de ejemplo) ✓

**3. Consistencia de tipos/nombres:** `progreso` enum `["estructura","stack","testing","resumen"]` definido en Task 1 y usado igual en Tasks 4 y 5; `skillEspejo` definido en Task 1, usado en Tasks 2, 3, 5; `paso` enum `["analyze","listo"]` consistente en Tasks 1-3; reporte `Resultado: CONTINUAR|DETENER` producido en Task 2 y consumido en Task 3 ✓
