# Bitácora ACR XRAY — Auditoría y Recuperación OpenClaw

## Regla permanente
Toda anomalía o novedad relevante se registra antes de avanzar. `LEDGER.json` es la autoridad del cursor.

## Incidencia AGENTS.md
La reconstrucción manual produjo SHA distintos por pérdida de líneas en límites de respuestas/paginación. Solución: recuperar bytes directamente desde el commit fijado y cerrar sólo con `git hash-object` igual al SHA fuente.

- Fuente: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- SHA AGENTS: `7fcee34720673a4285bd35b7613cc226c6eed413`
- Estado final: `VERIFIED_WRITE`

## Incidencia CLAUDE.md
`CLAUDE.md` no debe copiarse como Markdown independiente. La fuente lo utiliza como symlink hermano de `AGENTS.md`. El endpoint de Contents puede resolver el enlace y mostrar el contenido objetivo, por lo que copiar esa salida crearía una duplicación incorrecta.

### Solución
Se añadió `.github/workflows/acr-restore-claude-symlink.yml` para que GitHub Actions ejecute:
1. comprobar que existe `ACR/source/root/AGENTS.md`;
2. eliminar cualquier `CLAUDE.md` incorrecto;
3. crear `ln -s AGENTS.md ACR/source/root/CLAUDE.md`;
4. comprobar `readlink`;
5. hacer commit/push sólo si hay cambio.

Commit que instala el mecanismo: `11d99623017998256e195834f563e05471fad822`.

## Método de lotes adaptativos
Archivos pequeños/medianos pueden agruparse cuando el tamaño total sea seguro. La integridad sigue siendo individual por ruta + SHA. Un lote parcialmente fallido conserva sólo elementos individualmente verificados.

## Inventario raíz
`openclaw/openclaw` está confirmado en 61 entradas de raíz: 40 archivos + 21 directorios. Los directorios se recorren recursivamente y no se cuentan como archivos raíz.

## Estado actual
- Familia: `01-root-manifests`
- Último archivo verificado: `AGENTS.md`
- Siguiente: `CLAUDE.md`
- Verificados: 17/40
- Pendientes provisionales: 23
- Ledger: no avanzar hasta verificar el symlink Git real.

## Regla de continuidad
Después de cualquier commit, comprobar evidencia de GitHub. No afirmar un workflow/trigger completado hasta observar su ejecución y resultado. No marcar `CLAUDE.md` como verificado por el mero hecho de que exista una ruta: debe comprobarse como symlink Git a `AGENTS.md`.
