---
name: ebook-format
description: Convierte manuscrito.md a EPUB + PDF (pandoc + Edge headless). Usar tras edit o "genera el epub".
---

# ebook-format

## Misión
Maquetar el archivo final. Un comando.

## Pasos
1. Verificar existe manuscrito.md; si no → devolver a write
2. Ejecutar: `python "C:\Users\silvio\.config\opencode\skills\ebook-format\scripts\build_ebook.py" "<state.json>"`
3. Salida:
   - `OK:` → avisar rutas `out/libro.epub` + `out/libro.pdf`
   - `NO_ENGINE` → entregar EPUB + HTML, explicar PDF manual
   - Error pandoc → instalar manualmente: `winget install JohnMacFarlane.Pandoc`, reintentar
4. Actualizar `paso:"format"`