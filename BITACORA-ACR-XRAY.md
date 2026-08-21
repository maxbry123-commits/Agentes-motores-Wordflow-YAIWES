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
- Fuente canónica OpenClaw fijada para esta recuperación: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`.
- El árbol oficial de ese ref fue consultado mediante GitHub API y contiene, entre otros, `.agents/`, `.agents/skills/...` y el árbol versionado del proyecto.
- El repositorio de trabajo no debe considerarse exclusivamente OpenClaw: debe conservar espacio estructural independiente para otras raíces/agentes/motores.
- El método `RAIZ-OPENCLAW-COMO-HACER-TODO.md` ya documenta ZIP → extracción → eliminación de envoltura → conservación de rutas relativas → escritura directa → read-back.
- Existe `FORENSIC-INVENTORY-2026-08-21.md` con el inventario inicial del repositorio.
- Inventario inicial detectó 8 ZIP; ZIP 1 y ZIP 4 fueron observados con el mismo blob SHA y, por tanto, son duplicados exactos a nivel GitHub.
- No se autoriza todavía declarar qué ZIP es fuente válida, parte, duplicado funcional o artefacto hasta inspeccionar su contenido.

## REGLA DE VERIFICACIÓN CRUZADA — NO ALUCINAR
Toda afirmación sobre OpenClaw debe poder trazarse a una de estas evidencias:
1. árbol/archivo real de `openclaw/openclaw` en el ref fijado;
2. archivo/árbol real de un ZIP extraído;
3. archivo/árbol real del repositorio destino;
4. SHA/blob/tamaño/commit verificable en GitHub;
5. prueba reproducible local/CI con salida real.

No usar el nombre de un ZIP, una lista aproximada, una memoria del chat ni una inferencia para afirmar que un archivo existe o debe existir.

## PLAN MAESTRO — LOOP/BÚCLE PARALELO
El trabajo se ejecuta por tareas independientes en paralelo cuando no existe dependencia de datos. Cada lote debe terminar sus subtareas antes de emitir la salida del lote. Después de cada lote se actualizan: tarea en curso, total de tareas, siguiente tarea, evidencia y estado.

### T01 — BASELINE GITHUB
- Leer branch, tip, árbol recursivo y documentos de control.
- Registrar commit y SHA de los documentos usados.
- Estado: COMPLETADA parcialmente mediante evidencia GitHub; se debe repetir read-back al iniciar cada lote crítico.

### T02 — XRAY DEL REPOSITORIO
- Inventariar rutas, modos, tipos, tamaños y blobs.
- Clasificar CONTROL / DOCS / OPENCLAW-CANDIDATE / ZIP / ARTEFACTO / DESCONOCIDO.
- Registrar duplicados por blob SHA y por tamaño.
- Salida: `FORENSIC-INVENTORY` + clasificación.
- Estado: inventario inicial confirmado; clasificación detallada pendiente.

### T03 — AUDITORÍA DE LOS 8 ZIP
Para cada ZIP, sin mezclarlo con otro:
- confirmar ruta, tamaño y blob SHA;
- obtener bytes mediante mecanismo que realmente entregue el ZIP;
- SHA-256 del ZIP;
- listar contenido sin modificar;
- identificar carpeta envolvente;
- extraer en workspace temporal;
- generar árbol relativo y manifiesto;
- detectar artefactos prohibidos.
Salida: `ZIP-MANIFEST`, `ZIP-XRAY-MATRIX`, `ZIP-EXTRACTION-MANIFEST`.
Gate: ningún ZIP se incorpora a la raíz antes de pasar este gate.

### T04 — COMPARACIÓN CRUZADA ZIP↔ZIP
En paralelo por pares/familias:
- comparar rutas;
- comparar hashes de archivos cuando sea posible;
- detectar subconjuntos, duplicados, solapamientos y piezas complementarias;
- no asumir que numeración 1/4/5/5.1/6/7/8/9 representa una secuencia válida.
Salida: `ZIP-CROSS-COMPARISON` y `DUPLICATE-REPORT`.

### T05 — ÁRBOL CANÓNICO OPENCLAW
- Consultar exactamente `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`.
- Registrar árbol completo, no una lista aproximada.
- Separar directorios, blobs, modos y tamaños.
Salida: `OPENCLAW-CANONICAL-TREE`.

### T06 — VERIFICACIÓN CRUZADA ARCHIVO POR ARCHIVO
Para cada candidato que se quiera colocar como OpenClaw:
- buscar ruta exacta en árbol canónico;
- comparar tipo/mode;
- comparar tamaño;
- comparar blob SHA cuando el contenido sea idéntico;
- si el blob SHA difiere, marcar MODIFIED y no asumir equivalencia;
- clasificar MATCH / MISSING / EXTRA / MODIFIED / DUPLICATE / UNKNOWN.
Para archivos demasiado grandes o cuando el API no permita una comparación directa, usar evidencia de bytes/sha256 del origen y destino, no una estimación.
Salida: `ROOT-DIFF-MATRIX`.

### T07 — MAPA DE RAÍCES MULTI-AGENTE
El repositorio NO es exclusivamente OpenClaw. La arquitectura final debe reservar un espacio limpio y explícito para múltiples raíces independientes.
Regla propuesta a validar antes de mover archivos:
```text
ROOTS/
  openclaw/
  <future-agent-02>/
  <future-agent-03>/
```
Cada raíz de agente debe conservar su árbol interno original después de eliminar únicamente la envoltura del ZIP cuando corresponda. Documentación/bitácora/pipeline permanecen fuera de las raíces de agentes.
NO mover el OpenClaw actual hasta terminar T06 y construir el manifiesto final.
Salida: `MULTI-AGENT-ROOT-LAYOUT` + decisión registrada.

### T08 — MANIFIESTO DE RAÍZ OPENCLAW
Construir un manifiesto de destino con:
- ruta fuente canónica;
- ruta ZIP;
- ruta destino `ROOTS/openclaw/...` si T07 es aprobado;
- SHA fuente;
- SHA del candidato;
- tamaño;
- acción KEEP/COPY/MERGE/EXCLUDE/REPAIR;
- razón y evidencia.
Salida: `OPENCLAW-ROOT-MANIFEST`.
Gate: no publicar sin manifiesto.

### T09 — CONSTRUCCIÓN TEMPORAL
- reconstruir `ROOTS/openclaw/` en workspace temporal;
- mantener exactamente las rutas relativas del árbol canónico;
- excluir `node_modules`, `.pnpm-store`, `dist`, `build`, `coverage`, caches, logs, credenciales y temporales;
- no regenerar código existente.
Salida: `ROOT-BUILD`.

### T10 — VERIFICACIÓN LOCAL
- conteo de archivos/directorios;
- rutas esperadas/faltantes/extras;
- tamaños;
- SHA-256;
- anchors críticos (`package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `openclaw.mjs`, etc. cuando pertenezcan al ref);
- `git diff --check` si aplica;
- pruebas mínimas reproducibles después de completar el código.
Salida: `LOCAL-VERIFY` PASS/FAIL.
Gate: FAIL bloquea publicación.

### T11 — PUBLICACIÓN GITHUB POR LOTES
Solo con `LOCAL-VERIFY=PASS`.
Publicar por familias para controlar tamaño y cursor, sin alterar contenido:
- root manifests;
- src;
- packages;
- extensions;
- resto del árbol;
- documentación específica del agente si corresponde.
Cada lote registra commit, archivos, tamaño y SHA.

### T12 — REMOTE READ-BACK
Después de cada lote:
- releer GitHub;
- verificar rutas, tamaños, blobs/sha y commit;
- comparar con manifest local;
- si falla, `PERSISTENCE_FAILURE → REPAIR`, nunca DONE.
Salida: `REMOTE-VERIFY`.

### T13 — PRUEBA OPENCLAW
Solo después de que la raíz haya pasado la verificación de persistencia:
- comprobar estructura de workspace;
- instalar dependencias solo en entorno temporal y nunca subirlas;
- ejecutar el procedimiento oficial disponible en el ref;
- registrar salida real PASS/FAIL.
Salida: `OPENCLAW-BOOT-VERIFY`.

### T14 — AUDITORÍA FORENSE XRAY FINAL
Cruce final independiente:
```text
OPENCLAW CANÓNICO
      ↕
ZIP EXTRAÍDO
      ↕
MANIFIESTO
      ↕
ROOTS/openclaw
      ↕
GITHUB READ-BACK
```
Dominios: METHOD / REQUIREMENTS / TRACEABILITY / SOURCE / ZIP / ROOT / INTEGRITY / PUBLISH / REMOTE / TESTS / DOCS / NO_UNAUTHORIZED.
Cada discrepancia genera REPAIR_REQUIRED o BLOCKED.
Salida: `FORENSIC-AUDIT`.

### T15 — AUDITORÍA MULTI-RAÍZ
Comprobar que:
- OpenClaw está aislado dentro de su raíz;
- no hay archivos de otros agentes dentro de `ROOTS/openclaw`;
- `ROOTS/` permite añadir nuevas raíces sin mezclar árboles;
- documentos de control siguen fuera de las raíces de agentes;
- no existen duplicados accidentales de la raíz OpenClaw.
Salida: `MULTI-ROOT-AUDIT`.

### T16 — CIERRE / COMPLETION RECORD
Solo DONE si T01–T15 tienen evidencia suficiente, con publicación y read-back confirmados.
Registrar: task_id, objective, sources, outputs, paths, commits, SHA, verdict, next_task.

## FORMATO OBLIGATORIO DE CADA SALIDA DEL LOOP
```text
Tarea en curso: Txx — <nombre>
Total de tareas: 16
Tareas terminadas al 100%: <lista con evidencia>
Tareas pendientes: <lista>
Siguiente tarea: <Txx + subtareas paralelas>
Confirmación de tarea terminada al 100%: SÍ/NO — <evidencia GitHub/local real>
Bloqueos/reparación: <ninguno o evidencia>
```

## REGLA DE PARALELISMO
Antes de cada salida, planificar el siguiente lote con todas las tareas independientes que puedan ejecutarse en paralelo. No esperar innecesariamente una tarea que no sea dependencia. Pero nunca publicar una salida como "100%" si alguna subtarea del lote quedó sin verificar.

## REGLA LOOP / NO-STOP
Mientras existan tareas pendientes, el agente debe continuar con el siguiente lote disponible. Si una herramienta falla:
1. registrar fallo real;
2. inspeccionar estado actual;
3. cambiar mecanismo si el mismo fallo ocurre dos veces;
4. reintentar de forma determinista;
5. no inventar resultado.
Si existe un bloqueo externo que impida continuar, marcar BLOCKED con evidencia concreta en vez de afirmar DONE.

## ESTADO DE ESTE CICLO
- Objetivo: reconstruir una raíz OpenClaw verificable dentro de una arquitectura que soporte múltiples raíces de agentes.
- Tarea en curso: T03/T04/T05/T06 en paralelo.
- Total de tareas: 16.
- Siguiente salida: matriz de verificación ZIP↔ZIP y OpenClaw canónico↔candidatos, más decisión de layout `ROOTS/`.
- Cierre: solo después de T14, T15 y T16.

## REGLA FINAL
Una afirmación del asistente nunca es evidencia. Solo se marca una tarea como 100% terminada cuando existe evidencia reproducible y persistente. El último paso obligatorio es la verificación cruzada y auditoría forense XRAY final.
