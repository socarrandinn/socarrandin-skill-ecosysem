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
