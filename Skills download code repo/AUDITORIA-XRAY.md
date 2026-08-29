# Auditoría X-Ray — plan + lista + skill extract

Workflow: `.github/workflows/descarga-extraccion-inventario.yml`
Inventario: `Skills download code repo/INVENTARIO.md`
Plan: `Skills download code repo/README.md`
Skill extract origen: `agentes/Wordflow Code/skills/code Yaml sobre como se extrae los archivos del skills.yaml`

## Lista — 37/37

TSV del Paso 1 = tabla INVENTARIO.md. Mismos 37 nombres. Mismas 37 URLs. 0 vacíos. 0 duplicados. 0 URLs fuera del input.

## Plan — 5/5

1. Destino `Agentes-motores-Wordflow-YAIWES` rama `main`. Raíz = nombre exacto. ZIP entero dentro de esa raíz. Nada suelto. No mezcla.
2. Fuente = inventario vigente. Los 37. Sin filtro. Sin borrar.
3. Action solo esos 37. No es research-download-chain. No hay repos extra.
4. Extract usa el núcleo del skill: `ZipFile`, `testzip`, `BadZipFile`, path `..` / absoluto, `duplicate member`, `extraction escape`, `copyfileobj(..., 1024 * 1024)`, `zero files extracted`, `PASS EXTRACT`.
5. Solo dos steps nombrados: `Paso 1 - Descargar ZIP` y `Paso 2 - Extraer cada ZIP en su raíz`.

## Skill — núcleo extract PASS

Copiado del step `Extract all ZIP parts safely` + validación CRC del skill.
No se copió el lock 20 repos / 61 ZIP / `xray/extracted` / TAR / artifact: eso es la action anterior y viola el plan (puntos 3 y 5).

## Resultado

PASS plan 5/5. PASS lista 37/37. PASS núcleo extract del skill.
No se disparó Run.
