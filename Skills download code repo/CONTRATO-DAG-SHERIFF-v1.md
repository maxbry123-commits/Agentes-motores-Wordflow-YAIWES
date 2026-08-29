# CONTRATO DAG SHERIFF v1
# Fail-closed. Un nodo FAIL bloquea el siguiente. Prohibido Run hasta revisión del Director.

fuente_gana: input_block > blob_sha > este_dag > chat
blob_packer: https://github.com/maxbry123-commits/agentes/blob/main/skills/research-download-chain/scripts/research_download_chain.py
blob_yaml: https://github.com/maxbry123-commits/agentes/blob/main/skills/research-download-chain/assets/FORENSIC-PASS-research-download-chain-final.yml
dest: Agentes-motores-Wordflow-YAIWES / main
run_autorizado: NO

## INPUT BLOCK (literal)

- I01: Si algo bajó en LFS, buscarlo y eliminarlo con un GitHub Action.
- I02: Workflow_dispatch NUEVO con lo que falta (83 = 37–119) para Paso 1 y Paso 2 del plan.
- I03: Copia fiel exacta del code fuente del skills. No reescribir. Solo editar la lista a descargar.
- I04: Plan: INVENTARIO → DOWNLOAD ZIP → EXTRACT → raíz individual por repo → main. Sin tercer paso.
- I05: Solo montar el GitHub Action. NO Run hasta que el Director revise si se cumplió el contrato.

## DSL DAG

```
N0_LOCK → N1_BLOB → N2_LFS_ACTION → N3_PACKER_LISTA → N4_YAML_SKILL → N5_SHERIFF → N6_REVIEW
                                                                              ↓ FAIL
                                                                         STOP (no Run)
N6_REVIEW --Director INICIA--> N7_RUN → N8_EVIDENCIA
```

## Nodos

### N0_LOCK
- in: este archivo + INPUT BLOCK
- out: orden citada I01..I05
- sheriff: faltó citar un Ixx → FAIL → STOP

### N1_BLOB
- in: blob_packer SHA + blob_yaml SHA
- out: archivos leídos, no resumidos
- sheriff: no se abrió el blob → FAIL → STOP

### N2_LFS_ACTION
- in: I01
- out: job/workflow que busca filter=lfs y punteros git-lfs y los borra
- sheriff: no existe Action de strip LFS → FAIL → STOP

### N3_PACKER_LISTA
- in: I03 + packer blob + lista 37–119
- out: scripts/research_download_chain.py con funciones = blob; REPOS solo gap
- sheriff:
  - falta clone --depth 1 --no-tags → FAIL
  - falta zip -q -r -9 -y → FAIL
  - falta zipsplit 12MB / MAX 17MB → FAIL
  - falta commit/push 90MB → FAIL
  - REPOS incluye 01–36 → FAIL
  - funciones reescritas ≠ blob → FAIL

### N4_YAML_SKILL
- in: I02 + I03 + I04 + blob_yaml
- out: UN workflow_dispatch nuevo
- permitido editar vs blob_yaml:
  - name
  - quitar cron y push (I05 = solo dispatch)
  - REPOS ya vive en el packer
  - añadir Paso 2 extract (I04; el blob_yaml solo tiene Paso 1)
  - env GIT_LFS_SKIP_SMUDGE (I01, no es rewrite del packer)
- prohibido: tercer job de negocio, otro downloader, audit 20/20 del ejemplo
- sheriff:
  - no es workflow_dispatch → FAIL
  - no llama python3 scripts/research_download_chain.py 'Download code/archivos' → FAIL
  - no llama extract a raíces → FAIL

### N5_SHERIFF
- in: salidas N2 N3 N4
- out: PASS_MONTAJE | FAIL
- regla: 1 FAIL de N2–N4 = FAIL global
- bloquea N7_RUN

### N6_REVIEW
- in: PASS_MONTAJE + enlaces
- out: espera Director
- arranque: INICIA | RUN | IMPUTA EL CONTRATO

### N7_RUN
- in: palabra de arranque
- sheriff: N5 != PASS_MONTAJE → no disparar

### N8_EVIDENCIA
- PASS_CIERRE solo si: run success AND COMPLETE>=119 AND raíces>=119 AND 0 punteros LFS

## Estado actual

- N2: strip-lfs existe (CUMPLE_JOB)
- N3: packer skill + REPOS 37-119 (CUMPLE_LISTA)
- N4: YAML ≠ blob_yaml → GAP I03
- N5: FAIL
- N7: BLOQUEADO (I05). Este turno = 0 Run
- N8: 40/119 ZIP; 0 raíces

veredicto_montaje: NO CUMPLE I03 (yaml ≠ blob)
accion_este_turno: solo contrato. 0 Run.
