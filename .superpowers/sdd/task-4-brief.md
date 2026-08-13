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
