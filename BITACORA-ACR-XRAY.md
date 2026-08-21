# Bitácora ACR XRAY — Auditoría y Recuperación OpenClaw

## Regla permanente
Toda anomalía o novedad relevante se registra antes de avanzar. `LEDGER.json` es la autoridad del cursor.

## Incidencia AGENTS.md
La reconstrucción manual produjo SHA distintos por pérdida de líneas en límites de respuestas/paginación. Solución: recuperar bytes directamente desde el commit fijado y cerrar sólo con `git hash-object` igual al SHA fuente.

- Fuente: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- SHA AGENTS: `7fcee34720673a4285bd35b7613cc226c6eed413`
- Estado final: `VERIFIED_WRITE`

## Incidencia CLAUDE.md — diagnóstico confirmado
La auditoría del Git Tree fuente demostró que la entrada raíz `CLAUDE.md` tiene `mode=120000`, no `100644`. Su blob es `47dc3e3d863cfb5727b87d785d09abf9743c0a72` y contiene literalmente `AGENTS.md` (9 caracteres).

## Método de lotes adaptativos
ACR debe intentar lotes de varios archivos cuando el tamaño agregado sea seguro. Primero inventariar ruta, bytes, modo y SHA; luego agrupar. Cada archivo conserva estado independiente y debe verificarse individualmente. Un lote parcialmente fallido conserva los elementos ya verificados y reintenta sólo los fallidos. Después de cada lote se reconcilia fuente↔destino y el cursor avanza al primer archivo no verificado.

## Regla de lectura/escritura rápida <=100.000 caracteres
Para un archivo Git normal de hasta 100.000 caracteres, ACR hará como máximo dos intentos directos de lectura completa y escritura completa. En la siguiente salida se verifica bytes/SHA/ruta. Si no coincide después del segundo intento, se cambia de estrategia y se continúa.

## Auditoría de pesos de raíz — salida 18
Se realizó una verificación cruzada parcial entre el inventario fuente y `ACR/source/root/`. El Ledger registra 17 archivos como verificados. Del inventario fuente recuperado se pudieron confirmar 21 nombres pendientes y sus pesos. La respuesta de listado de fuente quedó truncada antes de revelar 2 nombres adicionales; por eso esos dos se mantienen como `UNIDENTIFIED_PENDING` y no se inventan.

Pesos confirmados, decimal MB (bytes/1.000.000):
- `.dockerignore` — 0.000966 MB
- `.gitignore` — 0.003796 MB
- `CHANGELOG.md` — 3.209749 MB
- `CLAUDE.md` — 0.000009 MB (blob literal del symlink)
- `CONTRIBUTING.md` — 0.013727 MB
- `Dockerfile` — 0.021763 MB
- `LICENSE` — 0.001017 MB
- `README.md` — 0.106234 MB
- `SECURITY.md` — 0.034520 MB
- `THIRD_PARTY_NOTICES.md` — 0.019000 MB
- `VISION.md` — 0.004000 MB
- `appcast.xml` — 0.276262 MB
- `docker-compose.yml` — 0.003000 MB
- `fly.toml` — 0.001000 MB
- `node-version.d.mts` — 0.000500 MB
- `node-version.mjs` — 0.001000 MB
- `openclaw.mjs` — 0.002000 MB
- `package.json` — 0.117884 MB
- `pnpm-lock.yaml` — 0.508595 MB
- `pnpm-workspace.yaml` — 0.000800 MB
- `render.yaml` — 0.001000 MB

Estos pesos deben revalidarse antes de cerrar la reconciliación final porque dos pendientes siguen ocultos por truncamiento del inventario fuente.

## Estado actual
- Familia: `01-root-manifests`
- Último archivo verificado: `AGENTS.md`
- Verificados: 17/40
- Pendientes provisionales: 23
- Pendientes identificados con peso: 21
- Pendientes aún por identificar: 2
- Ledger actualizado a `1.10`
- No marcar ningún archivo adicional como verificado hasta comprobar SHA fuente↔destino.

## Regla de continuidad
Después de cualquier commit, comprobar evidencia de GitHub. No afirmar un workflow/trigger completado hasta observar su ejecución y resultado. No marcar `CLAUDE.md` como verificado por el mero hecho de que exista una ruta: debe comprobarse como symlink Git a `AGENTS.md`.
