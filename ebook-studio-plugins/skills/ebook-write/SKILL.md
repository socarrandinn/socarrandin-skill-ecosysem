---
name: ebook-write
description: Escribe el ebook capítulo a capítulo, estilo humano, sin voz robótica. Usar tras outline o "escribe el libro".
---

# ebook-write

## Misión
Escribir como persona, no como AI. Cada capítulo un archivo.

## Reglas de voz (críticas)
- Prohibido: "En el mundo actual", "es importante destacar", "además,", listas genéricas de 3, resumen al final de cada sección, frases plantilla
- Permitido: anécdotas breves, opinión con fundamento, ejemplos concretos, preguntas retóricas puntuales, transiciones naturales
- Variar longitud de frases; mezclar cortas y largas
- Si hay material extraído: reescribir con voz propia, datos/recetas en formato estándar pero texto original

## Pasos
1. Leer outline.md + state
2. Por cada capítulo (orden): escribir `capitulos/capitulo-NN-titulo.md` con el wordcount del outline
3. Tras cada capítulo: anotar avance en `capitulos[].n` del state.json; cada 2-3 capítulos, resumir avance al usuario ("3/10 capítulos, 8k palabras")
4. Al terminar: concatenar en `manuscrito.md` con estructura completa (portada, copyright, intro, capítulos, conclusión, CTA) y ejecutar el verificador desde la carpeta de esta skill (scripts/ está junto a este SKILL.md): `python scripts/check_manuscrito.py "<state.json>"`
   - `WARN_SHORT:` → capítulo muy por debajo del objetivo del outline: expandirlo antes de pasar a edit
   - `WARN:` sin capitulos[] → solo conteo total, seguir igual
5. Preguntar: "Manuscrito completo: N capítulos, N palabras. ¿Reviso estilo y coherencia?"

## Regla
- NO saltarse capítulos del outline. Si un capítulo no funciona, proponer cambio al usuario primero.