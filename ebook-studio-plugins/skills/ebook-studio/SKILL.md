---
name: ebook-studio
description: Orquestador maestro del pipeline de ebooks para Amazon KDP. Decide qué skill ejecutar según state.json. Usar SIEMPRE al inicio: "haz un ebook", "/ebook", "sigue con mi libro". Cargar esta skill primero, después delegar a las steps.
---

# ebook-studio

## Misión
Ser el productor editorial: sabe dónde está cada libro y qué toca hacer ahora. NO escribe ni maqueta — delega.

## Pipeline (orden fijo)
idea → research → outline → (extract si fuentes) → write → edit → format → cover → kdp → listo

## Decisión (leer primero)
1. Buscar `E:\MY\Libros\*\state.json`. Si existe alguno (si varios → preguntar cuál, o usar el de modificación más reciente):
   - `paso` = fase en curso → cargar skill de ese paso y ejecutarla
   - pedido "nuevo tema" → ignorar estados, arrancar ebook-idea
   - `paso:"listo"` → preguntar: re-generar (format), nuevo libro, o editar metadata
2. Si NO existe: arrancar ebook-idea

## Reglas de orquestación
- Una sola skill activa por turno. Cargar la skill del paso actual, ejecutar, esperar confirmación del usuario, pasar al siguiente paso (actualizando state.paso)
- Dueño único de state.paso: el orquestador. Las skills NO escriben paso; solo el orquestador lo actualiza tras confirmación del usuario (excepción: ebook-idea al crear el state)
- El usuario puede pedir saltar pasos (ej: "sin investigación") → marcar paso completado sin ejecutar, anotar en state
- Antes de cada salto: confirmar con usuario
- Frases típicas y su mapeo:
  - "sigue con mi libro" → leer state, continuar en paso actual
  - "nuevo ebook sobre X" → idea con nicho pre-cargado
  - "usa estos PDFs" → añadir fuentes a state → extract
- Al terminar todo (paso:"listo"): resumen final 5 líneas + checklist publicación (subir epub+pdf, portada, metadata, fijar precio)