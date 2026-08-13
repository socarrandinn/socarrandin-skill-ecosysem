# Diseño: architecture-clone-plugins

Fecha: 2026-08-13
Estado: aprobado

## Propósito

Plugin que empaqueta un ecosistema de skills de OpenCode/Claude para analizar la arquitectura de un proyecto completo y generar un skill de convenciones reutilizable (SKILL.md) que los agentes cargan en sesiones futuras para escribir código consistente con esa arquitectura.

## Decisiones (brainstorming)

| Decisión | Elección |
|---|---|
| Destino del skill generado | Dentro del proyecto analizado |
| Idioma | Español (consistente con ecosistema ebook-studio) |
| Granularidad | 2 skills + agente orquestador (patrón ebook-studio) |
| Estado intermedio | `<proyecto>/.architecture-clone/` (hidden dir versionable) |

## Repo layout

```
architecture-clone-plugins/
  agent/architecture-clone.md        # orquestador (primary agent)
  command/architecture-clone.md      # /architecture-clone
  skills/
    architecture-analyze/SKILL.md    # 1: analiza → resumen + state.json
    architecture-generate/SKILL.md   # 2: resumen → SKILL.md convenciones
  state.schema.json                  # contrato state.json
  README.md  LICENSE (MIT)  .gitignore
```

## Flujo

```
"clona la arquitectura de este proyecto"
  → orquestador (agent/architecture-clone.md)
    1. carga architecture-analyze → analiza → escribe:
         <proyecto>/.architecture-clone/state.json (paso:"analyze")
         <proyecto>/.architecture-clone/architecture-summary.md
    2. carga architecture-generate → genera skill de convenciones en:
         <proyecto>/.claude/skills/<slug>-convenciones/SKILL.md
         <proyecto>/.opencode/skills/<slug>-convenciones/SKILL.md  (espejo)
    3. resume vía state.json.paso (analyze → continuar; generate/listo → regenerar skill)
```

## architecture-analyze — dimensiones de análisis

1. Estructura de carpetas + convenciones de nombres
2. Tech stack (lenguajes, frameworks, runtimes, build tools) + versiones
3. Dependencias / gestor de paquetes
4. Patrones de diseño del sistema (MVC, capas, microservicios, hexagonal…)
5. Manejo de estado
6. API/servicios: diseño y convenciones de rutas
7. Modelos de datos / esquemas
8. Testing: frameworks, ubicación, convenciones
9. Config y entorno (CI/CD, env vars, scripts de build)

Salida = patrones y decisiones ("cómo se construye esto"), NO inventario archivo-por-archivo. Formato de salida = receta positiva (contrato de secciones), no prohibiciones.

## architecture-generate — artefacto generado

SKILL.md de convenciones con:

- Frontmatter: `name: <slug>-convenciones`, `description: Use when…` (tercera persona, triggers, keywords del proyecto)
- Quick reference de convenciones (tabla escaneable)
- Reglas concretas extraídas del análisis
- Ejemplo(s) de código típico del proyecto
- Idioma español

Escribir copia espejo en `.claude/skills/` (Claude Code) y `.opencode/skills/` (opencode).

## state.json

```json
{ "proyecto": "ruta abs", "nombre": "slug", "paso": "analyze|generate|listo",
  "resumen": "ruta summary", "skillGenerada": "ruta", "fecha": "ISO" }
```

Claves en español, consistente con ebook-studio. Contrato documentado en `state.schema.json` (informativo, sin validación runtime — igual que ebook-studio).

## Testing (writing-skills Iron Law)

- RED: fixture repo → agente fresco sin skill de convenciones escribe código nuevo → documentar violaciones verbatim
- GREEN: pipeline genera skill → mismo escenario → verificar cumplimiento
- Validar SKILL.md generado: frontmatter bien formado, `name` == carpeta, `description` con trigger

## Fuera de alcance

- Scripts Python (análisis lo hace el agente con herramientas de lectura)
- Validación runtime del state.json
- Detección de idioma del proyecto analizado (output siempre en español)