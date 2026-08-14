---
name: socarrandin-sync
description: Usar para mantener actualizados y desplegar los skills de uso de los packages @socarrandin del monorepo socarrandin-expo-ecosystem. Re-lee packages/*/src, verifica que los patrones y rutas citadas en los skills sigan vigentes, re-curza el contenido si cambió, y copia a .agents/skills y .claude/skills. Triggers: "re-curza", "actualiza los skills", "sync de skills", "desplega los skills", "los packages cambiaron".
---

# socarrandin-sync

## Misión

Mantener los skills de área del plugin `socarrandin-expo-plugins` alineados con el código real de `socarrandin-expo-ecosystem/packages/*`, y desplegar las copias a los directorios de skills del harness.

## Rutas

- **Fuente de verdad**: `E:\MY\_TOOLS\socarrandin-skills-ecosysem\socarrandin-expo-plugins\skills\`
- **Código a verificar**: `E:\MY\_TOOLS\socarrandin-expo-ecosystem\packages\*\src\`
- **Destinos de despliegue**: `E:\MY\_TOOLS\socarrandin-expo-ecosystem\.agents\skills\` y `E:\MY\_TOOLS\socarrandin-expo-ecosystem\.claude\skills\`

## Procedimiento

0. Confirmar que las rutas de paquetes existan. Si el path del monorepo cambió, pedirlo al usuario.
1. **Verificar vigencia**: para cada skill de área (`socarrandin-forms`, `socarrandin-upload`, `socarrandin-api`, `socarrandin-ui`, `socarrandin-theme`, `socarrandin-i18n`, `socarrandin-utils`), leer el SKILL.md y verificar en `packages/*/src` que:
   - Cada import/export citado sigue existiendo en el barrel (`index.ts`) del package correspondiente
   - Cada ejemplo con evidencia `archivo:linea` sigue apuntando a un archivo real (o al menos a un archivo que exista; actualizar `:linea` si cambió)
   - Cada prop/variant/hook documentado sigue en la firma
2. **Detectar drift**: si un componente se renombró, movió de carpeta, cambió de props o desapareció → re-curzar el contenido: actualizar el catálogo, ejemplos y anti-patterns del skill afectado contra el código real.
3. **Actualizar fuentes**: editar los SKILL.md en `socarrandin-expo-plugins/skills/` (fuente de verdad), NO los destinos.
4. **Desplegar**: copiar cada carpeta `skills/<nombre>/SKILL.md` a `.agents/skills/<nombre>/SKILL.md` y a `.claude/skills/<nombre>/SKILL.md`. Borrar skills de área que ya no existan en la fuente.
5. **Verificar**: tras copiar, confirmar que el frontmatter `name:` coincide con el nombre de carpeta y que no quedaron skills huérfanos en los destinos.

## Reglas

- La fuente de verdad es el plugin: **nunca** editar `.agents/skills/` o `.claude/skills/` a mano ni en este proceso (solo copiar).
- No inventar convenciones: si algo ya no está en `packages/*/src`, quitarlo o corregirlo; si falta algo nuevo que los componentes usan, agregarlo con evidencia.
- Si un pattern documentado NO se encuentra en el código (quedó obsoleto), eliminarlo o marcar que ya no aplica; no conservarlo.
- Reportar al final: qué skills se actualizaron, qué drift se encontró y qué se desplegó.

## Verificación

- `rg -l "socarrandin" E:\MY\_TOOLS\socarrandin-expo-ecosystem\.agents\skills\socarrandin-*\SKILL.md` matchea los 7 skills desplegados
- No hay diffs entre la fuente y los destinos (comparar `skills/*` vs `.agents/skills/*` y `.claude/skills/*`)