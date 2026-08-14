# Escenarios socarrandin-expo-plugins (T1-Tn)

Blanco de verificación: apps reales del monorepo `E:\MY\_TOOLS\socarrandin-expo-ecosystem\apps\` (percentil, trici-go-driver). Cada escenario valida que los skills del plugin producen y describen código consistente con apps que ya usan los packages.

Antes de cada escenario: asegurarse de que las rutas de apps y packages existan. Reemplazar rutas si el workspace cambió de ubicación.

## Escenarios

- [ ] T1 **UI primitives**: `socarrandin-ui` documenta `Button` (variants, sizes, `Button.Label`, `isIconOnly`), `SearchField` compound, `Grid`+`Grid.Item`, `RadioGroup`, `Select`, `Text`. Verificar contra `packages/ui/src/components/controls/button.tsx`, `.../inputs/search-field.tsx`, `.../layout/grid.tsx`, `.../typography/text.tsx`. Comando: `rg -l "Pressable" apps/percentil/src apps/trici-go-driver/src` solo debe matchear list-rows o internals de packages/ui.
- [ ] T2 **Forms**: `socarrandin-forms` documenta `FormTextField`, `FormBirthDayField`, `FormSelectField`, `FormOtpField`, `FormDateField`, `FormRadioGroupField`, gate `handleSubmit`. Verificar contra `packages/ui/src/forms/*.tsx`. Referencia real: `apps/trici-go-driver/src/modules/auth/screens/SignInScreen.tsx`, `apps/percentil/src/app/patient/new.tsx`. Comando: `rg -n "canSubmit" apps/*/src` sin matches.
- [ ] T3 **Upload**: `socarrandin-upload` documenta `ImageGridUploader`, `AvatarUploader`, `CropModal`, `PickSourceSheet`, `useImageGridUpload`, `useUploadImages`, `useImageUri`. Verificar contra `packages/ui/src/components/upload/**`. Referencia real: `apps/trici-go-driver/src/modules/onboarding/screens/AvatarStepScreen.tsx` (AvatarUploader). Comando: `rg -n "expo-image-picker|expo-document-picker" apps/*/src` sin matches fuera de re-exports.
- [ ] T4 **API/auth**: `socarrandin-api` documenta `authApi`, `driverApi`, `resourcesApi`, `getJson`/`sendJson`, `createQueryClient`, `persistAuth`/`clearAuth`, `BackendErrorPayload`. Verificar contra `packages/api/src/*.ts`. Referencia real: `apps/trici-go-driver/src/shared/hooks/useAuth.tsx`, `apps/trici-go-driver/src/modules/auth/api/auth.api.ts`. Comando: `rg -n "fetch\(" apps/*/src` sin matches de fetch crudo fuera de `apiFetch`.
- [ ] T5 **Theme + errors**: `socarrandin-theme` documenta `useAppColors`, `ThemeProvider`, `useTheme`, `ErrorAlert`, `useErrorResolver`, `ErrorMap`. Verificar contra `packages/ui/src/theme/*.ts(x)` y `packages/ui/src/errors/*`. Referencia real: `apps/percentil/src/app/(tabs)/patients.tsx` (useAppColors), `apps/trici-go-driver/src/modules/auth/constants/errors.ts` (ErrorMap), `apps/trici-go-driver/src/modules/onboarding/screens/SubmittedScreen.tsx` (ErrorAlert). Comando: `rg -n "#[0-9A-Fa-f]{6}" apps/percentil/src apps/trici-go-driver/src` sin matches fuera de paleta.
- [ ] T6 **i18n**: `socarrandin-i18n` documenta `I18nProvider`, `useI18n`, `defineResources`. Verificar contra `packages/i18n/src/*.ts(x)`. Referencia real: `apps/trici-go-driver/src/locales/resources.ts`, `apps/percentil/src/app/result.tsx` (useI18n). Comando: `rg -n "AsyncStorage" apps/*/src` sin matches para locale.
- [ ] T7 **Utils + types**: `socarrandin-utils` documenta `cn`, `mergeStyles`, `useDebouncedValue`, `useTheme`; `socarrandin-types` documenta `IImage`, `IImageMedia`, `IPhoto`, `IResource`. Verificar contra `packages/utils/src/*.ts` y `packages/types/src/*.ts`. Referencia real: `apps/trici-go-driver/src/shared/components/buttons/loading-button.tsx` (mergeStyles). Comando: `rg -n "tailwind-merge" apps/*/src` sin matches.
- [ ] T8 **Providers correctos**: la raíz de cada app monta `ThemeProvider` + `QueryClientProvider(createQueryClient)` + `I18nProvider` + `ToastProvider`. Verificar `apps/percentil/src/app/_layout.tsx` y `apps/trici-go-driver/app/_layout.tsx`.
- [ ] T9 **Sync deploy**: `socarrandin-sync` copia los 7 skills a `.agents/skills` y `.claude/skills`. Comando: `rg -l "name: socarrandin-" E:\MY\_TOOLS\socarrandin-expo-ecosystem\.agents\skills\*.SKILL.md` = 7 files.
- [ ] T10 **Evidencia viva**: cada skill de área cita imports existentes en los barrels. Verificar que todo `export` citado existe en `packages/*/src/index.ts`. Comando: para cada skill, `rg -n "<Exportado>" packages/*/src/index.ts`.

## Comandos de verificación global

```bash
cd E:\MY\_TOOLS\socarrandin-expo-ecosystem
pnpm -r typecheck      # typecheck de packages + apps
```

## Notas

- Las apps `percentil` y `trici-go-driver` son la referencia viva: si un patrón del skill no se encuentra en ninguna app ni en los packages, el skill está desactualizado → correr `socarrandin-sync`.
- Los escenarios T1-T7 validan contenido; T8-T10 validan integración y despliegue.