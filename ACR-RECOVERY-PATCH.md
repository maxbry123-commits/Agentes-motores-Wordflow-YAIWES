# ACR Recovery Patch — OpenClaw Motor

## Método ACR por lotes — OBLIGATORIO
ACR debe trabajar por **bloques/lotes de archivos** siempre que sea técnicamente posible. No volver al flujo de una salida = un archivo salvo una excepción técnica concreta (symlink, binario incompatible, límite de tamaño o fallo individual).

### Regla rápida para archivos normales <=100.000 caracteres
1. Leer el archivo completo.
2. Escribirlo completo.
3. En la siguiente salida verificar ruta, tamaño y SHA.
4. Si falla tras un máximo de 2 intentos, cambiar de estrategia y continuar; nunca entrar en bucle.
5. El fallo de un archivo no detiene los demás elementos del lote.

### Reglas de lotes
- Primero inventariar ruta, bytes, modo Git y SHA fuente.
- Agrupar archivos pequeños/medianos en un bloque seguro por tamaño agregado.
- Intentar el bloque más grande que el canal permita sin truncamiento.
- Cada archivo conserva estado independiente: `PENDING`, `FETCHED`, `WRITTEN`, `VERIFIED`, `FAILED`, `SHA_MISMATCH`.
- Un lote sólo se cierra cuando cada elemento tiene verificación individual.
- Si un elemento falla, conservar los ya verificados y reintentar/cambiar método sólo para el fallido.
- Después de cada lote: reconciliar fuente↔destino y mover el cursor al primer archivo no verificado.
- No contar existencia, contenido parcial o intento de escritura como transferencia completada.
- Archivos grandes: lote individual o grupo pequeño; segmentar sólo cuando sea necesario.

### Regla de fallback literal
Si un archivo normal falla dos veces en el método de lote, en lugar de detener el proceso se usa lectura literal/input block del contenido completo, se escribe completo en una salida y en la salida siguiente se vuelve a leer el destino para comprobar tamaño y SHA. Después de `PASS` se continúa con el siguiente lote. No se permite un tercer intento idéntico ni un bucle.

### Symlinks
`CLAUDE.md` raíz es `mode=120000` y su blob Git literal es el objetivo del enlace. Contents API puede resolver el enlace y mostrar el contenido de `AGENTS.md`; eso no debe confundirse con el modo Git. La copia de contenido en `ACR/source/root/CLAUDE.md` queda marcada como recuperación de contenido/provisional hasta verificar el modo `120000` en destino. La estructura Git ideal se conserva con Blob → Tree (`mode=120000`) → Commit → Branch.

### ZIP / artefactos empaquetados
ACR puede leer un ZIP que haya descargado o generado si los bytes del ZIP están disponibles en el entorno de trabajo. El flujo es: descargar/generar ZIP → conservar bytes → inspeccionar/listar → extraer → auditar archivos → comparar SHA → escribir/verificar. Un ZIP no se considera transferido sólo por existir: sus archivos extraídos también requieren verificación. Para repositorios Git, preferir el árbol Git cuando se necesita conservar modos/symlinks; usar ZIP como transporte cuando simplifique la transferencia.

## Inventario de raíz confirmado
`openclaw/openclaw`: **61 entradas = 40 archivos + 21 directorios**.

## Estado
- Fuente: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- Familia: `01-root-manifests`
- Último verificado: `AGENTS.md`
- Siguiente: `CLAUDE.md`
- Verificados: 17/40
- Pendientes: 23

## Incidencia CLAUDE.md
Contents API resolvía el symlink y mostraba el contenido de `AGENTS.md`. Auditoría Git confirmó el tipo symlink en la fuente. La solución ideal conserva el symlink. Si una limitación de escritura impide crear `120000`, una copia provisional del contenido puede usarse explícitamente marcada, sin afirmar que conserva el modo.

## Regla de continuidad
Leer Ledger → parche → mapa de versiones → XRAY → bitácora → inventario fuente↔destino → elegir **bloque obligatorio** desde el primer pendiente → leer/escribir → verificar cada elemento → reconciliar → avanzar cursor.

No entrar en bucles. Buscar soluciones integrales y cambiar de estrategia después de dos intentos fallidos en un archivo normal <=100.000 caracteres.
