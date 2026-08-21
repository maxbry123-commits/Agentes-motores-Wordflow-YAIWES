# BITÁCORA ACR XRAY — historial operativo reutilizable

## Objetivo
Conservar conocimiento verificable para que otro GPT/agente pueda recuperar y continuar el trabajo sin depender de memoria conversacional. GitHub es la fuente persistente de verdad. No convertir hipótesis, planes o respuestas del asistente en hechos confirmados.

## Estado confirmado
- Repo: `maxbry123-commits/Agentes-motores-Wordflow-YAIWES`
- Branch: `main`
- Canonical OpenClaw: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- `ROOTS/README.md` confirma arquitectura multi-agente y aislamiento de `ROOTS/openclaw/`.
- 8 ZIPs están identificados; ZIP 1 y ZIP 4 comparten blob SHA/tamaño y son duplicados exactos a nivel GitHub.
- La barrera inicial de acceso directo a blobs grandes fue superada mediante GitHub Actions: el run `32529275113` produjo 8 artifacts de extracción verificable.
- La extracción ya está CONFIRMADA para el run: cada job ejecutó `unzip -t`, extrajo preservando rutas relativas y generó manifests/SHA-256. No confundir el ZIP externo del artifact con el archivo fuente.

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
- `.github/workflows/acr-zip-xray.yml` creado y reparado para extraer los 8 ZIP en jobs paralelos, validar ZIP, generar SHA-256/manifiestos y subir artifacts.
- `FORENSIC-ZIP/RUN-32529275113.md` confirma artifacts de los 8 ZIP.
- `FORENSIC-ZIP/ZIP-EXTRACTION-VERIFIED-2026-08-21.md` creado en commit `a8151dd42cac64feaf7ddc848f8e046fb12f9bca` con evidencia de extracción, conteos, SHA y observaciones de rutas.

## Plan T01–T16
T01 baseline; T02 XRAY repo; T03 auditoría ZIP; T04 ZIP↔ZIP; T05 árbol canónico; T06 canónico↔candidatos; T07 multi-agent ROOTS; T08 manifiesto; T09 build temporal; T10 local verify; T11 publish; T12 remote read-back; T13 boot verify; T14 XRAY final; T15 multi-root audit; T16 completion record.

## Lote LOOP ejecutado — 5 líneas en paralelo
- T03-A: observabilidad resuelta. GitHub Actions run `32529275113` produjo artifacts de extracción para los 8 ZIP. Artifacts no expirados y recuperables; IDs: zip1 `9463282499`, zip4 `9463282194`, zip5 `9463285201`, zip5.1 `9463281605`, zip6 `9463282580`, zip7 `9463282058`, zip8 `9463283012`, zip9 `9463282609`.
- T04-B: verificación local de artifacts descargados para zip1, zip6, zip7, zip8 y zip9. `unzip.testzip()` devuelve `None` en los cinco; manifests fuente reportan respectivamente 1387, 801, 953, 1334 y 2579 archivos.
- T06-C: los artifacts demuestran contenido real pero NO canonicidad. No se clasifica ningún ZIP como fuente oficial hasta comparar rutas/modos/SHA contra `openclaw/openclaw@a4178c7...`.
- T08-D: se creó `FORENSIC-ZIP/ZIP-EXTRACTION-VERIFIED-2026-08-21.md`; el wrapper `extracted/` pertenece al workspace de extracción y no debe convertirse automáticamente en `ROOTS/openclaw/extracted/`.
- T10-E: comparación cruzada inicial entre los cinco artifacts descargados: 6912 rutas físicas distintas; zip1↔zip6 comparte 10 rutas de configuración/deploy; no se observaron overlaps entre los demás pares muestreados. Esta observación es solo de los cinco artifacts descargados, no del conjunto completo.

## Resultado de este lote
- Ejecución GitHub Actions: CONFIRMADA.
- Ocho artifacts: CONFIRMADOS y no expirados en run `32529275113`.
- Extracción verificable: CONFIRMADA para los artifacts; cinco fueron inspeccionados localmente en este lote.
- Conteos de manifiestos: CONFIRMADOS para los ocho por `RUN-32529275113.md`.
- Canonicalidad OpenClaw: NO CONFIRMADA para ningún ZIP todavía.
- `ROOTS/openclaw/`: permanece sin reconstruir; no se ha movido ni sobrescrito la raíz existente.

## Próximo lote — 5 tareas paralelas
1. T03-A: descargar e inspeccionar artifacts zip5 y zip5.1; completar los ocho ZIP con checks locales y SHA.
2. T04-B: construir comparación ZIP↔ZIP de las ocho fuentes usando rutas relativas y hashes de archivo, separando duplicados, complementos y solapamientos.
3. T06-C: comparar las rutas extraídas contra el árbol canónico oficial, empezando por archivos raíz y después por directorios `apps/`, `config/`, `deploy/`, `packages/`, `src/`, `test/`, `extensions/` cuando existan.
4. T08-D: convertir `OPENCLAW-ROOT-MANIFEST.md` de borrador a matriz de evidencia con estados `MATCH/MISSING/EXTRA/MODIFIED/PENDING`, sin publicar todavía.
5. T10-E: validar que el stripping de la envoltura `extracted/` conserva exactamente las rutas relativas y que ningún artefacto (`node_modules`, build, dist, coverage, caches) entre en la raíz final salvo evidencia explícita del ref.

## Formato obligatorio
Tarea en curso / Total de tareas / Tareas terminadas al 100% / Tareas pendientes / Siguiente tarea con 3–5 subtareas paralelas / Confirmación 100% / Bloqueos-reparación.

## Regla final
No DONE hasta completar T01–T15 con evidencia, publicación, read-back, verificación cruzada y auditoría forense XRAY. Si una subtarea está bloqueada, continuar tareas independientes y registrar BLOCKED; nunca inventar DONE.
