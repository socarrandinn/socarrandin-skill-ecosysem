---
name: socarrandin-theme
description: Usar al trabajar con colores, tema claro/oscuro, tipografía, spacing o presentación de errores en apps del monorepo socarrandin-expo-ecosystem. Obliga a tokens de @socarrandin/ui (useAppColors, ThemeProvider, useTheme, Fonts, Spacing, Radii) y al sistema de errores (ErrorAlert, useErrorResolver) en lugar de hex hardcodeados o manejo de errores manual. Triggers: colores, dark mode, cambiar tema, estilo de texto, mostrar error de API, alert de error, error resolver.
---

# socarrandin-theme

## Regla de oro

**Ningún color hex ni font family en código de app**: todo color sale de `useAppColors()` (o la paleta custom de la app vía `ThemeProvider`), toda tipografía de `Text`/`useThemeFonts()`. **Ningún error se muestra a mano**: pasa por `ErrorAlert`/`useErrorResolver`.

## Cuándo usar

- Cualquier color de estilo → token de `useAppColors()` (kebab, ej. `colors.muted`, `colors["field-border"]`)
- Cambio de tema claro/oscuro → `ThemeProvider` + `useThemeScheme()` / `setScheme`
- Tipografía → `Text` con `type`/`weight` (ver socarrandin-ui) o `useThemeFonts()`
- Spacing/radii → `Spacing` / `Radii` de `@socarrandin/ui`
- Mostrar error (API, red, validación) → `ErrorAlert` + `useErrorResolver`
- Mapear códigos de error a mensajes → `ErrorMap` (references + statusCodes)

## Theme (packages/ui/src/theme)

| API | Uso |
|---|---|
| `ThemeProvider` | `scheme` (default "dark"), `colors: Record<ThemeScheme, ThemeColors>`, `fonts` — la app registra sus paletas; default `Colors`/`Fonts` |
| `useTheme()` | `ThemeColors` del scheme activo (estructura anidada: base, surface, accent, status, neutral, field, soft, border, misc) |
| `useAppColors()` | record PLANO kebab de ~60 tokens (`background`, `foreground`, `accent`, `muted`, `danger`, `field`, `field-border`, `default-hover`, `accent-soft`…) — el que usan los componentes y la app |
| `useThemeScheme()` / `setScheme` | leer/cambiar scheme (ThemeProvider lo provee) |
| `useThemeFonts()` | `sans`, `sansMedium`, `sansSemibold`, `sansBold` |
| `Spacing` | tokens de spacing (ej. `Spacing.one`, `Spacing.two`) |
| `Radii` | tokens de radio (ej. `Radii.sm`) |
| `Typography` | presets tipográficos |

## Errores (packages/ui/src/errors)

| API | Uso |
|---|---|
| `ErrorAlert` | `error`, `errors?: ErrorMap`, `localMap?`, `onClose`, `showIcon`, `iconSize`, `defaultSeverity`; renderiza `Alert` con status mapeado; no renderiza nada si `error` falsy |
| `useErrorResolver(error, {localMap, iconSize, defaultSeverity})` | devuelve `{status: "accent"\|"warning"\|"danger"\|"success", errorPresentation: {title, description, icon, severity, dismissible}}` |
| `resolveError(error, options)` | función pura de resolución |
| `ErrorMap` | `{ references?: Record<string, ErrorMapEntry>, statusCodes?: Record<number, ErrorMapEntry> }`; `ErrorMapEntry = {title, description, iconKey?, severity, dismissible?}` |

Resolver busca por `reference`/`key` primero, luego `statusCode`; fallback con strings en español traducibles vía `translate` (usa `t()` del i18n). Iconos built-in por `iconKey` (wifi-off, lock, mail, shield-x, user-x, server-crash, alert-circle, …).

## Patrón correcto

```tsx
// Root de la app
<ThemeProvider scheme="dark">
  <QueryClientProvider client={queryClient}>
    <I18nProvider>
      <App />
    </I18nProvider>
  </QueryClientProvider>
</ThemeProvider>
```

```tsx
// Colores dentro del componente (nunca en StyleSheet de módulo)
const colors = useAppColors();
const [pressed, setPressed] = useState(false);
// style={[styles.base, { backgroundColor: colors.accent, color: colors["accent-foreground"] }]}
```

```tsx
// Error de API tipado a presentación
const { status, errorPresentation } = useErrorResolver(error, {
  localMap: {
    references: {
      VALIDATION: { title: t("errors:validation.title"), description: t("errors:validation.description"), iconKey: "alert-triangle", severity: "warning" },
    },
    statusCodes: {
      401: { title: t("errors:auth.title"), description: t("errors:auth.unauthorized"), iconKey: "lock", severity: "danger" },
    },
  },
});

// o directo:
<ErrorAlert error={error} errors={{ references: {...}, statusCodes: {...} }} onClose={() => setError(null)} />
```

## Anti-patterns (prohibidos)

| Anti-pattern | Fix |
|---|---|
| Hex hardcodeado `#5B6478` en estilos | token de `useAppColors()` |
| `StyleSheet.create` a nivel módulo con `useAppColors()` | array de estilos dentro del componente |
| Font family hardcodeada (ej. `Mulish_600SemiBold`) | `Text` con `type`/`weight` o `useThemeFonts()` |
| Alert/Modal de error hecho a mano | `ErrorAlert` |
| `console.log(error)` + mensaje genérico | `useErrorResolver` + `ErrorAlert` |
| Mapear status codes en cada pantalla | `ErrorMap` compartido + `ErrorAlert` |
| Tema con estado global propio (context a mano) | `ThemeProvider` de `@socarrandin/ui` |

## Errores comunes

- `useAppColors` devuelve record con keys kebab: acceder `colors["field-border"]`, `colors["accent-foreground"]` (no camelCase).
- `ThemeProvider` default scheme es `"dark"`: apps con light mode deben setearlo explícitamente.
- `ErrorAlert.errors` y `localMap` se fusionan: `errors` gana sobre `localMap`.
- `title`/`description` de `ErrorMapEntry` son keys de i18n o strings directos — el resolver los traduce con `t()` cuando hay `translate`.
- `useErrorResolver` memoiza: pasa `error` estable (no crear objeto nuevo en cada render).
- Cambiar `scheme` con `setScheme` re-resuelve `useAppColors` automáticamente en toda la app.

## Verificación

- `npm run typecheck` limpio (desde raíz del repo)
- `git grep -n "#[0-9A-Fa-f]\{6\}" apps/*/src` sin matches fuera de paleta definida en la app
- Ningún `Alert.alert`/Modal manual para errores de API — `ErrorAlert`
- Estilos con colores: `useAppColors()` dentro del componente