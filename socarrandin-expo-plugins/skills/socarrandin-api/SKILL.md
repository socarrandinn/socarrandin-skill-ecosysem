---
name: socarrandin-api
description: Usar al hacer peticiones HTTP, autenticación, sesión, cache de datos o subida a storage en apps del monorepo socarrandin-expo-ecosystem. Obliga a los clients de @socarrandin/api (authApi, driverApi, resourcesApi, apiFetch/getJson/sendJson) + react-query con createQueryClient en lugar de fetch crudo. Triggers: login, register, OTP, forgot password, getMe, queries de datos, mutaciones, subir archivos, tokens, refresh, BackendErrorPayload.
---

# socarrandin-api

## Regla de oro

**Toda petición HTTP en código de app pasa por `@socarrandin/api`** — nunca `fetch` directo a `API_BASE_URL`. El client ya maneja: base URL, headers (`x-workspace`, `Authorization`, `Accept-Language`), timeout (30s), refresh automático en 401 y errors tipados (`BackendErrorPayload`).

## Cuándo usar

- Cualquier GET/POST/PATCH/DELETE → `getJson` / `sendJson` (o los wrappers `authApi`/`driverApi`/`resourcesApi`)
- Cualquier consulta con cache → react-query (`useQuery`/`useMutation`) sobre los clients
- Login/register/OTP/forgot password → `authApi`
- Perfil/vehículos/contactos/licencia de driver → `driverApi`
- Subir imágenes/documentos → `resourcesApi` (o mejor: hooks de upload, ver socarrandin-upload)
- Persistir/limpiar sesión → `persistAuth` / `clearAuth` / `readAccessToken`

## Clientes (packages/api/src)

| Client | Métodos | Notas |
|---|---|---|
| `authApi` | `register(data)`, `login(identifier, password)`, `getMe()`, `resendOtp(identifier)`, `verifyOtp(identifier, code)`, `forgotPasswordInit(email)`, `forgotPasswordCheck(email, code)`, `forgotPasswordFinish(resetToken, password)` | retorna `AuthResult` ({access_token, refresh_token, space?}) en login/verify/finish; `getMe` → `AuthUser` |
| `driverApi` | `updateProfile(data)`, `getLicense()`, `updateLicense(data)`, `createContact(data)`, `createVehicle(data)` | tipos `DriverProfilePatchInput`, `DriverLicensePatchInput`, `DriverContactInput`, `DriverVehicleInput` |
| `resourcesApi` | `upload(file)`, `uploadMany(files)`, `uploadDocument(files)` | FormData; `upload` single → `/storage`, `uploadMany` → `/storage/multiple`, document → `/storage/document`; retornan `IImageMedia`/`IImageMedia[]` |
| `getJson<T>(path)` | GET unwrapped | |
| `sendJson<T>(path, method, payload?)` | POST/PATCH/PUT/DELETE con body JSON | |
| `apiFetch<T>(path, init)` | crudo; `{auth?, locale?, timeoutMs?}` | retorna `ApiResult<T>` (`{ok,status,data,body}`) |

## Config y entorno (packages/api/src/config.ts)

| Constante | Fuente | Default |
|---|---|---|
| `API_BASE_URL` | `EXPO_PUBLIC_API_URL` | `http://192.168.0.100:8080` |
| `PUBLIC_SPACE_ID` | `EXPO_PUBLIC_FORCE_SPACE` | `DRIVER_SPACE` |
| `CDN_PREFIX` | `EXPO_PUBLIC_APP_CDN_PREFIX` | URL supabase del proyecto |

`env()` de `@socarrandin/api` lee `process.env` (usar `EXPO_PUBLIC_*` para exponer a la app).

## Auth flow

- `persistAuth(result)` guarda access/refresh (SecureStore en native, localStorage en web) y el space
- `clearAuth()` borra todo
- `apiFetch` con `auth: true` (default) inyecta `Authorization: Bearer <access_token>` y, en 401, intenta refresh automático (`refreshTokens` → `persistAuth` → reintento)
- Requiere `expo-secure-store` instalado en la app (peer dependency)

## Error contract

Toda llamada unwrapped (`getJson`/`sendJson`/wrappers) **lanza** `BackendErrorPayload` en fallo:

```ts
interface BackendErrorPayload {
  message: string;
  statusCode: number;
  reference?: string;
  key?: string;
  metadata?: unknown;
}
```

Network failures: `{ statusCode: 0, message }`. Errores de auth 401 con refresh fallido: `HTTP 401` (`reference: HTTP_401`).

## Patrón correcto

```tsx
// Provider de react-query en la raíz de la app
import { createQueryClient } from "@socarrandin/api";

const queryClient = createQueryClient({
  onError: (error, meta) => {
    // wirear a toast/alert a nivel app; meta?.suppressGlobalError para silenciar
  },
});

// Root: <QueryClientProvider client={queryClient}> ...
```

```tsx
// Query de datos
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { driverApi, type BackendErrorPayload } from "@socarrandin/api";

const { data: license, isLoading } = useQuery({
  queryKey: ["driver", "license"],
  queryFn: () => driverApi.getLicense(),
  meta: { suppressGlobalError: true }, // manejar error localmente
});

const mutation = useMutation({
  mutationFn: driverApi.updateProfile,
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ["driver", "me"] }),
  meta: { errorMap: { VALIDATION: t("errors.validation") } },
});
```

```tsx
// Login con persistencia de sesión
const { mutateAsync, isPending } = useMutation({
  mutationFn: ({ email, password }: { email: string; password: string }) =>
    authApi.login(email, password),
  onSuccess: async (result) => {
    await persistAuth(result);
    await queryClient.invalidateQueries();
  },
});
```

```tsx
// Error tipado
try {
  await mutateAsync(data);
} catch (error) {
  const err = error as BackendErrorPayload;
  showError(err.message);
}
```

## Anti-patterns (prohibidos)

| Anti-pattern | Fix |
|---|---|
| `fetch(API_BASE_URL + ...)` directo | `getJson`/`sendJson` o wrappers |
| URL hardcodeada del backend en app | `API_BASE_URL`/`MS_AUTH` de `@socarrandin/api` |
| Manejo de 401/refresh a mano | `apiFetch` ya lo hace (`auth: true`) |
| Tokens guardados con AsyncStorage/plain | `persistAuth`/`clearAuth` (SecureStore) |
| Validar `res.ok` + parsear body a mano | `getJson`/`sendJson` (unwrap tipado, lanza error) |
| FormData/fetch manual para subir archivos | `resourcesApi.upload*` o hooks de upload |
| QueryClient nuevo por render | `createQueryClient` una vez (módulo o root) |

## Errores comunes

- `apiFetch` NO stringifica el body JSON: usar `sendJson` para POST/PATCH (o `JSON.stringify` a mano).
- `retry: false` y `staleTime: 5min` son defaults del client creado con `createQueryClient` — no re-configurar por query salvo necesidad.
- `meta.suppressGlobalError: true` silencia el notifier global por query/mutation puntual.
- En 401 con refresh fallido el error es `HTTP 401` — distinguir de `API_AUTH_ERRORS.UNAUTHORIZED` (constante `API_AUTH_ERRORS` de `@socarrandin/api`) para forzar logout.
- `driverApi.getLicense` retorna el shape de input (`DriverLicensePatchInput`), útil para prellenar el form de edición.
- El header `Accept-Language` se setea vía `locale` en `apiFetch` — el i18n del app debe pasar el locale actual si el backend traduce (ver socarrandin-i18n).

## Verificación

- `npm run typecheck` limpio (desde raíz del repo)
- `git grep -n "fetch(" apps/*/src` solo debe matchear `apiFetch` importado o re-exports
- Ningún `SecureStore`/`AsyncStorage` para tokens fuera de `@socarrandin/api`
- Toda query usa react-query con `queryKey` estable; invalidar en mutations con `invalidateQueries`