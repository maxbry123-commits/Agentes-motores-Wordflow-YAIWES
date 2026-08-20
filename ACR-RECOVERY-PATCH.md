# ACR Recovery Patch — OpenClaw Motor

## Método de descarga por lotes adaptativos
ACR puede procesar varios archivos en un lote cuando el tamaño total sea seguro para el canal. La unidad de integridad sigue siendo **cada archivo**, nunca el lote.

### Reglas
1. Inventariar ruta, tamaño y SHA fuente antes de agrupar.
2. Agrupar archivos pequeños/medianos sólo cuando la suma estimada permanezca dentro del límite seguro del canal.
3. Archivos grandes: lote individual o grupo pequeño; si exceden el límite, segmentar.
4. Cada archivo mantiene estado independiente: `PENDING`, `FETCHED`, `WRITTEN`, `VERIFIED`, `FAILED`, `SHA_MISMATCH`.
5. El lote sólo queda `VERIFIED` cuando todos sus archivos están individualmente verificados.
6. Un fallo no invalida los archivos ya verificados del lote; sólo se reintenta el elemento fallido.
7. Registrar por archivo: `batch_id`, ruta, bytes fuente, SHA fuente, bytes destino, SHA destino, commit destino, estado y errores.
8. Tras cada lote, reconciliar fuente↔destino y mover el cursor al primer archivo no verificado.
9. Nunca contar contenido parcial, una ruta existente o un intento de escritura como descarga completada.
10. Los umbrales de tamaño son adaptativos: se determinan por el límite efectivo del canal y el tamaño real del archivo, no por un número fijo inventado.
11. Archivos muy grandes deben recuperarse por segmentos deterministas y reconstruirse antes de verificar SHA.
12. Antes de cerrar una familia, reconciliar todos sus archivos por ruta + SHA y detectar faltantes/extras.

### Objetivo
Aumentar el rendimiento de ACR sin perder trazabilidad: un lote puede acelerar la transferencia, pero **SHA individual + evidencia de GitHub siguen siendo la autoridad**.

## Inventario de raíz confirmado
`openclaw/openclaw` contiene **61 entradas en la raíz: 40 archivos + 21 directorios**. Los directorios no se cuentan como archivos descargados; se inventarían recursivamente por separado.

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

**Regla:** existir en destino no implica estar transferido. Sólo `ruta + SHA fuente + evidencia de destino` puede cerrar un archivo.

## Protocolo de continuidad
1. Leer `LEDGER.json`.
2. Leer este parche.
3. Leer `ACR-VERSION-MAP.md`.
4. Leer XRAY JSON.
5. Revisar bitácora para errores/soluciones.
6. Comprobar inventario fuente↔destino.
7. Continuar desde el primer archivo no verificado del ledger.

## Estado conocido
- Fuente: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- Familia: `01-root-manifests`
- Raíz: 61 entradas / 40 archivos / 21 directorios
- Último archivo verificado: `.pre-commit-config.yaml`
- Siguiente: `AGENTS.md`
- `AGENTS.md`: recuperado de fuente, pendiente de escritura/verificación como transferencia.

## Incidencias reutilizables
- Blob truncado → recuperar completo o segmentar/reconstruir.
- SHA diferente → mantener pendiente; no contar.
- Escritura parcial → identificar el parcial y reconstruir desde fuente.
- Inventario truncado → dividir por familias/directorios.
- Lote parcialmente fallido → conservar sólo elementos individualmente verificados y reintentar los fallidos.

## Regla final
No avanzar el cursor sobre un archivo pendiente. No declarar un lote completo hasta verificar cada elemento. No modificar `main` como integración final hasta disponer de SHA y contenido verificables.
