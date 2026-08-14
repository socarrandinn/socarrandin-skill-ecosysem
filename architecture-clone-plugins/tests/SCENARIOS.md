# Escenarios architecture-validate (T1-T10)

Fixture: `tests/fixture/proyecto-prueba/`. Para cada escenario: escribir el state.json indicado, cargar architecture-validate, correr checks, comparar reporte.
Antes de cada escenario: reemplazar las rutas absolutas de `state.json` (proyecto, resumen) por las locales del repo.

- [x] T1 state.json no existe → V1 ✗, DETENER, no crea archivo
- [x] T2 estado sano → V1-V7 ✓, CONTINUAR, sin cambios
- [x] T3 resumen ruta muerta + 1 summary en disco → V4 sana ruta
- [x] T4 resumen muerto + 0 summaries → V4 ✗, DETENER
- [x] T5 paso:"listo" + falta espejo existente en disco → V6 sana skillEspejo
- [x] T6 paso:"listo" + skills borradas + summary válido → V5 recalcula, orquestador ofrece regenerar
- [x] T7 fecha no ISO → V7 sana
- [x] T8 paso inválido → V3 ✗, DETENER, state intacto
- [x] T9 analyze interrumpido con progreso:"estructura" → retoma desde stack (F5)
- [x] T10 re-analiza con paso:"listo" → confirmar y forzar analyze (F4)
