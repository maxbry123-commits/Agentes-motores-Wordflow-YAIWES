# ACR OpenClaw Motor Recovery

Estado: PARTIDO EN LOTES
Fuente: openclaw/openclaw
Objetivo: motor para Wordflow, sin UI.

## División de trabajo

- Parte 01 — raíz y manifests del workspace
- Parte 02 — `src/` núcleo del motor
- Parte 03 — `packages/` paquetes internos
- Parte 04 — `extensions/` capacidades/plugins del motor
- Parte 05 — validación, exclusiones, checksums y reconstrucción

## Exclusiones

- `ui/**`
- `node_modules/**`
- `.pnpm-store/**`
- caches y artefactos generados

## Método de transferencia

Cada parte se procesa independientemente. ACR mantiene inventario de rutas, tamaño, SHA y estado. Los lotes se pueden reintentar sin repetir los lotes ya validados.

## Regla

No se considera terminada una parte hasta que sus archivos estén verificados. La UI no forma parte del motor recuperado.
