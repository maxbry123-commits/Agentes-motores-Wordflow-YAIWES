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

## Arquitectura multi-raíz
`ROOTS/openclaw/` es el destino exclusivo de OpenClaw. Futuras raíces serán hermanas. No mover archivos OpenClaw existentes hasta T06/T08. Documentación, manifiestos y control permanecen fuera de las raíces.

## Archivos de control creados/actualizados
- `FORENSIC-CROSSCHECK-OPENCLAW.md` actualizado en commit `dbcbeecaaa2f69ebbd73da3386a0566e56c25f79`.
- `OPENCLAW-ROOT-MANIFEST.md` creado como borrador de evidencia en commit `f7c6e450ef158367f527512dffef7fd9469553eb`.

## Plan T01–T16
T01 baseline; T02 XRAY repo; T03 auditoría ZIP; T04 ZIP↔ZIP; T05 árbol canónico; T06 canónico↔candidatos; T07 multi-agent ROOTS; T08 manifiesto; T09 build temporal; T10 local verify; T11 publish; T12 remote read-back; T13 boot verify; T14 XRAY final; T15 multi-root audit; T16 completion record.

## Lote ejecutado en este LOOP
- T03-A: revalidado estado de adquisición; sigue bloqueado, sin falsa extracción.
- T04-B: revalidado inventario de 8 ZIP y duplicado ZIP1=ZIP4.
- T06-C: ampliada matriz con `LICENSE`, `THIRD_PARTY_NOTICES.md` y `openclaw.mjs`.
- T07-D: releído `ROOTS/README.md`; aislamiento confirmado.
- T08-E: creado `OPENCLAW-ROOT-MANIFEST.md` con esquema y entradas solo verificadas.

## Próximo lote — 5 tareas paralelas
1. T03-A: probar mecanismo reproducible alternativo para obtener bytes ZIP reales.
2. T04-B: completar tabla ZIP con todos los blobs/tamaños y buscar duplicados restantes.
3. T06-C: verificar 3–5 archivos/directorios raíz adicionales mediante consultas directas no truncadas.
4. T08-D: ampliar `OPENCLAW-ROOT-MANIFEST.md` únicamente con evidencia nueva.
5. T10-E: diseñar checks locales de conteo/rutas/SHA sin construir todavía la raíz final.

## Formato obligatorio
Tarea en curso / Total de tareas / Tareas terminadas al 100% / Tareas pendientes / Siguiente tarea con 3–5 subtareas paralelas / Confirmación 100% / Bloqueos-reparación.

## Regla final
No DONE hasta completar T01–T15 con evidencia, publicación, read-back, verificación cruzada y auditoría forense XRAY. Si una subtarea está bloqueada, continuar tareas independientes y registrar BLOCKED; nunca inventar DONE.
