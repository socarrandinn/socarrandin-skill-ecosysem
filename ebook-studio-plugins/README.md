# ebook-studio-plugins

Ecosistema de skills para OpenCode que produce ebooks listos para Amazon KDP: un agente orquestador, un comando y 11 skills encadenadas (idea → research → outline → extract → write → edit → format → cover → kdp), más 4 scripts Python.

## Requisitos

| Dependencia | Para qué | Cómo instalarla |
|---|---|---|
| Python 3.9+ | scripts | — |
| Pillow (auto-instala) | portada | `pip install Pillow` |
| pdfplumber (auto-instala) | extracción PDF | `pip install pdfplumber` |
| pandoc | EPUB + HTML | Windows: `winget install JohnMacFarlane.Pandoc` · macOS: `brew install pandoc` · Debian/Ubuntu: `sudo apt-get install -y pandoc` |
| Edge/Chrome (headless) | PDF | opcional; fallback: `wkhtmltopdf` o `weasyprint` en PATH |
| epubcheck | validación EPUB (opcional) | https://github.com/w3c/epubcheck |

Los scripts instalan sus dependencias Python automáticamente desde `requirements.txt` propio de cada skill.

## Instalación

1. Copiar `agent/`, `command/` y `skills/` a tu carpeta de skills de OpenCode (ej. `~/.config/opencode/skills/`).
2. (Opcional) Fijar carpeta base de libros:

   ```sh
   # PowerShell
   $env:EBOOK_ROOT = "D:\MisLibros"
   # bash
   export EBOOK_ROOT=~/Libros
   ```

   Default: `~/Libros`.

3. (Opcional) Fuente de portada custom: `EBOOK_FONT=/ruta/a/fuente.ttf`.

## Uso

```
haz un ebook
/ebook
sigue con mi libro
```

El orquestador (`ebook-studio`) lee `state.json` del libro y decide qué skill ejecutar. Una skill activa por turno.

## Pipeline

```
idea → research → outline → (extract si fuentes) → write → edit → format → cover → kdp → listo
```

| Skill | Salida |
|---|---|
| ebook-idea | `<EBOOK_ROOT>/<slug>/state.json` |
| ebook-research | `research.md` |
| ebook-outline | `outline.md` + `state.capitulos[]` |
| ebook-extract | `extraido/*.md` (PDFs fuente) |
| ebook-write | `capitulos/capitulo-NN-*.md` → `manuscrito.md` |
| ebook-edit | manuscrito pulido |
| ebook-format | `out/libro.epub` + `out/libro.html` + `out/libro.pdf` |
| ebook-cover | `portada.png` (2560×1600) |
| ebook-kdp | checklist de publicación |

## Scripts

| Script | Skill | Función |
|---|---|---|
| `scripts/make_cover.py` | ebook-cover | Portada 2560×1600 con paleta por keywords del nicho, wrap de título por ancho real de píxel |
| `scripts/extract_pdf.py` | ebook-extract | PDF → markdown; detecta PDFs escaneados (`WARN_SCANNED`) |
| `scripts/build_ebook.py` | ebook-format | pandoc → EPUB/HTML + motor headless → PDF; validación estructural del EPUB |
| `scripts/check_manuscrito.py` | ebook-write | wordcount por capítulo vs objetivos del outline (`WARN_SHORT`) |

Todas aceptan `<state.json>` como argumento y emiten líneas prefijadas (`OK:`, `ERROR:`, `WARN_*:`) en stderr cuando es un aviso; exit code ≠ 0 en error.

## Multiplataforma

- Fuentes: auto-detecta Windows/macOS/Linux, fallback a `fc-match` y fuente default.
- Pandoc: auto-instala por SO (winget/brew/apt), con instrucción manual si falla.
- Motor PDF: Edge/Chrome (rutas por SO) → wkhtmltopdf → weasyprint.
- Rutas: los SKILL.md referencian `scripts/` relativo a la carpeta de la skill, sin paths absolutos.

## Schema de estado

`state.schema.json` documenta `state.json` (claves, enums, `capitulos[]`). Las skills escriben con ese contrato.

## Limitaciones conocidas

- Los mensajes conversacionales de las skills están en español; solo los scripts se localizan según `state.idioma`.
- La validación del EPUB es estructural (stdlib); `epubcheck` solo corre si está en PATH.
- `state.schema.json` es informativo: no hay validación en runtime.

## Licencia

MIT.