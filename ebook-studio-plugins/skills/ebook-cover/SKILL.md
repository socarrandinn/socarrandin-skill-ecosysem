---
name: ebook-cover
description: Genera portada 2560x1600 PNG con Pillow, paleta según nicho. Usar tras format o "haz la portada".
---

# ebook-cover

## Misión
Portada que venda: legible en miniatura, título grande, promesa clara.

## Pasos
1. Ejecutar desde la carpeta de esta skill (scripts/ está junto a este SKILL.md): `python scripts/make_cover.py "<state.json>"`
2. Leer salida:
   - `COVER_OK:` → avisar ruta de la portada
   - `TITLE_TRUNCATED` → título largo: proponer título corto comercial
   - `ERROR:` → reportar y pedir acción
3. Avisar: portada generada. Para portada premium (tipografía decorativa, ilustración) → recomendar Canva con el brief: título, colores, estilo
4. `paso:"cover"`

## Notas
- Fuente: auto-detecta por SO (Windows/macOS/Linux). Override con variable `EBOOK_FONT` apuntando a un .ttf/.otf.
- Portada sale en `<dir>/portada.png` (o ruta pasada como segundo argumento).