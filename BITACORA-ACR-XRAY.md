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
- `FORENSIC-CROSSCHECK-OPENCLAW.md` fue creado con la primera matriz de discrepancias verificadas.

## HALLAZGOS DE VERIFICACIÓN CRUZADA CANÓNICO ↔ REPO ACTUAL

### 1. `package.json`
Fuente canónica `openclaw/openclaw@a4178c7...`:
- versión observada `2026.8.1`;
- bloque `openclaw.schemaVersions` con `state: 9` y `agent: 17`;
- autor `OpenClaw Foundation (https://openclaw.org)`;
- declara `node-version.mjs` en `files`.

Repo actual `main`:
- versión observada `2026.7.1`;
- no contiene el bloque `openclaw.schemaVersions` observado en la fuente canónica;
- autor vacío;
- contiene `npm-shrinkwrap.json` en `files`.

Veredicto: **MODIFIED / NO MATCH**. No usar este archivo actual como copia canónica.

### 2. `node-version.mjs`
- Existe en el ref canónico y fue leído directamente; blob observado `dc7876dd0ce35116aaef535d342647ebb1ad16e7`.
- No existe en la raíz actual del repositorio de trabajo (`Not Found`).

Veredicto: **MISSING** en el repo actual respecto al ref canónico.

### 3. `npm-shrinkwrap.json`
- No existe en el ref canónico fijado (`Not Found`).
- Existe en la raíz actual del repositorio de trabajo.

Veredicto: **EXTRA / NON-CANONICAL** respecto al ref fijado.

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
Para cada archivo candidato: ruta exacta, tipo/mode, tamaño, blob SHA si aplica, y clasificación MATCH/MISSING/EXTRA/MODIFIED/DUPLICATE/UNKNOWN. Hallazgos actuales: `package.json` MODIFIED/NO MATCH; `node-version.mjs` MISSING; `npm-shrinkwrap.json` EXTRA/NON-CANONICAL. Salida: `ROOT-DIFF-MATRIX`.

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
- Tarea en curso: T03/T04/T06 en paralelo; T05 canónico continúa como referencia.
- Total: 16.
- T01/T02: baseline/inventario inicial disponibles; clasificación detallada sigue abierta.
- T05: árbol canónico consultado.
- T06: tres hallazgos confirmados (`package.json` MODIFIED, `node-version.mjs` MISSING, `npm-shrinkwrap.json` EXTRA).
- T07: `ROOTS/README.md` creado y verificado; layout reservado, auditoría final pendiente.
- T03/T04: bloqueados parcialmente por la limitación actual para obtener los bytes binarios de los ZIP del repositorio mediante el conector. No se declara descarga/extracción.
- Siguiente lote en paralelo: ampliar T06 con más archivos raíz críticos y continuar T03/T04 buscando un mecanismo verificable de adquisición de los ZIP; después construir el manifiesto.

## REGLA FINAL
La última salida del proyecto debe contener la verificación cruzada completa y la auditoría forense XRAY final. Una afirmación del asistente nunca sustituye evidencia.
