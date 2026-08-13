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
