---
name: architecture-generate
description: Use cuando existe un resumen de arquitectura (architecture-summary.md + state.json en .architecture-clone/) y hay que generar el SKILL.md de convenciones del proyecto: "genera el skill de convenciones", "genera el skill".
---

# architecture-generate

## Misión
Convertir el `architecture-summary.md` en un SKILL.md de convenciones reutilizable: en sesiones futuras, el agente lo carga y escribe código nuevo consistente con la arquitectura analizada.

## Entradas y estado
- Leer `<proyecto>/.architecture-clone/state.json`; el summary se lee desde la ruta `state.json.resumen` (NUNCA hardcodear la ruta)
- Si no existe `state.json`, o `state.json.resumen` no existe en disco, o `state.json.progreso` no es `"resumen"` → NO ejecutar; decir al usuario que primero corre architecture-analyze (o architecture-validate)
- Slug del proyecto: `state.json.nombre`

## Destino (espejo en ambas ubicaciones)
Escribir el MISMO contenido en:
1. `<proyecto>/.claude/skills/<slug>-convenciones/SKILL.md` (Claude Code)
2. `<proyecto>/.opencode/skills/<slug>-convenciones/SKILL.md` (OpenCode)

Crear carpetas si faltan. Actualizar `state.json` al final: `paso: "listo"`, `skillGenerada` (ruta `.claude/skills/<slug>-convenciones/SKILL.md`), `skillEspejo` (ruta `.opencode/skills/<slug>-convenciones/SKILL.md`), `fecha` ISO.

## Contrato del SKILL.md generado — estructura EXACTA

```markdown
---
name: <slug>-convenciones
description: Use when escribiendo, editando o revisando código en <proyecto>. <2-4 keywords concretas del stack: ej. "Express, TypeScript, Zod, vitest">
---

# <slug>-convenciones

## Visión general
<1-2 frases: qué hace el proyecto, qué arquitectura usa>

## Reglas de oro (no negociables)
<tabla o lista: las reglas de oro del summary, en lenguaje de orden: "Siempre…", "Nunca…">

## Estructura y nombres
<dónde va cada tipo de archivo, patrón de nombres, imports/exports>

## Stack y dependencias
<lenguajes, frameworks, versiones, gestor de paquetes, comandos de build/dev/test>

## Patrones de diseño
<patrón del sistema + flujo de una petición típica: paso a paso con capas>

## Manejo de estado
<si aplica>

## API y servicios
<prefijos de ruta, envoltura de respuestas, códigos de error, auth>

## Datos y validación
<models, schemas, validación, migraciones>

## Testing
<framework, ubicación, nombres de archivo, patrón, comando>

## Config y entorno
<env vars, CI/CD, scripts, lint/format>

## Ejemplos de código
<2-3 ejemplos REALES adaptados del proyecto: un controller típico, un test típico, una ruta típica — copiar la forma real del código, no inventar estilos>
```

## Reglas de generación
- `name` = `<slug>-convenciones` exacto, en minúsculas con guiones. `description` empieza con "Use when", tercera persona, incluye triggers con los keywords del proyecto
- Cada regla debe derivarse del summary — NO inventar convenciones nuevas
- Lenguaje de órdenes concretas: "Siempre X", "Nunca Y", "Todo endpoint Z" — no sugerencias ("considerar…")
- Ejemplos de código: copiar LITERALMENTE de archivos reales del proyecto (un controller, una ruta, un test, un validator). Abrir el archivo real y copiar su contenido, renombrando solo el recurso si se necesita. PROHIBIDO reconstruir ejemplos de memoria o inventar campos que no existen en el código real

## Checklist de validación (OBLIGATORIO antes de terminar)
- [ ] Frontmatter YAML válido: `name` y `description` presentes, sin tabulaciones
- [ ] `name` == nombre de la carpeta donde se escribe
- [ ] `description` empieza con "Use when" y menciona el proyecto
- [ ] Existen TODAS las secciones del contrato (ninguna omitida; "No aplica" en una línea si no corresponde)
- [ ] Reglas de oro presentes y no negociables
- [ ] Ejemplos de código copiados literalmente de archivos reales (verificar contra los archivos fuente: imports, campos, rutas)
- [ ] Copia espejo escrita en `.claude/skills/` Y `.opencode/skills/`; ambas rutas registradas en `state.json` (`skillGenerada` + `skillEspejo`)
- [ ] `state.json` actualizado (`paso: "listo"`, `skillGenerada`, `skillEspejo`, `fecha`)

## Regla de oro
- Si falta el summary o el estado → no inventar: pedir el análisis.
