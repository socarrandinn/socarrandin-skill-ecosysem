# Resumen de arquitectura: proyecto-prueba
## 1. Estructura y convenciones de nombres
Fixture de prueba. Carpeta src/ con archivos kebab-case.
## 2. Tech stack y versiones
Node.js 22, TypeScript 5.6.
## 3. Dependencias y gestión de paquetes
npm. Express, zod, vitest.
## 4. Patrones de diseño del sistema
Capas: routes → controllers → services.
## 5. Manejo de estado
No aplica.
## 6. API y servicios
Prefijo /api/v1. Envoltura { data }.
## 7. Datos y validación
zod en cada endpoint.
## 8. Testing y convenciones
vitest, tests colocado junto al fuente (<archivo>.test.ts).
## 9. Config, CI/CD y entorno
.env.example validado con zod.
## 10. Reglas de oro (no negociables)
Todo endpoint valida con zod antes de tocar el servicio.
Toda feature nueva lleva test.