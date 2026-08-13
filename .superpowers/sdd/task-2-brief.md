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
