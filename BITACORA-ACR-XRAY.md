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
- La extracción está CONFIRMADA para el run: cada job ejecutó `unzip -t`, extrajo preservando rutas relativas y generó manifests/SHA-256.

## Método persistente
`TASK_INTAKE → SANDBOX_BUILD → LOCAL_VERIFY → READY_FOR_PUBLISH → GITHUB_PUBLISH → REMOTE_VERIFY → FORENSIC_AUDIT → DONE`.
GitHub es la verdad persistente; sandbox es temporal; HTTP 200 no basta; toda publicación requiere read-back; una afirmación LLM no es evidencia; mismo fallo ×2 obliga a cambiar mecanismo.

## Hallazgos canónico ↔ repo
1. `package.json`: MODIFIED / NO MATCH. Canonical 2026.8.1; repo 2026.7.1.
2. `node-version.mjs`: MISSING en repo; canonical blob `dc7876dd0ce35116aaef535d342647ebb1ad16e7`.
3. `npm-shrinkwrap.json`: EXTRA / NON-CANONICAL; ausente en canonical, presente en repo.
4. `pnpm-workspace.yaml`: MODIFIED / NO MATCH.
5. `README.md`: MODIFIED / NO MATCH.
6. `LICENSE`: MATCH; comparten blob `ebaebf7c416761a32f932ad70ebe5d1d2e214f68`.
7. `THIRD_PARTY_NOTICES.md`: MATCH; comparten blob `6b6721901b7590d20774ba0504d975e1be70a57a`.
8. `openclaw.mjs`: MODIFIED / NO MATCH; el canonical importa `./node-version.mjs` y recomienda Node 26; repo actual difiere.
9. `pnpm-lock.yaml`: MODIFIED / NO MATCH.
10. `Dockerfile`: MODIFIED / NO MATCH.
11. `tsconfig.json`: MODIFIED / NO MATCH.
12. `vitest.config.ts`: MODIFIED / NO MATCH.
13. `AGENTS.md`: MODIFIED / NO MATCH.

## Arquitectura multi-raíz
`ROOTS/openclaw/` es el destino exclusivo de OpenClaw. Futuras raíces serán hermanas. Documentación, manifiestos y control permanecen fuera de las raíces.

## Archivos de control
- `FORENSIC-CROSSCHECK-OPENCLAW.md` actualizado previamente.
- `OPENCLAW-ROOT-MANIFEST.md` existe como borrador de evidencia.
- `.github/workflows/acr-zip-xray.yml` extrae y audita los 8 ZIP.
- `FORENSIC-ZIP/RUN-32529275113.md` confirma artifacts de los 8 ZIP.
- `FORENSIC-ZIP/ZIP-EXTRACTION-VERIFIED-2026-08-21.md` contiene evidencia de extracción.
- `.github/workflows/assemble-openclaw-root.yml` creado en commit `92b81a6bfc4a8628c932c6fd0a6f165969a353e3`. Su objetivo es: descargar los 8 artifacts, comparar cada archivo extraído byte-a-byte contra el ref canónico, clonar el ref oficial y construir `ROOTS/openclaw/` completo desde el canonical, excluyendo dependencias/artefactos generados.

## Auditoría real de los 8 artifacts
Los 8 artifacts fueron recuperados mediante GitHub Actions y están identificados: zip1 `9463282499`, zip4 `9463282194`, zip5 `9463285201`, zip5.1 `9463281605`, zip6 `9463282580`, zip7 `9463282058`, zip8 `9463283012`, zip9 `9463282609`.

Inspección local reproducible de los 8 artifacts descargados:
- zip1: 1355 archivos bajo `extracted/`; ZIP válido (`testzip=None`).
- zip4: 1355 archivos bajo `extracted/`; ZIP válido; rutas y SHA de contenido coinciden exactamente con zip1.
- zip5: 7786 archivos bajo `extracted/`; ZIP válido.
- zip5.1: 754 archivos bajo `extracted/`; ZIP válido.
- zip6: 764 archivos bajo `extracted/`; ZIP válido.
- zip7: 953 archivos bajo `extracted/`; ZIP válido.
- zip8: 1271 archivos bajo `extracted/`; ZIP válido.
- zip9: 2579 archivos bajo `extracted/`; ZIP válido.
- Unión de rutas relativas de los ocho: 14698 rutas únicas.
- ZIP1 y ZIP4 son duplicados de contenido, no solo de nombre/tamaño: 1355 rutas y hashes de archivo coinciden.
- Solapamientos adicionales: ZIP1/ZIP4 ↔ ZIP6 comparten 10 rutas; ZIP5.1 ↔ ZIP6 comparten 754 rutas. No se observaron conflictos de contenido en esos solapamientos.
- Distribución top-level observada: ZIP1/4=`apps` más `config`/`deploy`; ZIP5=`extensions`,`packages`,`qa`,`patches`,`git-hooks`; ZIP5.1=`docs`,`examples`; ZIP6=`docs`,`config`,`examples`,`deploy`; ZIP7=`scripts`,`skills`,`security`; ZIP8=`test`,`ui`; ZIP9=`agents`,`auto-reply`,`acp`,`audit`,`bindings`.
- Esto demuestra que los ZIP son piezas complementarias del árbol, no ocho copias completas. No se debe asumir que uno solo es la raíz completa.

## Decisión de reconstrucción
La raíz final NO se construirá pegando ciegamente las piezas ZIP ni reutilizando la raíz modificada que ya existe en el repo. El ref canónico oficial es la autoridad para completar la raíz.

Proceso obligatorio:
1. Extraer los 8 ZIP.
2. Quitar únicamente la envoltura técnica `extracted/`.
3. Comparar cada ruta/archivo ZIP contra `openclaw/openclaw@a4178c7...` por contenido SHA-256.
4. Rechazar cualquier ZIP que tenga archivo ausente o diferente respecto al canonical.
5. Construir `ROOTS/openclaw/` desde el ref canónico completo, usando los ZIP como evidencia cruzada de las piezas recibidas.
6. Excluir `node_modules/`, `.pnpm-store/`, `dist/`, `build/`, `coverage/`, `.cache/`, `.tmp/` y logs generados.
7. Generar manifest completo con ruta, SHA-256, tamaño y modo.
8. Hacer read-back de GitHub y repetir XRAY.

## Plan T01–T16
T01 baseline; T02 XRAY repo; T03 auditoría ZIP; T04 ZIP↔ZIP; T05 árbol canónico; T06 canónico↔candidatos; T07 multi-agent ROOTS; T08 manifiesto; T09 build temporal; T10 local verify; T11 publish; T12 remote read-back; T13 boot verify; T14 XRAY final; T15 multi-root audit; T16 completion record.

## Estado LOOP actual
- T03: 100% en extracción/recuperación de los 8 artifacts; canonicidad aún pendiente.
- T04: 100% en inventario de rutas/solapamientos de los 8 artifacts; conflictos pendientes de comparación canónica.
- T05: canonical ref confirmado.
- T06: parcial; comparación manual inicial del repo ya documentada; comparación automática completa pendiente.
- T07: 100% estructura `ROOTS/` definida.
- T08: parcial; manifiesto completo pendiente de ejecución del ensamblador.
- T09/T10/T11/T12/T13/T14/T15/T16: pendientes.

## Próximo lote — 5 tareas paralelas
1. T03/T06-A: ejecutar el nuevo workflow de ensamblaje y verificar el resultado real del run; no declarar éxito hasta leer `ROOTS/openclaw/package.json` y `.acr-canonical-ref` desde GitHub.
2. T04-B: usar la extracción local completa para verificar que ZIP1=ZIP4 y cuantificar todos los overlaps de los 8 ZIP.
3. T06-C: si el workflow falla, leer jobs/logs, corregir solo la causa demostrada y re-ejecutar; no cambiar el objetivo.
4. T08-D: leer de vuelta `FORENSIC-ZIP/FINAL-CROSSCHECK.md` y `OPENCLAW-ROOT-MANIFEST.md` cuando aparezcan; clasificar cada resultado.
5. T10/T12/T14/T15-E: después de un build PASS, verificar exclusiones, árbol, hashes, aislamiento `ROOTS/openclaw/` y auditoría XRAY final.

## Formato obligatorio
Tarea en curso / Total de tareas / Tareas terminadas al 100% / Tareas pendientes / Siguiente tarea con 3–5 subtareas paralelas / Confirmación 100% / Bloqueos-reparación.

## Regla final
No DONE hasta completar T01–T15 con evidencia, publicación, read-back, verificación cruzada y auditoría forense XRAY. Si una subtarea está bloqueada, continuar tareas independientes y registrar BLOCKED; nunca inventar DONE.
