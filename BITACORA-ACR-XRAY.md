# Bitácora ACR XRAY — Auditoría y Recuperación OpenClaw

## Entrada 2026-08-20 — Salida 94

### Incidente
Durante la recuperación de `AGENTS.md` se detectó que el archivo existente en `ACR/source/root/AGENTS.md` no coincidía con el blob fuente fijado.

- Fuente fijada: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- SHA/blob fuente esperado: `7fcee34720673a4285bd35b7613cc226c6eed413`
- SHA/blob encontrado inicialmente en destino: `5002767dfe77512d7b0f6dcb88df67ab1e518a56`
- Diagnóstico: copia antigua/incompleta; la existencia de la ruta no demuestra transferencia válida.
- Estado: `SHA_MISMATCH` / `RETRY_PENDING`.

### Evidencia y aprendizaje
La recuperación correcta exige comparar el blob exacto del commit fuente fijado, no una versión actual, resumen, memoria del chat ni una copia previa del destino. Un archivo parcialmente recuperado nunca debe marcarse como `VERIFIED`.

La fuente contiene secciones adicionales de política, arquitectura, auditoría de identidad, comandos, validación, GitHub/PR, tooling, código, tests, seguridad y operaciones que no deben perderse durante la reconstrucción.

### Solución prescrita
1. Mantener el cursor en `AGENTS.md`.
2. Recuperar el blob completo del commit fijado.
3. Escribir el contenido íntegro en `ACR/source/root/AGENTS.md`.
4. Obtener evidencia del destino y comparar SHA/contenido.
5. Sólo si coincide, registrar `VERIFIED` en el Ledger y avanzar.
6. Si vuelve a fallar, registrar el nuevo síntoma antes de continuar.

### Regla permanente añadida
**Cada fallo, discrepancia de SHA, novedad fuera de lo normal, truncamiento, bloqueo de escritura o descubrimiento relevante debe registrarse en esta bitácora antes de continuar con la recuperación.**

La bitácora documenta aprendizaje y diagnóstico; `LEDGER.json` continúa siendo la autoridad del cursor y estado de transferencia.

## Método de lotes adaptativos
Los archivos pequeños/medianos pueden procesarse en grupos cuando el tamaño combinado sea seguro. Los archivos grandes se procesan individualmente o segmentados. Cada archivo mantiene verificación independiente por ruta + SHA. Un lote parcialmente fallido conserva como válidos únicamente los elementos individualmente verificados.

## Regla de recuperación para futuros GPT/agentes
Ante cualquier inconsistencia:
- detener avance del cursor;
- registrar el incidente;
- conservar el SHA/ref fuente;
- identificar causa;
- aplicar solución reproducible;
- verificar fuente↔destino;
- actualizar Ledger;
- sólo entonces continuar.

## Entrada 2026-08-20 — Salida 105

### Nueva incidencia: reconstrucción escrita pero SHA no coincide
Después de ejecutar una actualización real de `ACR/source/root/AGENTS.md` desde el contenido recuperado del blob fuente, GitHub devolvió:

- commit de destino: `a69bdf7e5864468fa6248ea5a2d446533be42f49`
- blob de destino: `f1331f42ada9397d98b605ffce253307a1231a39`
- SHA fuente fijado: `7fcee34720673a4285bd35b7613cc226c6eed413`
- resultado: `SHA_MISMATCH`

### Diagnóstico
La operación de escritura sí ocurrió, pero la reconstrucción manual del contenido no fue byte-exacta respecto al blob fuente. Por seguridad, el archivo sigue sin estar `VERIFIED` y el Ledger no se mueve.

### Aprendizaje reutilizable
Cuando la fuente exige coincidencia criptográfica exacta, una reconstrucción manual del contenido es una operación de riesgo aunque el texto aparente ser completo. El método debe tratar cualquier SHA diferente como fallo de transferencia, no como éxito semántico.

### Acción obligatoria
1. Mantener `AGENTS.md` como cursor.
2. No incrementar `root_files_verified`.
3. Recuperar nuevamente el blob fuente exacto.
4. Resolver la transferencia sin alterar contenido.
5. Verificar SHA de destino.
6. Sólo después actualizar Ledger y continuar.

## Estado actual
- Familia: `01-root-manifests`
- Cursor: `AGENTS.md`
- `AGENTS.md`: `SHA_MISMATCH` / `RETRY_PENDING`
- Raíz fuente auditada: 61 entradas = 40 archivos + 21 directorios.
- No contabilizar archivos por mera existencia de ruta.
