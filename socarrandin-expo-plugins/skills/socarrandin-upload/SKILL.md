---
name: socarrandin-upload
description: Usar al implementar subida de imágenes o documentos en apps del monorepo socarrandin-expo-ecosystem. Obliga a los componentes de upload de @socarrandin/ui (ImageGridUploader, AvatarUploader, CropModal, PickSourceSheet) y hooks (useImageGridUpload, useUploadImages, useImageUri) en lugar de expo-image-picker/document-picker crudos. Triggers: subir imágenes, galería, grid de fotos, crop, avatar, documentos, picker de cámara, UploadProgress.
---

# socarrandin-upload

## Regla de oro

**Toda subida de imágenes/documentos en código de app usa los componentes y hooks de upload de `@socarrandin/ui`** — nunca `expo-image-picker`/`expo-document-picker`/`fetch` directo al storage. El flujo completo (permisos, picker, crop, upload, progreso, errores) ya está resuelto.

## Cuándo usar

- Grid de fotos con límite + tips + format hint → `ImageGridUploader`
- Avatar circular único → `AvatarUploader`
- Subida sin UI, desde código → `useUploadImages` (mutation react-query)
- Necesitar el flujo completo pero con UI propia → `useImageGridUpload`
- Mostrar imagen remota del CDN → `useImageUri`
- Solo recortar una imagen local → `CropModal` (shape circle/square)
- Solo elegir fuente (cámara/galería) → `PickSourceSheet`

## Catálogo (packages/ui/src/components/upload)

| Componente | Props clave | Notas |
|---|---|---|
| `ImageGridUploader` | `images: IImageMedia[]`, `onChange: (images: IImage[]) => void`, `maxImages` (6), `columns` (3), `kind: "image"\|"document"`, `uploadMode: "batch"\|"sequential"`, `documentTypes`, `rawFile`, `allowRemove`, `showTips`, `showProgress`, `showFormatHint`, `rules: {tips, allowedFormats, maxSizeMB}`, `onUploadingChange`, `onError`, `onInfo` | Todo-in-uno: header, tiles, add tile, tips, progreso, format hint, crop + picker sheet |
| `AvatarUploader` | `image: AvatarItem \| null`, `onChange: (image: AvatarItem \| null) => void`, `size` (140), `kind`, `rawFile`, `showTips`, `rules`, `error: boolean`, `onUploadingChange`, `onError` | crop circular (shape="circle") |
| `CropModal` | `uri`, `onCancel`, `onConfirm({uri,width,height})`, `shape: "circle"\|"square"` | full-screen editor pan/pinch/rotate, salida JPEG square 512px |
| `PickSourceSheet` | `isPresented`, `onPickCamera`, `onPickLibrary`, `onDismiss` | bottom sheet nativo @expo/ui |
| `UploadProgress` | `current`, `max` | |
| `AddTile` / `ImageGridTile` / `TipsTile` / `GridHeader` / `FormatHint` | piezas sueltas del grid | |

| Hook | Firma | Notas |
|---|---|---|
| `useUploadImages` | `(kind: "image"\|"document" = "image", opts?: { single?: boolean }) => useMutation<IImageMedia[], BackendErrorPayload, IPhoto[]>` | `single: true` → endpoint single (`resourcesApi.upload`), batch → `uploadMany`/`uploadDocument` |
| `useImageGridUpload` | `({images, onChange, maxImages, kind, uploadMode, documentTypes, rawFile, onRawPick, onUploadingChange, onError, onInfo})` | devuelve `requestPick`, `handlePickCamera`, `handlePickLibrary`, `handleCropConfirm/Cancel`, `removeAt`, `remaining`, `isUploading`, `progress`, `isPickerOpen`, `cropOpen`, `pendingPhoto` |
| `useImageUri` | `(image?: IImageMedia \| null, size?: number) => string` | `size` → `${CDN_PREFIX}/url-w${size}`; sin size → thumb o url |

Helpers: `getUri(item)` (resuelve IPhoto local vs IImageMedia CDN), `toGridPhoto(uri,width,height)`, `DEFAULT_RULES` (JPG/PNG, 2MB).

## Providers y dependencias

- `useUploadImages` usa react-query → requiere `QueryClientProvider` (ver socarrandin-api)
- Todos usan `useI18n()` → requieren `I18nProvider` (ver socarrandin-i18n)
- `CropModal` usa gesture-handler/reanimated → require `GestureHandlerRootView` en la raíz de la app

## Patrón correcto

```tsx
// Grid de fotos, batch, máx 6
<ImageGridUploader
  images={images}
  onChange={setImages}
  maxImages={6}
  kind="image"
  uploadMode="batch"
  rules={{ tips: ["Buena iluminación", "Fondo neutro"], allowedFormats: ["JPG", "PNG"], maxSizeMB: 2 }}
  onError={(title, description) => alert(title, description)}
/>

// Avatar único (rawFile para interceptar el archivo local)
<AvatarUploader
  image={avatar}
  onChange={setAvatar}
  size={140}
  error={!!errors.avatar}
  onUploadingChange={setUploading}
/>
```

```tsx
// Uso desde código: subir sin UI propia
const upload = useUploadImages("image");
const handlePick = async () => {
  const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ["images"] }); // solo picker nativo
  if (!result.canceled) {
    const uploaded = await upload.mutateAsync([result.assets[0] as IPhoto]);
    setImages(uploaded);
  }
};
```

```tsx
// Render de imagen remota
const uri = useImageUri(profileImage, 200);
<Image source={{ uri }} />
```

## Anti-patterns (prohibidos)

| Anti-pattern | Fix |
|---|---|
| `expo-image-picker` + `fetch` FormData a mano | `ImageGridUploader` / `useUploadImages` |
| Modal de elegir origen (cámara/galería) hecho a mano | `PickSourceSheet` |
| Recorte con `expo-image-manipulator` manual | `CropModal` |
| Grid de fotos + spinner de progreso manual | `ImageGridUploader` (trae `UploadProgress`) |
| URLs de CDN concatenadas a mano | `useImageUri` / `getUri` |
| Manejo de permisos con Alert a mano | `onError` callback del uploader |

## Errores comunes

- `ImageGridUploader.onChange` recibe la lista NUEVA completa (add o remove): usar `setState` directo, no append manual.
- `maxImages === 1` cambia el comportamiento interno a single-upload (`single: true`).
- `rawFile: true` NO sube a red: devuelve los archivos locales vía `onRawPick` o los appende — útil para forms donde el upload se dispara al submit.
- `uploadMode="sequential"` sube de a uno y actualiza `images` después de cada archivo; `batch` hace una sola request.
- `AvatarUploader.error` es controlado por el padre: wirear a `formState.errors` del form.
- `useImageUri` devuelve `""` (no `undefined`) cuando no hay imagen.
- Para documentos, `kind="document"` + `documentTypes` (mime types) — el picker document usa `multiple` según `remaining > 1 && uploadMode === "batch"`.
- Errores de upload llegan como `BackendErrorPayload` en `mutation.error` — presentar con `onError` del componente, no con console.

## Verificación

- `npm run typecheck` limpio (desde raíz del repo)
- `git grep -n "expo-image-picker\|expo-document-picker" apps/*/src` solo debe matchear re-exports o nada — el picker lo gestionan los componentes del ui
- Ningún `fetch`/`FormData` a endpoints de storage en código de app