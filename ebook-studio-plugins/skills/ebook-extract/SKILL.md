---
name: ebook-extract
description: Extrae texto de PDFs fuente a markdown (pdfplumber) para reescribir contenido. Usar cuando state.fuentes tiene PDFs o se pide "usa este PDF".
---

# ebook-extract

## Misión
Convertir material base a markdown limpio. Un solo comando, sin prometer más.

## Pasos
1. Verificar state.fuentes no vacío; si vacío → decir que no aplica, saltar a write
2. Ejecutar: `python "C:\Users\silvio\.config\opencode\skills\ebook-extract\scripts\extract_pdf.py" "<state.json>"`
3. Revisar salida: FALTA = avisar archivo inexistente; archivos ilegibles (poco texto) → avisar
4. Actualizar `paso:"extract"` en state
5. Resumir: "Extraje 3 recetarios → extraido/. Reescritura usará este material, sin copiar textualmente."

## Regla anti-plagio
- El material extraído es MATERIA PRIMA. El libro final se reescribe con voz propia, nunca copia verbatim de secciones enteras. Recetas = formato estándar, texto original.
