# architecture-clone-plugins

Ecosistema de skills para OpenCode/Claude Code que analiza la arquitectura de un proyecto y genera un skill de convenciones reutilizable: en sesiones futuras, el agente carga ese skill y escribe código nuevo consistente con "cómo se construye" ese proyecto.

Pipeline: `validar → analizar → resumir → generar skill de convenciones → validar`.

## Instalación

1. Copiar `agent/`, `command/` y `skills/` a tu carpeta de skills de OpenCode (ej. `~/.config/opencode/skills/`), o usar el repo como carpeta de skills vía `skills.paths` en `opencode.json`.
2. Reiniciar OpenCode.

## Uso

```
clona la arquitectura de este proyecto
/architecture-clone
analiza la arquitectura de <ruta>
```

El orquestador (`architecture-clone`) decide la skill del paso actual según `state.json`. Una skill activa por turno.

## Pipeline

| Skill | Salida |
|---|---|
| architecture-validate | Reporte V1-V7 de continuidad + auto-sanado de `state.json` |
| architecture-analyze | `<proyecto>/.architecture-clone/state.json` + `architecture-summary.md` |
| architecture-generate | `<proyecto>/.claude/skills/<slug>-convenciones/SKILL.md` + espejo en `.opencode/skills/` |

## Qué analiza `architecture-analyze`

- Estructura de carpetas y convenciones de nombres
- Tech stack (lenguajes, frameworks, runtimes, build tools) con versiones
- Dependencias y gestor de paquetes
- Patrones de diseño del sistema (MVC, capas, microservicios, hexagonal…)
- Manejo de estado
- Diseño de API/servicios y convenciones de rutas
- Modelos de datos / esquemas
- Testing: frameworks, ubicación, convenciones
- Config y entorno (CI/CD, env vars, scripts de build)

El resumen documenta **patrones y decisiones**, no un inventario archivo por archivo.

## Skill generado

`<slug>-convenciones` es un SKILL.md estándar (frontmatter `name` + `description`, quick reference de convenciones, reglas concretas y ejemplos de código típicos). Se escribe en dos ubicaciones para que lo cargue cualquier harness:

| Ubicación | Harness |
|---|---|
| `<proyecto>/.claude/skills/<slug>-convenciones/SKILL.md` | Claude Code |
| `<proyecto>/.opencode/skills/<slug>-convenciones/SKILL.md` | OpenCode (auto-detectado) |

## Estado intermedio

`<proyecto>/.architecture-clone/` guarda `state.json` (contrato en `state.schema.json`), `architecture-summary.md` y el checkpoint `progreso`. Versionable con el repo; permite retomar análisis a medias y validar continuidad antes de cada paso.

## Limitaciones conocidas

- `state.schema.json` es informativo: no hay validación en runtime.
- El resumen y el skill generado se escriben en español, independientemente del idioma del código analizado.
- El análisis lo hace el agente con sus herramientas de lectura; proyectos muy grandes pueden requerir varias pasadas.

## Licencia

MIT.