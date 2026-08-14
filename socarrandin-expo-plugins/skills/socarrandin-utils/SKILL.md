---
name: socarrandin-utils
description: Usar al necesitar utilidades compartidas o tipos comunes en apps del monorepo socarrandin-expo-ecosystem: cn(), mergeStyles, useDebouncedValue, useTheme, y tipos IImage/IImageMedia/IPhoto. Obliga a importar desde @socarrandin/utils y @socarrandin/types en lugar de reimplementar utilidades o definir tipos duplicados. Triggers: merge de clases, condicional de estilos, debounce, tipos de imagen, tipos comunes.
---

# socarrandin-utils

## Regla de oro

**Toda utilidad compartida y tipo común viene de `@socarrandin/utils` y `@socarrandin/types`** — nunca reimplementar `cn`/merge de estilos, debounce, o definir tipos de imagen/entidades que ya existen en los packages.

## Cuándo usar

- Combinar clases/condicionales de clases → `cn()`
- Combinar estilos de RN con valores falsy → `mergeStyles()`
- Input con debounce (búsqueda, autocomplete) → `useDebouncedValue()`
- Seguir el scheme del sistema (light/dark) → `useTheme()` (de `@socarrandin/utils`)
- Tipos de imágenes/recursos → `IImage`, `IImageMedia`, `IPhoto`, `IResource`
- Props comunes (`children`, `className`) → `ChildrenProps`, `ClassNameProps`
- Enums de dominio → `IDENTIFY_TYPE_ENUM`, `ORDER_TYPE_ENUM`

## API (packages/utils/src)

| Utilidad | Firma | Notas |
|---|---|---|
| `cn(...inputs)` | `(...inputs: ClassValue[]) => string` | `twMerge(twJoin(...))` — para clases estilo Tailwind/classnames |
| `mergeStyles(...styles)` | `(...styles: StyleProp<ViewStyle\|TextStyle\|ImageStyle>[]) => StyleProp` | aplanado recursivo, descarta falsy, último gana (para StyleSheet de RN) |
| `useTheme()` | `() => "light" \| "dark"` | reacciona a `Appearance.addChangeListener` |
| `useDebouncedValue<T>(value, delayMs)` | `(value: T, delayMs: number) => T` | valor con delay; para búsquedas |

## API (packages/types/src)

| Tipo | Forma |
|---|---|
| `IResource` | `{ _id?, url, size?, mimetype?, isLoading?, isError? }` |
| `IImageMedia` | `IResource` + `{ thumb, width?, height?, sizes? }` |
| `IPhoto` | `{ fileName, fileSize, height, originalPath, type, uri, width }` (archivo local) |
| `IImage` | `IPhoto \| IImageMedia` (unión) |
| `IDocumentMedia` | `{ originalname, size, mimetype, url }` |
| `ChildrenProps` | `{ children?: ReactNode }` |
| `ClassNameProps` | `{ className?: string }` |
| `IDENTIFY_TYPE_ENUM` | PASSPORT, NID, DRIVER_LICENCE |
| `ORDER_TYPE_ENUM` | DELIVERY, COLLECTION |

## Patrón correcto

```tsx
import { cn } from "@socarrandin/utils";
import { mergeStyles } from "@socarrandin/utils";
import { IImageMedia } from "@socarrandin/types";

// condicionales de clase
<View className={cn("base", isActive && "active", !enabled && "disabled")} />

// merge de estilos RN (último gana)
style={mergeStyles(styles.base, isActive && { borderColor: colors.accent })}

// debounce de búsqueda
const [query, setQuery] = useState("");
const debouncedQuery = useDebouncedValue(query, 300);
// queryKey: ["search", debouncedQuery]
```

## Anti-patterns (prohibidos)

| Anti-pattern | Fix |
|---|---|
| Implementar merge de clases a mano (template strings + filter) | `cn()` |
| Arrays de estilos con `.flat().filter(Boolean)` a mano | `mergeStyles()` |
| Debounce con setTimeout/useEffect propio | `useDebouncedValue()` |
| `Appearance.addChangeListener` manual en cada screen | `useTheme()` de `@socarrandin/utils` |
| Definir `type IImageMedia`/`IPhoto` duplicados en la app | `@socarrandin/types` |

## Errores comunes

- `cn()` es para className-style (Tailwind); `mergeStyles()` es para `StyleProp` de RN — no confundir.
- `mergeStyles` con un solo style válido devuelve ese style directo (no array) — compatible con el typing de RN.
- `useTheme` de `@socarrandin/utils` sigue el scheme del SISTEMA; el theme de la app (con ThemeProvider) se lee con `useTheme` de `@socarrandin/ui` — no mezclar ambos en el mismo componente sin intención.
- `IImage` es unión de local (IPhoto) y remoto (IImageMedia): para resolver URI usar `getUri` de `@socarrandin/ui` (ver socarrandin-upload).

## Verificación

- `npm run typecheck` limpio (desde raíz del repo)
- `git grep -n "tailwind-merge\|filter(Boolean).*flat" apps/*/src` sin matches — `cn`/`mergeStyles` importados
- Ningún tipo de imagen redefinido en apps: `IImage`/`IImageMedia`/`IPhoto` importados de `@socarrandin/types`