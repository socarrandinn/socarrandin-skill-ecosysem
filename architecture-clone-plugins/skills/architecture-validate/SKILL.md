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
- `paso:"listo"` y no existe ningún `*-convenciones/SKILL.md` → ⚠: si el summary existe en disco, recalcular `paso:"analyze"` Y sanear `progreso:"resumen"` (el summary en disco implica análisis completo), reportar "V5: paso recalculado a analyze y progreso a resumen (skills ausentes); regenerar skill con architecture-generate".
- `paso:"analyze"` y existe `*-convenciones/SKILL.md` → ⚠: recalcular a `paso:"listo"` y rellenar `skillGenerada`/`skillEspejo` desde disco (ver V6).

### V6 — rutas de skill viven en disco (solo si `paso:"listo"` o si los campos existen en state.json; con `paso:"analyze"` y sin campos, marcar ✓ — las skills aún no se generan)
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