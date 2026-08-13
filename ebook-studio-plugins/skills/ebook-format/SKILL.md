---
name: ebook-format
description: Convierte manuscrito.md a EPUB + PDF (pandoc + motor headless disponible). Usar tras edit o "genera el epub".
---

# ebook-format

## Misión
Maquetar el archivo final. Un comando.

## Pasos
1. Verificar existe manuscrito.md; si no → devolver a write
2. Ejecutar desde la carpeta de esta skill (scripts/ está junto a este SKILL.md): `python scripts/build_ebook.py "<state.json>"`
3. Salida:
   - `OK:` → avisar rutas `out/libro.epub` + `out/libro.pdf`
   - `EPUB_WARN:` → EPUB generado pero con problema estructural; avisar y revisar antes de subir a KDP
   - `EPUBCHECK_WARN:` → epubcheck (si está instalado) encontró errores; mostrar el detalle
   - `NO_ENGINE` → entregar EPUB + HTML, explicar PDF manual
   - `PDF_WARN` → PDF falló, EPUB + HTML OK
   - `ERROR:` pandoc → instalar manualmente (winget/brew/apt según SO), reintentar
4. Actualizar `paso:"format"`