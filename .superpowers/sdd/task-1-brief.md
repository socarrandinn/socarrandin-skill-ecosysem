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
