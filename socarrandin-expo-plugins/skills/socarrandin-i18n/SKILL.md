---
name: socarrandin-i18n
description: Usar al agregar textos traducibles, cambiar idioma o configurar i18n en apps del monorepo socarrandin-expo-ecosystem. Obliga a I18nProvider + useI18n de @socarrandin/i18n (i18next) en lugar de strings hardcodeados o estado de idioma manual. Triggers: t(), traducciones, textos, cambiar idioma, locale, resources i18n.
---

# socarrandin-i18n

## Regla de oro

**Ningún string de UI hardcodeado en código de app**: todo texto visible pasa por `t()` de `useI18n()`. **El idioma se maneja con `I18nProvider` + `useI18n().setLocale`** — nunca estado global propio ni AsyncStorage manual.

## Cuándo usar

- Cualquier label, placeholder, título, mensaje → `t("namespace:key")`
- Cualquier pantalla de cambio de idioma → `setLocale`
- Configurar i18n de una app → `I18nProvider` en la raíz
- Recursos de traducción tipados → `defineResources`
- Traducción de errores → keys `errors:*` consumidas por `ErrorAlert`/`useErrorResolver` (ver socarrandin-theme)

## API (packages/i18n/src)

| API | Uso |
|---|---|
| `I18nProvider` | `resources: Record<L, Resource>`, `defaultLanguage`, `supportedLanguages: readonly L[]`, `persistenceKey?` (default `@socarrandin/i18n/locale`), `children` |
| `useI18n<L>()` | `{ t, locale: L, setLocale(locale), ready }` |
| `defineResources(resources)` | helper de tipos para resources |
| `SupportedLocales` | tipo `keyof resources & string` |
| `DEFAULT_PERSISTENCE_KEY` | `@socarrandin/i18n/locale` |

Comportamiento del provider:
- Crea instancia i18next propia (nunca el singleton global)
- Idioma inicial: locale del dispositivo si está en `supportedLanguages`, si no `defaultLanguage`
- Al montar, restaura locale persistido (SecureStore native / localStorage web)
- `setLocale` persiste + cambia idioma (validando contra `supportedLanguages`)

## Patrón correcto

```tsx
// resources tipados (app)
import { defineResources } from "@socarrandin/i18n";

const resources = defineResources({
  es: {
    home: { newMeasurement: "Nueva medición", search: "Buscar" },
    errors: { auth: { invalidCredentials: { title: "Error de acceso", description: "Credenciales inválidas" } } },
  },
  en: {
    home: { newMeasurement: "New measurement", search: "Search" },
    errors: { auth: { invalidCredentials: { title: "Sign-in error", description: "Invalid credentials" } } },
  },
} as const);
```

```tsx
// Raíz de la app
<I18nProvider
  resources={resources}
  defaultLanguage="es"
  supportedLanguages={["es", "en"]}
>
  <App />
</I18nProvider>
```

```tsx
// Dentro de componentes
const { t, locale, setLocale, ready } = useI18n();

<Text>{t("home:newMeasurement")}</Text>

// cambio de idioma
await setLocale(locale === "es" ? "en" : "es");

// interpolación
t("profile:ageLabel", { count: age })
```

## Anti-patterns (prohibidos)

| Anti-pattern | Fix |
|---|---|
| String hardcodeado en JSX (`"Guardar"`, `"Buscar"`) | `t("namespace:key")` |
| Estado de idioma con useState/Context propio | `useI18n().setLocale` |
| Persistir idioma con AsyncStorage a mano | `I18nProvider` ya persiste |
| `i18next` singleton importado directo | `useI18n()` (instancia del provider) |
| `t` de react-i18next directo | `useI18n()` (mismo resultado, un solo punto de acceso) |

## Errores comunes

- Keys con namespace: formato `namespace:key` (ej. `"ui:forms.searchPlaceholder"`, `"errors:validation.title"`). Los componentes del ui usan namespace `ui:` — la app debe incluir esos resources o pasar textos explícitos.
- `setLocale` es async y valida contra `supportedLanguages`: idiomas no soportados se ignoran silenciosamente.
- El locale inicial es el del dispositivo si está soportado: no asumir `defaultLanguage` al primer render.
- `ready` indica si la instancia terminó de inicializar — renderizar con fallback si se depende del idioma inicial.
- `defineResources` da tipado completo: usarlo para que `t()` valide keys en dev.

## Verificación

- `npm run typecheck` limpio (desde raíz del repo)
- `git grep -n '"[A-Z][a-z ]*"' apps/*/src` — strings largos en JSX deben ser keys `t(...)` o datos, no UI copy
- Un solo `I18nProvider` en la raíz de cada app
- Ningún `AsyncStorage` para locale