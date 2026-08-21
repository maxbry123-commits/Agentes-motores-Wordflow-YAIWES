# BITÁCORA ACR XRAY — historial operativo reutilizable

## Objetivo
Conservar conocimiento verificable para que otro GPT/agente pueda recuperar y continuar el trabajo sin depender de memoria conversacional. GitHub es la fuente persistente de verdad. No convertir hipótesis, planes o respuestas del asistente en hechos confirmados.

## Orden obligatorio de recuperación
1. `LEDGER.json` — si existe, cursor transaccional.
2. `ACR-RECOVERY-PATCH.md` / Recovery Patch vigente.
3. `ACR-VERSION-MAP.md`.
4. `ACR_OpenClaw_Recovery_Patch_XRAY_1.0.json` si existe.
5. `RAIZ-OPENCLAW-COMO-HACER-TODO.md`.
6. `PIPELINE/00_METODO_TRABAJO_Y_ARQUITECTURA.md`.
7. Esta bitácora.
8. Inventarios/manifiestos y árbol GitHub actual.

## ESTADO ACTUAL CONFIRMADO
- Repositorio de trabajo: `maxbry123-commits/Agentes-motores-Wordflow-YAIWES`.
- Rama: `main`.
- Fuente canónica OpenClaw fijada: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`.
- El árbol oficial de ese ref fue consultado mediante GitHub API.
- El repositorio de trabajo es multi-agente/multi-motor; no se debe mezclar OpenClaw con futuras raíces.
- `ROOTS/README.md` fue creado y verificado en GitHub como reserva estructural para `ROOTS/openclaw/` y futuras raíces independientes.
- Existe `FORENSIC-INVENTORY-2026-08-21.md` con el inventario inicial.
- El inventario inicial detectó 8 ZIP; ZIP 1 y ZIP 4 fueron observados con el mismo blob SHA y, por tanto, son duplicados exactos a nivel GitHub.
- El conector disponible no pudo descargar directamente el ZIP binario del `zipball` oficial; por tanto, la descarga/extracción real NO está marcada como completada.

## HALLAZGO CRÍTICO — VERIFICACIÓN CRUZADA CANÓNICO ↔ REPO ACTUAL
Se comparó el `package.json` del ref canónico con el `package.json` actualmente en `main`.

### Fuente canónica
`openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- versión observada: `2026.8.1`
- contiene bloque `openclaw.schemaVersions` con `state: 9` y `agent: 17`.
- declara `node-version.mjs` en el campo `files`.
- autor observado: `OpenClaw Foundation (https://openclaw.org)`.

### Repositorio actual
`maxbry123-commits/Agentes-motores-Wordflow-YAIWES@main`
- versión observada: `2026.7.1`
- NO contiene el bloque `openclaw.schemaVersions` observado en la fuente canónica.
- su campo `files` contiene `npm-shrinkwrap.json`, que no aparece en el fragmento inicial equivalente de la fuente canónica.
- autor observado: vacío.

### Veredicto de esta comparación
`package.json` actual = **MODIFIED / NO MATCH** respecto al ref canónico. No se puede tratar como copia válida del ref `a4178c7...` ni usarlo como autoridad para reconstruir la raíz.

Evidencia: lecturas GitHub de `openclaw/openclaw/package.json` en el ref fijado y de `maxbry123-commits/Agentes-motores-Wordflow-YAIWES/package.json` en `main`.

## REGLA DE VERIFICACIÓN CRUZADA — NO ALUCINAR
Toda afirmación sobre OpenClaw debe poder trazarse a: árbol/archivo real del ref canónico; archivo/árbol real de ZIP extraído; archivo/árbol real del destino; SHA/blob/tamaño/commit verificable; o prueba reproducible real.

No usar nombre de ZIP, lista aproximada, memoria del chat o inferencia para afirmar existencia/equivalencia.

## PLAN MAESTRO — LOOP/BÚCLE PARALELO
Cada lote termina todas sus subtareas antes de emitir la salida del lote. Se planifica el siguiente lote con tareas independientes en paralelo. `100%` solo con evidencia.

### T01 — BASELINE GITHUB
Branch, tip, árbol y documentos de control. Registrar commit/SHA. Gate: estado reproducible.

### T02 — XRAY REPO
Inventario completo, clasificación y duplicados. Salida: `FORENSIC-INVENTORY`.

### T03 — AUDITORÍA ZIP
Para cada ZIP: ruta, tamaño, blob SHA, descarga real, SHA-256, listado, envoltura, extracción, árbol relativo y artefactos. Salidas: `ZIP-MANIFEST`, `ZIP-XRAY-MATRIX`, `ZIP-EXTRACTION-MANIFEST`.

### T04 — ZIP↔ZIP
Comparar rutas, hashes, tamaños, subconjuntos, duplicados y piezas complementarias. Salidas: `ZIP-CROSS-COMPARISON`, `DUPLICATE-REPORT`.

### T05 — ÁRBOL CANÓNICO
Obtener el árbol exacto del ref fijado; separar blobs/trees/modes. Salida: `OPENCLAW-CANONICAL-TREE`.

### T06 — CANÓNICO↔CANDIDATOS
Para cada archivo candidato: ruta exacta, tipo/mode, tamaño, blob SHA si aplica, y clasificación MATCH/MISSING/EXTRA/MODIFIED/DUPLICATE/UNKNOWN. El `package.json` ya tiene evidencia de `MODIFIED/NO MATCH`. Salida: `ROOT-DIFF-MATRIX`.

### T07 — MULTI-AGENT ROOTS
Mantener `ROOTS/` fuera de documentación/control y reservar `ROOTS/openclaw/`, `ROOTS/<agente-02>/`, etc. No mezclar árboles. No mover la raíz actual hasta completar T06/T08.

### T08 — MANIFIESTO OPENCLAW
Ruta canónica → ruta ZIP → ruta destino `ROOTS/openclaw/...` → SHA/tamaño → acción KEEP/COPY/MERGE/EXCLUDE/REPAIR → evidencia. Gate obligatorio antes de publicar.

### T09 — BUILD TEMPORAL
Construir `ROOTS/openclaw/` en workspace temporal conservando rutas relativas y excluyendo dependencias/artefactos generados.

### T10 — LOCAL VERIFY
Conteos, rutas, tamaños, SHA-256, anchors, `git diff --check` y pruebas mínimas. PASS requerido para publicar.

### T11 — PUBLISH
Publicar por familias/lotes con commit y cursor registrados. No regenerar desde LLM.

### T12 — REMOTE READ-BACK
Releer GitHub después de cada lote; comparar ruta/tamaño/blob/commit. Fallo = REPAIR, no DONE.

### T13 — OPENCLAW BOOT VERIFY
Después de persistencia: validar workspace, instalar dependencias solo temporalmente y ejecutar procedimiento oficial disponible. Registrar PASS/FAIL real.

### T14 — FORENSIC XRAY FINAL
Cruce independiente: CANÓNICO ↔ ZIP EXTRAÍDO ↔ MANIFIESTO ↔ `ROOTS/openclaw` ↔ GITHUB READ-BACK. Dominios METHOD/REQUIREMENTS/TRACEABILITY/SOURCE/ZIP/ROOT/INTEGRITY/PUBLISH/REMOTE/TESTS/DOCS/NO_UNAUTHORIZED.

### T15 — MULTI-ROOT AUDIT
Confirmar aislamiento de OpenClaw, espacio para otros agentes, documentación fuera de roots y ausencia de duplicados accidentales.

### T16 — COMPLETION RECORD
DONE solo si T01–T15 tienen evidencia y read-back. Registrar task_id, objetivo, fuentes, outputs, paths, commits, SHA, verdict y next_task.

## FORMATO OBLIGATORIO DE SALIDA
```text
Tarea en curso: Txx — <nombre>
Total de tareas: 16
Tareas terminadas al 100%: <lista + evidencia>
Tareas pendientes: <lista>
Siguiente tarea: <Txx + subtareas paralelas>
Confirmación de tarea terminada al 100%: SÍ/NO — evidencia real
Bloqueos/reparación: <evidencia>
```

## LOOP / NO-STOP
Mientras haya tareas pendientes, continuar con el siguiente lote disponible. Fallo de herramienta → registrar → inspeccionar estado → cambiar mecanismo tras dos fallos iguales → reintentar determinísticamente. Si un bloqueo externo impide continuar, marcar `BLOCKED` con evidencia, nunca inventar `DONE`.

## ESTADO DEL CICLO ACTUAL
- Tarea en curso: T03/T04/T05/T06 en paralelo.
- Total: 16.
- T01/T02: evidencia de baseline/inventario inicial disponible; clasificación y auditoría ZIP siguen abiertas.
- T05: árbol canónico consultado.
- T06: primer hallazgo confirmado: `package.json` = MODIFIED/NO MATCH.
- T07: `ROOTS/README.md` creado y verificado; decisión estructural implementada, pero auditoría final pendiente.
- Siguiente lote: continuar T03/T04/T06 en paralelo, obtener evidencia real de los ZIP y ampliar la matriz canónica↔repo/ZIP con archivos raíz críticos.

## REGLA FINAL
La última salida del proyecto debe contener la verificación cruzada completa y la auditoría forense XRAY final. Una afirmación del asistente nunca sustituye evidencia.
