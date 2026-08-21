# BITÁCORA ACR XRAY — historial operativo reutilizable

## Objetivo
Conservar conocimiento verificable para que otro GPT/agente pueda recuperar y continuar el trabajo sin depender de memoria conversacional. GitHub es la fuente persistente de verdad. No convertir hipótesis, planes o respuestas del asistente en hechos confirmados.

## Estado confirmado
- Repo: `maxbry123-commits/Agentes-motores-Wordflow-YAIWES`
- Branch: `main`
- Canonical OpenClaw: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- `ROOTS/README.md` confirma arquitectura multi-agente y aislamiento de `ROOTS/openclaw/`.
- 8 ZIPs están identificados; ZIP 1 y ZIP 4 comparten blob SHA/tamaño y son duplicados exactos a nivel GitHub.
- La extracción binaria real de los ZIP sigue BLOQUEADA por el mecanismo actual de acceso a blobs grandes. No marcar descarga/extracción como completada.

## Método persistente
`TASK_INTAKE → SANDBOX_BUILD → LOCAL_VERIFY → READY_FOR_PUBLISH → GITHUB_PUBLISH → REMOTE_VERIFY → FORENSIC_AUDIT → DONE`.
GitHub es la verdad persistente; sandbox es temporal; HTTP 200 no basta; toda publicación requiere read-back; una afirmación LLM no es evidencia; mismo fallo ×2 obliga a cambiar mecanismo.

## Hallazgos canónico ↔ repo
1. `package.json`: MODIFIED / NO MATCH. Canonical 2026.8.1, schemaVersions state 9/agent 17; repo 2026.7.1 sin bloque observado.
2. `node-version.mjs`: MISSING en repo; canonical blob `dc7876dd0ce35116aaef535d342647ebb1ad16e7`.
3. `npm-shrinkwrap.json`: EXTRA / NON-CANONICAL; ausente en canonical, presente en repo.
4. `pnpm-workspace.yaml`: MODIFIED / NO MATCH; canonical blob `5ffb3a0e59272237670f60b5448931290d5b9a65`; repo blob `05d3a199ce86c756006b698af705ae45e2855dd3`.
5. `README.md`: MODIFIED / NO MATCH; canonical blob `c74989cee8a9c1e8648aa892175de3c9e375bafe`; repo blob `c656353ef50013d27756c1717fd2df6e2645c1db`.
6. `LICENSE`: MATCH; canonical y repo comparten blob `ebaebf7c416761a32f932ad70ebe5d1d2e214f68`.
7. `THIRD_PARTY_NOTICES.md`: MATCH; canonical y repo comparten blob `6b6721901b7590d20774ba0504d975e1be70a57a`.
8. `openclaw.mjs`: MODIFIED / NO MATCH. Canonical importa `./node-version.mjs` y recomienda Node 26; repo actual contiene implementación distinta y recomienda Node 24. Las respuestas largas están truncadas, pero las diferencias del prefijo son directamente observables.
9. `pnpm-lock.yaml`: MODIFIED / NO MATCH. Ambos lockfileVersion 9.0, pero el canonical ref tiene overrides/dependencias más recientes y el repo contiene versiones anteriores y un `patchedDependencies` distinto; lectura directa de ambos muestra diferencias materiales.
10. `Dockerfile`: MODIFIED / NO MATCH. Canonical y repo comparten la arquitectura multi-stage general, pero difieren en digests de imágenes Node/Bun, argumentos y pasos de build/runtime; lectura directa de ambos demuestra divergencia.
11. `tsconfig.json`: MODIFIED / NO MATCH. Canonical y repo tienen base TypeScript similar, pero canonical incluye un conjunto distinto de aliases y el repo contiene `ScriptHost` y rutas adicionales/anteriores; blobs no se han tratado como equivalentes.
12. `vitest.config.ts`: MODIFIED / NO MATCH. Canonical blob `0c3c22faa3313065bc69600d15aa41b422a1bc25`; repo blob `8ccea14a99e8ebe43111ef3c0301ebd9890a1469`. El repo exporta además `rootVitestProjects`, ausente en el canonical observado.
13. `AGENTS.md`: MODIFIED / NO MATCH. Ambos contienen políticas OpenClaw, pero el contenido visible difiere materialmente; no se considera MATCH sin equivalencia de blob/contenido completo.

## Arquitectura multi-raíz
`ROOTS/openclaw/` es el destino exclusivo de OpenClaw. Futuras raíces serán hermanas. No mover archivos OpenClaw existentes hasta T06/T08. Documentación, manifiestos y control permanecen fuera de las raíces.

## Archivos de control creados/actualizados
- `FORENSIC-CROSSCHECK-OPENCLAW.md` actualizado en commit `dbcbeecaaa2f69ebbd73da3386a0566e56c25f79`.
- `OPENCLAW-ROOT-MANIFEST.md` creado como borrador de evidencia en commit `f7c6e450ef158367f527512dffef7fd9469553eb`.
- `.github/workflows/acr-zip-xray.yml` creado y posteriormente reparado para extraer los 8 ZIP en jobs paralelos, validar ZIP, generar SHA-256/manifiestos y subir artefactos; último commit del workflow `39e983ffc38aded79359f2653a7323868ef6ab42`.
- `ACR-LOOP-TRIGGER.md` usado para provocar un push posterior al workflow; último commit `71e9c2f90e44172f90e7a7d6d49fb0c65ad21b3e`.

## Plan T01–T16
T01 baseline; T02 XRAY repo; T03 auditoría ZIP; T04 ZIP↔ZIP; T05 árbol canónico; T06 canónico↔candidatos; T07 multi-agent ROOTS; T08 manifiesto; T09 build temporal; T10 local verify; T11 publish; T12 remote read-back; T13 boot verify; T14 XRAY final; T15 multi-root audit; T16 completion record.

## Lote LOOP ejecutado — 5+ líneas en paralelo
- T03-A: leída la guía `ACR-RECOVERY-PATCH-ZIP.md`; confirma que el ZIP canónico del ref exacto es fuente única y que la transferencia debe conservar bytes, hash/tamaño y rutas relativas. La guía también confirma que un ZIP no debe marcarse descargado sin existir físicamente. Evidencia: SHA `ebf4d3095dbb44c90b306d22140bf5ac9408d475`.
- T04-B: revalidada la estrategia GitHub Actions como mecanismo alternativo de transferencia binaria. El workflow valida con `unzip -t`, extrae y produce hashes/listados.
- T06-C: ampliada la matriz canónico↔repo con `pnpm-lock.yaml`, `Dockerfile`, `tsconfig.json`, `vitest.config.ts` y `AGENTS.md`; todos se clasifican como MODIFIED/NO MATCH salvo los matches previamente demostrados.
- T08-D: se intentó leer `FORENSIC-ZIP/` después del trigger; todavía devuelve 404. Por tanto no se afirma que el workflow haya terminado ni que los artefactos existan.
- T10-E: los checks previstos siguen definidos: tamaño, `unzip -t`, conteo, rutas, SHA-256 por archivo y posterior comparación contra el árbol canónico.

## Resultado de este lote
- Guía ZIP: CONFIRMADA por lectura directa.
- Cinco comparaciones canónico↔repo adicionales: DOCUMENTADAS; no se inventan matches.
- Workflow de extracción: CONFIGURADO y leído de vuelta; ejecución real todavía NO CONFIRMADA.
- `FORENSIC-ZIP/`: no visible todavía en GitHub.
- No se ha movido ni sobrescrito ningún archivo de OpenClaw a `ROOTS/openclaw/`.

## Próximo lote — 5 tareas paralelas
1. T03-A: resolver definitivamente la observabilidad/ejecución de GitHub Actions y recuperar evidencia de artifacts si el workflow está ejecutándose.
2. T04-B: ampliar el manifiesto ZIP con todos los nombres, tamaños y blobs ya conocidos y separar duplicado exacto de candidatos distintos.
3. T06-C: verificar cinco rutas canónicas adicionales seleccionadas del árbol oficial, incluyendo `node-version.mjs` y cuatro archivos de configuración/raíz.
4. T08-D: actualizar `OPENCLAW-ROOT-MANIFEST.md` con las nuevas discrepancias y mantener todas las entradas como `PENDING` hasta disponer de extracción.
5. T10-E: diseñar el comparador final de ruta+modo+SHA que usará los manifests de los ZIP contra el ref canónico antes de cualquier publicación en `ROOTS/openclaw/`.

## Formato obligatorio
Tarea en curso / Total de tareas / Tareas terminadas al 100% / Tareas pendientes / Siguiente tarea con 3–5 subtareas paralelas / Confirmación 100% / Bloqueos-reparación.

## Regla final
No DONE hasta completar T01–T15 con evidencia, publicación, read-back, verificación cruzada y auditoría forense XRAY. Si una subtarea está bloqueada, continuar tareas independientes y registrar BLOCKED; nunca inventar DONE.
