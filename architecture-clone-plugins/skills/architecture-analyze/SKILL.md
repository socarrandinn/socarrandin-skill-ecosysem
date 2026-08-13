---
name: architecture-analyze
description: Use cuando hay que analizar la arquitectura de un proyecto y clonar sus convenciones: "clona la arquitectura", "analiza este proyecto", "¿cómo se construye este proyecto?". Produce resumen de patrones + state.json.
---

# architecture-analyze

## Misión
Descubrir cómo se construye un proyecto: patrones, decisiones y convenciones que definen su arquitectura. NO producir inventario de archivos.

## Destino y estado
- Carpeta de estado: `<proyecto>/.architecture-clone/` (crear si falta)
- Escribir `state.json` al terminar con: `proyecto` (ruta absoluta), `nombre` (slug kebab-case), `paso: "analyze"`, `resumen` (ruta al summary), `fecha` (ISO). Respetar `state.schema.json` del plugin.
- Si `state.json` existe con `paso: "generate"` o `"listo"` → NO ejecutar análisis completo; devolver control al orquestador.

## Procedimiento
1. Raíz del proyecto: ruta dada por el usuario o el proyecto actual. Si el usuario da un subdirectorio de app, analizar SOLO esa app.
2. Leer manifiestos y config raíz: gestor de paquetes (package.json + package-lock/pnpm-lock/yarn.lock, requirements.txt/pyproject.toml, go.mod, Cargo.toml, pom.xml…), tsconfig, .env.example, Dockerfile, `.github/workflows/`, Makefile, scripts de build.
3. Mapear estructura de carpetas (2-3 niveles). Excluir dependencias (node_modules, vendor, .venv, dist, build, .git) — no aportan decisiones.
4. Leer una muestra representativa de cada capa/área: al menos 2-3 archivos por capa (routes, controllers, services, models, tests…). Leer archivos REALES: cada convención declarada debe poder trazarse a un archivo concreto.
5. Las 9 dimensiones de análisis (sección siguiente). Para cada una: extraer la convención REAL (no la ideal).
6. Escribir `architecture-summary.md` con el contrato de salida exacto y `state.json`.

## Dimensiones de análisis (todas obligatorias)
1. **Estructura y nombres**: organigrama de carpetas, patrón de nombres de archivo (kebab-case, PascalCase, camelCase), dónde vive cada tipo de archivo, reglas de exports/imports (sufijos `.js`, barrels, etc.)
2. **Tech stack**: lenguajes, frameworks, runtimes, build tools, transpiladores, versión de Node/Python/etc. y de TS si aplica
3. **Dependencias**: gestor de paquetes, dependencias clave de runtime y dev (solo las que definen arquitectura: ORM, validación, testing, auth, no listar utilitarios menores)
4. **Patrones de diseño**: MVC, capas, microservicios, hexagonal, feature-first, etc. Flujo de una petición típica (ruta → controlador → servicio → repositorio → …)
5. **Estado**: manejo de estado (si aplica): stores, contexto, estado de servidor/caché, persistencia
6. **API/servicios**: convención de rutas (prefijo base, versionado, REST vs RPC), envoltura de respuestas (`{ data }`, `{ error: { code, message } }`), códigos de error, auth por ruta
7. **Datos**: modelos/schemas, validación (zod, Joi, Pydantic…), dónde se definen, migraciones/seed
8. **Testing**: framework, ubicación (colocado vs carpeta tests), convenciones de nombres, patrón de test (unit/integration/e2e), cómo se ejecuta (script npm)
9. **Config y entorno**: env vars y su validación, CI/CD (workflows, jobs, comandos), scripts de build/deploy, configs de linter/formatter

## Contrato de salida — architecture-summary.md
El resumen DEBE contener estas secciones, en este orden, con estas cabeceras EXACTAS:

```
# Resumen de arquitectura: <nombre proyecto>
## 1. Estructura y convenciones de nombres
## 2. Tech stack y versiones
## 3. Dependencias y gestión de paquetes
## 4. Patrones de diseño del sistema
## 5. Manejo de estado
## 6. API y servicios
## 7. Datos y validación
## 8. Testing y convenciones
## 9. Config, CI/CD y entorno
## 10. Reglas de oro (no negociables)
```

Reglas del contenido:
- Cada sección: convenciones CONCRETAS y accionables ("los tests viven en tests/, archivo `<x>.test.ts`", no "el proyecto tiene tests")
- Cada convención con evidencia: `ruta/archivo.ts:linea` cuando aplique
- Sección 10: 3-7 reglas no negociables que cualquier código nuevo DEBE cumplir (ej: "todo endpoint valida con zod antes de tocar el servicio", "toda feature nueva lleva test")
- PROHIBIDO: listas de archivos, árboles de carpetas completos, repetir contenido de manifiestos
- Si una dimensión no aplica, escribir "No aplica" en UNA línea — nunca omitir la sección
- Contenido en español; nombres técnicos, comandos y código en su idioma original

## Regla de oro
- No analizar más de lo necesario: si el análisis se alarga, priorizar las capas por las que pasa una petición típica y las reglas de la sección 10.
- No inventar convenciones: si no hay evidencia en archivos, no declararla como convención.