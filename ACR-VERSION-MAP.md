# ACR Version Map — mapa de recuperación y memoria

## Propósito
Mapa compacto para que un GPT/agente pueda identificar qué versión/branch ACR consultar antes de continuar una recuperación. Este archivo no sustituye `LEDGER.json`; el ledger es la fuente autoritativa del cursor operativo.

## Ramas ACR identificadas en la auditoría
| Versión/branch | Uso | Estado conocido |
|---|---|---|
| `acr/openclaw-motor-recovery` | línea histórica de recuperación | conservar como evidencia hasta cerrar auditoría |
| `acr/openclaw-motor-recovery-v2` | rama ACR operativa con parche/mapa y ledger | rama de trabajo actual documentada |
| `acr/openclaw-motor-recovery-v3` | evolución histórica | conservar como evidencia |
| `acr/openclaw-motor-recovery-v4` | evolución histórica | conservar como evidencia |
| `acr/openclaw-motor-recovery-v5` | evolución histórica | conservar como evidencia |
| `acr/openclaw-motor-recovery-v6` | evolución histórica | conservar como evidencia |
| `acr/openclaw-motor-recovery-v7` | evolución histórica | conservar como evidencia |
| `acr/openclaw-motor-recovery-v8` | evolución histórica | conservar como evidencia |
| `acr/openclaw-motor-recovery-v9` | evolución histórica / estado posterior | no asumir que contiene el cursor operativo de v2 |

## Regla crítica de versiones
No asumir que la versión numéricamente más alta es la fuente correcta. Antes de continuar, verificar el contenido, el ledger, el commit fuente y el SHA del branch. Una rama histórica puede contener evidencia aunque no sea el cursor operativo.

## Fuente OpenClaw fijada
`openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`

## Familias ACR
1. `01-root-manifests` → `ACR/source/root/`
2. `02-src` → `ACR/source/src/`
3. `03-packages` → `ACR/source/packages/`
4. `04-extensions` → `ACR/source/extensions/`
5. `05-validation-reconstruction` → `ACR/validation/`

## Cursor operativo conocido
- Ledger: salida 14 → siguiente 15.
- Último archivo verificado: `.oxlintrc.json`.
- Último SHA fuente: `cfa18de8e1498d7dc189daff669faca40d99881a`.
- Último commit destino: `66049d58102870f9c09b828417b5764fddc6ba59`.
- Siguiente acción: continuar inventario de `01-root-manifests` y verificar fuente-vs-destino antes de cerrar la familia.

## Jerarquía de recuperación
1. `LEDGER.json` — cursor y evidencia transaccional.
2. `ACR-RECOVERY-PATCH.md` — reglas de ejecución y recuperación.
3. `ACR-VERSION-MAP.md` — selección de versión/branch y relaciones entre ramas.
4. `ACR_OpenClaw_Recovery_Patch_XRAY_1.0.json` — mapa estructurado.
5. `BITACORA-ACR-XRAY.md` — lecciones históricas y problemas/soluciones.
6. Manifiestos e inventarios — evidencia de qué debe existir.

## Estado vs. historial
Nunca interpretar una salida conversacional como prueba de una escritura. Una operación sólo está confirmada si GitHub devuelve evidencia verificable (commit/SHA o lectura posterior del contenido). Los documentos pueden describir operaciones pendientes; eso no las convierte en hechos consumados.

## Criterio de cierre
La integración a `main` sólo puede declararse completa después de comparar refs/SHA completos, verificar que los archivos ACR esperados existen en `main`, y comprobar que parche, bitácora, mapa y ledger apuntan al mismo estado operativo.
