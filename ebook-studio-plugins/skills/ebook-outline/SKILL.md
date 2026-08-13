---
name: ebook-outline
description: Construye índice y estructura de capítulos con wordcount por capítulo según longitud del state. Usar tras research o "haz el outline".
---

# ebook-outline

## Misión
Estructura editorial: qué capítulos, en qué orden, cuántas palabras cada uno.

## Pasos
1. Leer state.json (longitud, audiencia, nicho) y research.md
2. Calcular total según mapeo páginas→palabras: ≤60 págs → corta (~12k palabras), 61-120 → media (~25k), >120 → larga (~45k)
3. Diseñar capítulos (8-15): apertura gancho, núcleo, cierre acción. Cada uno: título + propósito + wordcount
4. Incluir siempre: portada, copyright page, introducción, conclusión, llamada a la acción final
5. Guardar `outline.md` + actualizar state.json `capitulos[]` con `n, titulo, palabras`
6. Presentar resumen: "Outline: 10 capítulos, 25k palabras. ¿OK o ajustamos?"

## Reglas
- Distribución realista: capítulos 1-2 cortos (gancho), medios equilibrados, final con resumen
- NO empezar a escribir — solo estructura