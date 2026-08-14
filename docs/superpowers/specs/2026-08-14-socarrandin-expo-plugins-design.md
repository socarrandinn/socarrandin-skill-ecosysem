# Diseño: socarrandin-expo-plugins

Fecha: 2026-08-14

## Propósito

Plugin de skills para OpenCode/Claude Code que enseña al agente a usar correctamente los packages `@socarrandin/*` del monorepo `socarrandin-expo-ecosystem` (ui, api, i18n, utils, types). El agente escribe código de app con imports, providers y patrones reales del library — nunca reimplementa controles, HTTP, i18n o utilidades.

## Decisiones tomadas

| Decisión | Valor |
|---|---|
| Propósito | Skills de uso/convenciones, estáticos, autocurrados del código real |
| Estructura | Orquestador + skills por área |
| Áreas | forms, upload, api+auth, ui (primitivas), theme+errores, i18n, utils+types |
| Profundidad | Patrones de uso + ejemplos con evidencia; sin inventario exhaustivo de props |
| Ubicación | `E:\MY\_TOOLS\socarrandin-skills-ecosysem\socarrandin-expo-plugins\` (hermano de architecture-clone-plugins) |
| Skill existente `socarrandin-ui` | Absorbido y reubicado como skill de área del plugin (traducido a español) |
| Sincronización | Skill `socarrandin-sync`: re-curza contra `packages/*/src` y despliega a `.agents/skills` + `.claude/skills` |
| Idioma | Español (convención del ecosistema) |
| Tests | `tests/SCENARIOS.md` contra apps reales (percentil, trici-go-driver) |

## Arquitectura

```
socarrandin-expo-plugins/
├── README.md / LICENSE / .gitignore
├── agent/socarrandin-usar.md       # orquestador: decide skill de área por task
├── command/socarrandin-usar.md     # /socarrandin-usar → agente
├── skills/
│   ├── socarrandin-forms/          # RHF + zod + campos Form*
│   ├── socarrandin-upload/         # ImageGridUploader, AvatarUploader, CropModal, hooks
│   ├── socarrandin-api/            # authApi, driverApi, resourcesApi, queryClient, tokens
│   ├── socarrandin-ui/             # Button, Input, Select, Grid, SearchField, Text…
│   ├── socarrandin-theme/          # useAppColors, ThemeProvider, ErrorAlert, useErrorResolver
│   ├── socarrandin-i18n/           # I18nProvider, useI18n
│   ├── socarrandin-utils/          # cn, mergeStyles, hooks + tipos (types)
│   └── socarrandin-sync/           # re-curzar + deploy
└── tests/SCENARIOS.md              # T1-T10 contra apps reales
```

## Contrato por skill de área

- Imports correctos solo desde `@socarrandin/<pkg>`
- Providers/wrappers requeridos (I18nProvider, QueryClientProvider, ThemeProvider, GestureHandlerRootView…)
- Patrones de uso con ejemplos trazables a `packages/*/src/*.tsx:linea`
- Anti-patterns/gotchas encontrados en las apps reales
- Verificación (typecheck + grep de anti-patterns)

## Orquestador

Como architecture-clone: una skill activa por turno, decisión por contenido del task (dominante: form → forms, subida → upload, HTTP → api, etc.). Sin `state.json` — no es pipeline multi-fase.

## Sincronización

`socarrandin-sync`: fuente de verdad = `skills/` del plugin. Verifica vigencia de imports y evidencias en `packages/*/src`, re-curza contenido si hubo drift, y copia a `.agents/skills/` y `.claude/skills/`. Nunca editar los destinos a mano.

## Evidencia clave (rutas citadas en skills)

- `packages/ui/src/forms/*` — Form, campos Form*, dates utils
- `packages/ui/src/components/upload/**` — grid, hooks, CropModal, PickSourceSheet, avatar
- `packages/ui/src/components/controls/button.tsx`, `inputs/search-field.tsx`, `layout/grid.tsx`, `typography/text.tsx`
- `packages/ui/src/theme/*` y `errors/*` — useAppColors, ThemeProvider, ErrorAlert, useErrorResolver
- `packages/api/src/*` — authApi, driverApi, resourcesApi, client/fetch, client/http, tokens, refresh, queryClient, config
- `packages/i18n/src/*` — I18nProvider, useI18n, defineResources
- `packages/utils/src/*` + `packages/types/src/*` — cn, mergeStyles, hooks, tipos de imagen

## Fuera de alcance

- glass-v2 (no seleccionado)
- Referencia exhaustiva de props (los skills documentan patrones; firmas completas se consultan en el código)
- Scaffolder de código (solo documentación de uso)
- state.json / pipeline multi-fase