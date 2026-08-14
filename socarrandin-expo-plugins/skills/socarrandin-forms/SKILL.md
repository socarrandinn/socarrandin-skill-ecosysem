---
name: socarrandin-forms
description: Usar al construir pantallas de formulario en apps del monorepo socarrandin-expo-ecosystem. Obliga a react-hook-form + zod (@hookform/resolvers/zod) con los campos Form* de @socarrandin/ui en lugar de inputs crudos o gates manuales de submit. Triggers: escribir un form screen, FormTextField, FormSelectField, FormDateField, FormBirthDayField, FormOtpField, FormRadioGroupField, handleSubmit, validación con zod, `canSubmit`.
---

# socarrandin-forms

## Regla de oro

**Todo formulario en código de app usa react-hook-form (`useForm`) + zod (resolver `@hookform/resolvers/zod`) + los campos `Form*` de `@socarrandin/ui`.** El gate de submit es `handleSubmit(schema-validated-callback)` — NUNCA un boolean `canSubmit` manual.

## Cuándo usar

- Cualquier pantalla/modal con 1+ campos de entrada → este skill
- Cualquier `TextInput` en un form → `FormTextField` (o `FormPasswordField`, `FormTextAreaField`)
- Cualquier selector en un form → `FormSelectField` (options `{value,label,description?,icon?}`)
- Cualquier fecha → `FormDateField` (picker) o `FormBirthDayField` (día/mes/año)
- Cualquier OTP → `FormOtpField`
- Cualquier radio exclusivo → `FormRadioGroupField` (options `{value,label,description?,icon?}`)
- Cualquier switch → `FormSwitchIOSField`; slider → `FormSliderField`; checkbox → `FormCheckboxField`

## Catálogo de campos (packages/ui/src/forms)

| Campo | Props clave | Output |
|---|---|---|
| `FormTextField` | `control`, `name`, `label`, `isRequired`, `helpText`, `startContent`/`endContent` | string |
| `FormPasswordField` | `control`, `name`, `label`, `startContent` | string (con toggle ojo) |
| `FormTextAreaField` | `control`, `name`, `label` | string multiline |
| `FormSelectField` | `control`, `name`, `label`, `placeholder`, `options: FormSelectOption[]` | string (value de option) |
| `FormDateField` | `control`, `name`, `label`, `minimumDate`, `maximumDate` | ISO `YYYY-MM-DD` |
| `FormBirthDayField` | `control`, `name`, `label`, `output: "date"\|"iso"` (default date) | Date o ISO |
| `FormOtpField` | `control`, `name`, `maxLength` (6), `pattern`, `onComplete` | string |
| `FormRadioGroupField` | `control`, `name`, `options: RadioGroupOption[]` | string |
| `FormSwitchIOSField` | `control`, `name`, props Switch | boolean |
| `FormSliderField` | `control`, `name`, props Slider | number |
| `FormCheckboxField` | `control`, `name` | boolean |

`FormSelectField` y `FormRadioGroupField` también aceptan modo no-controlado (omite `control`/`name`, pasa `value` + `onValueChange`).

## Providers

- `Form` (de `@socarrandin/ui`) envuelve el form y provee `useForm()` de contexto (isLoading, disabled, readOnly). Opcional: se puede usar `useForm` de react-hook-form directamente + `FormProvider`.
- `FormBirthDayField`, `FormDateField`, `FormSelectField` usan `useI18n()` → requieren `I18nProvider` arriba (ver socarrandin-i18n).

## Patrón correcto

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button, Form, FormSelectField, FormTextField } from "@socarrandin/ui";

const schema = z.object({
  firstName: z.string().min(2),
  role: z.string().min(1),
});
type FormData = z.infer<typeof schema>;

const { control, handleSubmit, formState } = useForm<FormData>({
  resolver: zodResolver(schema),
  defaultValues: { firstName: "", role: "" },
});

<Form onSubmit={handleSubmit(onSubmit)}>
  <FormTextField control={control} name="firstName" label="Nombre" isRequired />
  <FormSelectField
    control={control}
    name="role"
    label="Rol"
    placeholder="Seleccionar"
    options={[
      { value: "admin", label: "Admin", description: "Acceso total" },
      { value: "user", label: "Usuario" },
    ]}
  />
  <Button onPress={handleSubmit(onSubmit)} isDisabled={formState.isSubmitting}>
    <Button.Label>Guardar</Button.Label>
  </Button>
</Form>
```

```tsx
// Fecha de nacimiento (día/mes/año), salida ISO
<FormBirthDayField control={control} name="birthDate" output="iso" isRequired />
```

```tsx
// OTP con patrón de solo dígitos y callback al completar
<FormOtpField
  control={control}
  name="code"
  maxLength={6}
  pattern="^\d+$"
  onComplete={(code) => verifyCode(code)}
/>
```

## Anti-patterns (prohibidos)

| Anti-pattern | Fix |
|---|---|
| `canSubmit` boolean manual para gatear submit | `handleSubmit(schema-validated-callback)` |
| `TextInput` + `onChangeText` + estado local para campos de form | `FormTextField` con `control` + `name` |
| Inputs crudos con errores manejados a mano | campos `Form*` ya enlazan `fieldState.error` → `FieldError` |
| Sin zod, validación a mano en submit | `zodResolver(schema)` |
| Select con Modal/listado manual | `FormSelectField` con `options` |
| Estado de error gestionado con useState | dejar que RHF + campos `Form*` lo hagan |

## Errores comunes

- `FormTextField.value` puede venir `null`: el campo lo normaliza a string vacío internamente; en `defaultValues` usa `""` no `null`.
- `FormDateField` y `FormBirthDayField` emiten ISO `YYYY-MM-DD`: parsear con `parseIsoDate`/`toIsoDate` de `@socarrandin/ui` (`utils/dates`), no a mano.
- `FormBirthDayField` solo emite valor cuando día+mes+año están completos; los días inválidos (ej. Feb 31) se recortan automáticamente.
- `FormSelectField` en modo controlado: `onValueChange` recibe `string | undefined`; en uncontrolled el valor del form es el `value` de la option.
- `Form` provee `useForm()` de contexto, pero para typing estricto de `handleSubmit` usá `useForm` de react-hook-form directamente.
- Strings vacíos como `defaultValues` evitan warnings de inputs no controlados.

## Verificación

- `npm run typecheck` limpio (desde raíz del repo)
- `git grep -n "canSubmit" apps/*/src` no debe matchear gate de submit manual
- Ningún form con `useState` por campo: cada campo usa `control`/`name` de react-hook-form
- Toda pantalla con inputs usa `handleSubmit` como gate