# ACR Recovery Patch — OpenClaw Motor

## Método ACR por lotes adaptativos
ACR debe intentar primero lotes de varios archivos cuando el tamaño agregado sea seguro para el canal. La integridad nunca es del lote: es **por archivo**.

### Reglas operativas
1. Fijar commit fuente antes de leer.
2. Inventariar ruta, tamaño, modo Git y SHA fuente antes de agrupar.
3. Agrupar archivos pequeños/medianos cuando la suma real permanezca dentro del límite efectivo del canal.
4. Archivos grandes: lote individual o grupo pequeño; segmentar sólo cuando sea necesario.
5. Cada archivo conserva estado independiente: `PENDING`, `FETCHED`, `WRITTEN`, `VERIFIED`, `FAILED`, `SHA_MISMATCH`.
6. Un lote sólo queda `VERIFIED` cuando todos sus elementos están individualmente verificados.
7. Un fallo no invalida elementos ya verificados; reintentar sólo el elemento fallido.
8. Registrar por archivo: `batch_id`, ruta, bytes, modo, SHA fuente, SHA destino, commit destino, estado y errores.
9. Después de cada lote, reconciliar fuente↔destino y mover el cursor al primer archivo no verificado.
10. Nunca contar una ruta existente, contenido parcial o intento de escritura como descarga completada.
11. Para archivos muy grandes usar segmentos deterministas y reconstruir antes de verificar SHA.
12. Antes de cerrar una familia, reconciliar rutas, modos y SHA y detectar faltantes/extras.
13. Si un archivo es un symlink Git (`mode=120000`), no copiar el contenido resuelto por Contents API como archivo normal.
14. Para symlinks usar Git Tree API: blob = texto literal del destino del enlace; entrada del tree = `mode=120000`, `type=blob`, `sha=<blob>`; conservar el tree existente como `base_tree`.
15. Verificar symlink con árbol Git: ruta + `mode=120000` + blob de destino. No inferir el tipo por el contenido mostrado por Contents API.
16. Si falta el SHA del tip/tree de la rama destino, no inventarlo ni crear un tree sin `base_tree`; recuperar el tip mediante una fuente GitHub verificable o usar un workflow con checkout de la rama.
17. Toda anomalía se registra en bitácora antes de avanzar.
18. Cada modificación real debe quedar asociada a evidencia de commit/push; un trigger sólo se declara ejecutado cuando existe evidencia de run y resultado.

## Inventario de raíz confirmado
`openclaw/openclaw` contiene **61 entradas en la raíz: 40 archivos + 21 directorios**. Los directorios son contenedores y se recorren recursivamente; no se cuentan como archivos raíz.

## Código operativo ACR
- `ACR/recovery/ACR_OpenClaw_Recovery_Patch_XRAY_1.0.json`
- `ACR/recovery/LEDGER.json`
- `ACR-RECOVERY-PATCH.md`
- `ACR-VERSION-MAP.md`
- `BITACORA-ACR-XRAY.md`
- `ACR/source/root/`
- `ACR/source/src/`
- `ACR/source/packages/`
- `ACR/source/extensions/`
- `ACR/validation/`

**Regla:** existir en destino no implica transferencia. Sólo `ruta + modo + SHA fuente + evidencia destino` puede cerrar un archivo.

## Protocolo de continuidad
1. Leer `LEDGER.json`.
2. Leer este parche.
3. Leer `ACR-VERSION-MAP.md`.
4. Leer XRAY JSON.
5. Leer bitácora.
6. Auditar inventario fuente↔destino.
7. Elegir lote seguro desde el primer archivo no verificado.
8. Verificar cada elemento antes de mover el cursor.

## Estado conocido
- Fuente: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- Familia: `01-root-manifests`
- Raíz: 61 entradas / 40 archivos / 21 directorios
- Último archivo verificado: `AGENTS.md`
- SHA `AGENTS.md`: `7fcee34720673a4285bd35b7613cc226c6eed413`
- Siguiente: `CLAUDE.md`
- `CLAUDE.md` fuente: `mode=120000`, blob `47dc3e3d863cfb5727b87d785d09abf9743c0a72`, contenido literal `AGENTS.md`

## Incidencias reutilizables
- Blob truncado → recuperar completo o segmentar/reconstruir.
- SHA diferente → mantener pendiente; no contar.
- Escritura parcial → identificar el parcial y reconstruir desde fuente.
- Inventario truncado → dividir por familias/directorios.
- Lote parcialmente fallido → conservar sólo elementos individualmente verificados.
- Contents API resuelve un symlink → consultar Git Tree API y conservar `mode=120000`.
- SHA/tree de rama no disponible → no inventar; usar una operación verificable desde checkout o recuperar el tip/tree real.

## Incidencia `AGENTS.md` — solución
La reconstrucción manual desde respuestas truncadas produjo SHA distintos. Se corrigió recuperando los bytes directamente del commit fijado y cerrando sólo cuando `git hash-object` coincidió con `7fcee34720673a4285bd35b7613cc226c6eed413`.

## Incidencia `CLAUDE.md` — solución definitiva
La consulta Contents devolvía el contenido de `AGENTS.md`, ocultando que la entrada raíz era un symlink. La auditoría del Git Tree del commit fuente confirmó:
- ruta: `CLAUDE.md`
- modo: `120000`
- tipo: `blob`
- blob: `47dc3e3d863cfb5727b87d785d09abf9743c0a72`
- blob literal: `AGENTS.md`

Por tanto, la recuperación correcta es crear un symlink Git `CLAUDE.md → AGENTS.md`, no duplicar los 62 KB de `AGENTS.md`.

Se instaló `.github/workflows/acr-restore-claude-symlink.yml` para hacer la operación desde checkout Git, donde `ln -s` conserva el tipo de enlace. El workflow sólo hace commit si existe un cambio y usa `contents: write`.

## Regla final
No avanzar el cursor sobre un archivo pendiente. No declarar un lote completo hasta verificar cada elemento. No modificar `main` como integración final hasta disponer de SHA, modo y contenido verificables.
