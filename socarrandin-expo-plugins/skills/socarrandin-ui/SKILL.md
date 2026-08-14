---
name: socarrandin-ui
description: Usar al agregar o editar pantallas, botones, inputs, selects, grids, search fields, textos o cualquier elemento UI en apps del monorepo socarrandin-expo-ecosystem (apps/percentil, apps/trici-go-driver, apps/ipv-app o cualquier app que dependa de @socarrandin/ui). Obliga a importar la UI desde @socarrandin/ui en lugar de reimplementar controles con Pressable/TextInput/Text crudos o colores hardcodeados. Triggers: escribir Button, Input, Select, RadioGroup, SearchField, Grid, Switch, Text, InputOTP, o cualquier Pressable estilado.
---

# socarrandin-ui

## Regla de oro

**Todo control, input, botón, form field y superficie temada en código de app DEBE venir de `@socarrandin/ui`.** Nunca reimplementar lo que el package provee. Componentes locales propios (ej. `Card`, `Section`, `Segmented`, `StatusBadge`) deben componerse DESDE primitivas del ui (`Grid`, `RadioGroup`, `Text`, `useAppColors`), no desde `StyleSheet` + hex a mano.

Violar la letra de esta regla es violar su espíritu.

## Cuándo usar

- Cualquier `Pressable` en código de app → casi siempre un `Button` (o `RadioGroup.Item`)
- Cualquier `TextInput` → un `Input` (o `FormTextField` dentro de forms RHF)
- Cualquier texto con color hex → tokens de `useAppColors()` (o `brand.*` en paleta de percentil para colores de marca)
- Cualquier buscador → `SearchField` (compound: `.Group`, `.SearchIcon`, `.Input`, `.ClearButton`)
- Cualquier layout de grilla → `Grid` + `Grid.Item` (los hijos DEBEN ser `Grid.Item`, no views crudas)
- Cualquier selector exclusivo → `RadioGroup` + `RadioGroup.Item` + `Radio` (o `FormRadioGroupField` en forms RHF)
- Cualquier selector modal → `Select` (compound: `.Trigger`, `.Value`, `.Portal`, `.Overlay`, `.Content`, `.Item`)
- Cualquier botón icono+label → `Button` con hijo `<Button.Label>`
- Cualquier entrada de código OTP → `InputOTP` (compound: `.Group`, `.Slot`, `.Separator`)
- Cualquier texto → `Text` con `type` tipográfico (o `Text.Heading`, `Text.Paragraph`)
- Cualquier form screen → react-hook-form + zod + campos `Form*` (ver socarrandin-forms)

## Catálogo (qué existe en packages/ui)

| Necesidad | Usar | Notas |
|---|---|---|
| Botón | `Button` (compound `Button.Label`) | variants: primary, secondary, tertiary, outline, ghost, danger, danger-soft; sizes sm/md/lg; `isIconOnly` |
| Text input (no controlado) | `Input` | `variant` "primary" (field) / "secondary" (default); hereda estado del contexto FormField |
| Input con prefijo/sufijo | `InputGroup` (compound `.Prefix`, `.Suffix`, `.Input`) | afijos decorativos con `isDecorative` |
| Área de texto | `TextArea` | multiline, height 128 |
| Select modal | `Select` (compound) | `value: {value,label}`, `onValueChange`; `.Trigger`, `.Value` (placeholder), `.TriggerIndicator`, `.Portal`, `.Overlay`, `.Content`, `.Item` (`value`,`label`), `.ItemLabel`, `.ItemDescription`, `.ItemIndicator` |
| OTP | `InputOTP` (compound) | `maxLength`, `onComplete`, `pattern`, `pasteTransformer`; `.Group`, `.Slot` (index), `.Separator` |
| Radio group (controlado) | `RadioGroup` + `RadioGroup.Item` + `Radio` | compound: `<RadioGroup value onValueChange>...` |
| Radio cards | `RadioButtonGroup` | compound `.Item`, `.ItemContent`, `.ItemBackground` |
| Buscador | `SearchField` (compound) | `.Group`, `.SearchIcon`, `.Input`, `.ClearButton`; controlado: `value` + `onChange` |
| Switch | `Switch` | `isSelected` + `onSelectedChange` |
| Grid | `Grid` + `Grid.Item` | `columns`, `gap`; hijos deben ser `Grid.Item` |
| Texto | `Text` (compound `.Heading`, `.Paragraph`, `.Code`) | `type`: h1-h6, body, body-sm, body-xs, code; `color` "default"/"muted"; `weight`; `truncate` |
| Colores | `useAppColors()` | token object (accent, danger, muted, surface, border, ...); brand colors de percentil vía `@/theme/palette` `brand` |
| Toast | `useToast()` | `toast.show(msg)` |

## Patrones correctos

```tsx
// Botón con icono + label
<Button size="lg" onPress={submit} isDisabled={busy}>
  <Calculator size={22} color="#FFFFFF" />
  <Button.Label>{t("home:newMeasurement")}</Button.Label>
</Button>

// Radio cards controladas (grilla de 2)
<RadioGroup value={value ?? undefined} onValueChange={(v) => onChange(v as T)}>
  <Grid columns={2} gap={4}>
    {options.map((opt) => (
      <Grid.Item key={opt.value}>
        <RadioGroup.Item value={opt.value} style={styles.option}>
          <View style={styles.content}>{opt.icon}<Text>{opt.label}</Text></View>
          <Radio />
        </RadioGroup.Item>
      </Grid.Item>
    ))}
  </Grid>
</RadioGroup>

// Buscador
<SearchField value={query} onChange={setQuery}>
  <SearchField.Group>
    <SearchField.SearchIcon />
    <SearchField.Input placeholder={t("patients:search")} />
    <SearchField.ClearButton />
  </SearchField.Group>
</SearchField>

// Select modal
<Select value={selected} onValueChange={setSelected}>
  <Select.Trigger>
    <Select.Value placeholder={t("ui:select.placeholder")} />
    <Select.TriggerIndicator />
  </Select.Trigger>
  <Select.Portal>
    <Select.Overlay />
    <Select.Content>
      {options.map((o) => (
        <Select.Item key={o.value} value={o.value} label={o.label}>
          <Select.ItemLabel />
          <Select.ItemDescription>{o.description}</Select.ItemDescription>
          <Select.ItemIndicator />
        </Select.Item>
      ))}
    </Select.Content>
  </Select.Portal>
</Select>
```

## Anti-patterns (encontrados en el wild — prohibidos)

| Anti-pattern | Fix |
|---|---|
| `Pressable` + estilos propios como botón | `Button` (elegir variant) |
| `TextInput` + wrapper de icono de búsqueda manual | `SearchField` |
| Hijos de `Grid` que no son `Grid.Item` | envolver cada celda en `Grid.Item` |
| Radio cards con Pressable propio + `accessibilityRole="radio"` | `RadioGroup` + `RadioGroup.Item` + `Radio` |
| Selector modal hecho con Modal + lista manual | `Select` compound |
| OTP hecho con N TextInputs | `InputOTP` |
| Colores hex hardcodeados tipo `#5B6478` | tokens de `useAppColors()` (`colors.muted`) |
| Submit gate manual (`canSubmit` boolean) | `handleSubmit(schema-validated-callback)` vía RHF |
| Duplicar controles del ui en `src/components/` local | borrar archivo local; importar de `@socarrandin/ui` |

## Errores comunes

- Olvidar `Grid.Item`: las celdas colapsan a full width. Todo hijo directo de `Grid` debe ser `Grid.Item`.
- Hijos de `RadioGroup.Item`: poner contenido + `<Radio />` trailing adentro; nunca estilar la raíz `RadioGroup` con column layout esperando sobreescribir los items — usar `Grid` para grids de cards.
- `SearchField.Input` placeholder: pasar `placeholder` explícito (el default del package es su propio resource key `ui:forms.searchPlaceholder`, ausente en percentil).
- Estilos en `StyleSheet.create` a nivel módulo no pueden llamar `useAppColors()` — construir arrays de estilos dentro del componente (patrón: `[styles.base, { color: colors.muted }]`).
- `Button` con `variant="outline"` + height custom alto: mantener `height` en style prop, no en lógica de border del `StyleSheet` (la variant setea el border).
- `Select` usa `value: { value, label }` (objeto), no string plano.
- `Text` default es `body`: títulos con `type="h2"` etc. o `Text.Heading`.

## Verificación

- `npm run typecheck` y `npm run lint` limpios (desde raíz del repo)
- `git grep -l "Pressable" apps/*/src` solo debe matchear internals de packages/ui o list-row pressables que envuelven cards no-botón — uso botón-like debe ser `Button`
- No debe haber imports de `TextInput` fuera de packages/ui en código de app