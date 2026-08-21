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

El endpoint de Contents puede resolver el symlink y mostrar el contenido del objetivo. Por eso los intentos anteriores podían parecer una copia de `AGENTS.md` aunque el objeto Git real era un enlace. Copiar esa salida como Markdown produciría una duplicación incorrecta.

### Solución correcta
Para recuperar el archivo hay que preservar la semántica Git:
1. obtener el blob literal `AGENTS.md`;
2. crear/usar una entrada de tree con `path=CLAUDE.md`, `mode=120000`, `type=blob`, `sha=<blob>`;
3. construir el tree sobre el `base_tree` actual de la rama destino;
4. crear commit con el tree nuevo y el HEAD actual como padre;
5. mover la ref de la rama sólo después de obtener el commit;
6. verificar que `CLAUDE.md` en el tree destino tenga `mode=120000` y que su blob contenga `AGENTS.md`.

Se instaló `.github/workflows/acr-restore-claude-symlink.yml` para ejecutar la recuperación desde un checkout Git y evitar la limitación del Contents API. El workflow usa `contents: write`, crea `ln -s AGENTS.md ACR/source/root/CLAUDE.md` y sólo hace commit si existe un cambio.

## Nueva regla ACR para symlinks
Un symlink es un objeto Git distinto de un archivo Markdown. El contenido del blob es sólo el destino del enlace. Nunca verificarlo por tamaño/contenido resuelto; verificar por `path + mode=120000 + blob literal`.

## Método de lotes adaptativos
ACR debe intentar lotes de varios archivos cuando el tamaño agregado sea seguro. Primero inventariar ruta, bytes, modo y SHA; luego agrupar. Cada archivo conserva estado independiente y debe verificarse individualmente. Un lote parcialmente fallido conserva los elementos ya verificados y reintenta sólo los fallidos. Después de cada lote se reconcilia fuente↔destino y el cursor avanza al primer archivo no verificado.

Archivos grandes se segmentan sólo cuando sea necesario. No se inventan umbrales fijos para el tamaño del lote: depende del límite efectivo del canal y del tamaño real de los archivos.

## Regla de lectura/escritura rápida <=100.000 caracteres
Para un archivo Git normal de hasta **100.000 caracteres**, sin necesidad de segmentación, ACR hará como máximo **dos intentos directos** de lectura completa y escritura completa. En la siguiente salida se verifica bytes/SHA/ruta. Si no coincide después del segundo intento, no se repite el mismo procedimiento: se registra la causa y se cambia integralmente de estrategia (blob directo, lote más pequeño, workflow/checkout o segmentación determinista), mientras se conserva el progreso de los demás archivos. Esto evita bucles y permite continuar.

Para un symlink `mode=120000`, el límite se aplica al blob literal del enlace. `CLAUDE.md` raíz tiene **9 caracteres** (`AGENTS.md`); no se debe descargar como el contenido resuelto de `AGENTS.md`.

## Incidencia de herramienta / tree
Se intentó crear el tree del symlink con `base_tree`, pero la herramienta recibió un valor que no era un Tree SHA válido y devolvió `422 base_tree is not a valid tree oid`. Esto **no** se trató como éxito y no se movió el Ledger.

La solución operativa es no inventar el tree SHA: obtener el tip/tree real de la rama mediante una fuente GitHub verificable o dejar que el workflow haga checkout de la rama y cree el symlink localmente. La documentación de GitHub confirma que `120000` es el modo correcto para symlinks y que un tree nuevo debe construirse sobre el tree existente cuando se quiere conservar el resto del repositorio.

## Estado actual
- Familia: `01-root-manifests`
- Último archivo verificado: `AGENTS.md`
- Siguiente: `CLAUDE.md`
- Verificados: 17/40
- Pendientes provisionales: 23
- Ledger: no avanzar hasta verificar el symlink Git real.
- Parche actualizado con commit `044c32153f2c3f7b7a8b3cd2be8b6d2263a14d91`.

## Regla de continuidad
Después de cualquier commit, comprobar evidencia de GitHub. No afirmar un workflow/trigger completado hasta observar su ejecución y resultado. No marcar `CLAUDE.md` como verificado por el mero hecho de que exista una ruta: debe comprobarse como symlink Git a `AGENTS.md`.
