---
name: ebook-research
description: Investiga nicho en Amazon (mercado del state.json): competencia, demanda, sub-nichos, precio, keywords ganadoras. Usar tras ebook-idea o cuando se pide "investiga el nicho".
---

# ebook-research

## Misión
Saber si el nicho vende y cómo diferenciarse. Como lo haría un editor antes de encargar un libro.

## Pasos
1. Buscar en Amazon (mercado según state: `.com` o `.es`) usando websearch/webfetch: "ebook <nicho>", "libro <nicho>", "kindle <nicho>"
2. Analizar: nº de resultados, best-sellers (título, precio, nº reseñas, ranking), huecos ("qué no cubren")
3. Keywords: 7 términos con volumen/baja competencia (título corto de autocompletado Amazon)
4. Escribir `research.md`:
   - Demanda: alta/media/baja + evidencia
   - Competencia: top 5 títulos + precio medio + nº reseñas
   - Hueco editorial: 2-3 frases (ej: "nadie cubre postres sin azúcar para niños")
   - 7 keywords
5. Recomendación: seguir con tema / pivotar a sub-nicho / cambiar tema. Con opción concreta.
6. Preguntar: "¿Sigo con este tema o pivotamos?"

## Reglas
- Sin acceso web → usar conocimiento del modelo, anotar "estimación sin verificación web", seguir.
- Si hay `research.md` ya → preguntar si re-investigar o saltar a outline.
- Escribir `paso:"research"` en state.json al terminar.