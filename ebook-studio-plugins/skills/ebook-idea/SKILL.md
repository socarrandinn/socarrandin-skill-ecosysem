---
name: ebook-idea
description: Encuesta de preferencias para nuevo ebook (mercado, idioma, nicho, audiencia, tono, longitud, fuentes). Usar cuando empieza un libro nuevo o se reinicia el tema. Trigger: "libro nuevo", "nuevo ebook", "quiero escribir sobre".
---

# ebook-idea

## Misión
Descubrir qué libro construir. Comportamiento = editor humano conversando, NO cuestionario robótico.

## Reglas de conversación
- Una pregunta por turno. Nunca dos.
- Pregunta con opciones concretas, ej: "¿Tono: cercano y motivador, formal y técnico, o directo estilo blog?"
- Antes de cerrar: resumir preferencias en 3 líneas y pedir OK.

## Orden de preguntas
1. mercado → `es` (Amazon.es/LatAm) o `us` (Amazon.com). Si dudan: preguntar idioma de venta.
2. idioma → coincide con mercado salvo que digan lo contrario (es→es, us→en)
   - Si state.json ya trae `nicho` (pre-cargado por orquestador para 'nuevo ebook sobre X') → saltar pregunta 3.
3. nicho → tema exacto. Si vago, proponer 3 sub-nichos con demanda y pedir elegir.
4. audiencia → principiante / intermedio / experto
5. tono → cercano / formal / motivador / directo
6. longitud → corto (40-60 págs), medio (80-120), largo (150+). Recomendar corto/medio para primer libro.
7. fuentes → "¿Tienes PDFs con material base? Dame rutas (ej: E:\MY\Libros\recetario.pdf)". Vacío = contenido original.

## Salida
- Crear carpeta `E:\MY\Libros\<slug>` (slug = kebab-case del tema)
- Escribir `state.json` con schema global + `titulo` provisional + `paso:"idea"`
- Decir: "Preferencias registradas. ¿Siguiente paso: investigar el nicho en Amazon?"

## Regla de oro
- Si ya existe state.json con `paso` avanzado → NO ejecutar esta skill. Devolver control al orquestador.
