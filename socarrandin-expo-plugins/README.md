# socarrandin-expo-plugins

Ecosistema de skills para OpenCode/Claude Code que enseña al agente a usar correctamente los packages `@socarrandin/*` del monorepo `socarrandin-expo-ecosystem`: imports correctos, providers requeridos, patrones de uso con evidencia en el código real y anti-patterns prohibidos.

Pipeline de mantenimiento: `usar → (sync) → re-curzar contra packages/src → desplegar a .agents/skills y .claude/skills`.

## Instalación

1. Copiar `agent/`, `command/` y `skills/` a tu carpeta de skills de OpenCode (ej. `~/.config/opencode/skills/`), o usar el repo como carpeta de skills vía `skills.paths` en `opencode.json`.
2. En el proyecto app (ej. `socarrandin-expo-ecosystem/apps/percentil`), desplegar los skills de área a `.agents/skills/` y `.claude/skills/` con `socarrandin-sync`.
3. Reiniciar OpenCode.

## Uso

```
usa los packages @socarrandin para esta pantalla
/socarrandin-usar
escribe un form con los packages del ecosistema
```

El orquestador (`socarrandin-usar`) decide el skill de área según el task. Una skill activa por turno.

## Skills

| Skill | Área |
|---|---|
| socarrandin-forms | Form + campos RHF (react-hook-form + zod) |
| socarrandin-upload | Upload de imágenes (grid, crop, picker) |
| socarrandin-api | authApi, driverApi, resourcesApi, queryClient, tokens, refresh |
| socarrandin-ui | Primitivas generales (Button, Input, Grid, SearchField…) |
| socarrandin-theme | Theme, useAppColors, ErrorAlert, useErrorResolver |
| socarrandin-i18n | I18nProvider, useI18n, persistencia de idioma |
| socarrandin-utils | cn(), hooks, styles, tipos comunes |
| socarrandin-sync | Re-curza skills contra `packages/*/src/` y despliega copias |

## Mantenimiento

Cada skill de área documenta **patrones con evidencia**: cada convención declarada debe trazarse a un archivo real de `socarrandin-expo-ecosystem/packages/*/src/` (`archivo.tsx:linea`). Cuando los packages cambian:

1. Ejecutar `socarrandin-sync`: re-lee `packages/*/src/`, verifica que cada patrón y ruta citada siga vigente, actualiza el contenido y despliega a `.agents/skills/` y `.claude/skills/`.
2. Correr los escenarios de `tests/SCENARIOS.md` contra las apps reales.

## Limitaciones conocidas

- Los skills documentan patrones de uso, no un inventario exhaustivo de props: consultar el código del package para firmas completas.
- `socarrandin-sync` re-curza contenido guiado por el agente; no es un diff automático.

## Licencia

MIT.