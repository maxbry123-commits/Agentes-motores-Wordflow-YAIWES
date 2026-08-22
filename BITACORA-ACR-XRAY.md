# BITÁCORA ACR — AUDITORÍA FORENSE X-RAY

## 0. Regla fundamental
Esta bitácora es la memoria operativa del pipeline. Nunca se afirma que una extracción, ejecución o verificación ocurrió si no existe evidencia. Estados: `PLANNED`, `RUNNING`, `PASS`, `FAIL`, `BLOCKED`.

## 1. Método ZIP → ROOTS/<agente>
**Extraer NO vacía el ZIP.** Una extracción normal deja intacto el ZIP original. El ZIP solo se elimina después de verificar que todos sus archivos requeridos fueron desplegados y que ya no es necesario conservarlo.

### DAG / DSL de trabajo
```text
ZIP_SOURCE
 -> INVENTORY
 -> HASH_SOURCE
 -> EXTRACT_TEMP
 -> MANIFEST_EXTRACTED
 -> CLASSIFY_AGENT
 -> MAP_PATHS
 -> COPY_TO_ROOT
 -> HASH_DEST
 -> CROSSCHECK_SOURCE_VS_DEST
 -> CROSSCHECK_VS_OFFICIAL
 -> VERIFY_COUNTS
 -> VERIFY_NO_MISSING
 -> VERIFY_NO_UNEXPECTED
 -> CLEAN_TEMP_DUPLICATES
 -> POST_AUDIT
 -> COMMIT
```

### Comandos de referencia
Son comandos reproducibles de guía; solo se registran como ejecutados si existe evidencia del runner.

```bash
# Inventario
unzip -Z1 agente.zip > zip-manifest.txt
# Integridad
unzip -t agente.zip
# Hash del ZIP
sha256sum agente.zip
# Staging seguro
rm -rf .staging/agente
mkdir -p .staging/agente
unzip -q agente.zip -d .staging/agente
# Inventario extraído
find .staging/agente -type f -print | sort > extracted-manifest.txt
# Conteo
wc -l zip-manifest.txt extracted-manifest.txt
# Publicación preservando rutas
rsync -a --exclude='.git/' .staging/agente/ ROOTS/<agente>/
# Hash de destino
find ROOTS/<agente> -type f -print0 | sort -z | xargs -0 sha256sum > destination-sha256.txt
# SOLO después de PASS
rm agente.zip
```

**Regla:** nunca usar `rm`, `git rm` o `rsync --delete` contra `ROOTS/<agente>/` antes de snapshot + manifest + comparación.

## 2. Protección de raíces de agentes
Git no ofrece una subcarpeta físicamente imborrable. La protección correcta es por capas: `CODEOWNERS`, branch protection/PR requerido, workflow de auditoría, manifest+SHA, snapshot de commit y un guard de CI que falle ante eliminación/modificación no autorizada.

```text
ROOTS/<agente>
 -> CODEOWNERS
 -> PR / branch protection
 -> CI guard
 -> manifest + SHA
 -> snapshot conocido
 -> auditoría pre/post
```

Esto protege la raíz mediante el proceso de GitHub; no debe confundirse con un atributo local de solo lectura.

## 3. Despliegue por lotes
```text
ZIP -> INVENTARIO_GLOBAL -> LOTES -> STAGING -> HASH_POR_LOTE
    -> MERGE_LÓGICO -> HASH_GLOBAL -> ROOTS/<agente> -> AUDITORÍA
```
Cada lote requiere `manifest + count + hash + ruta destino + estado`.

## 4. Verificación cruzada en 4 pasadas
1. Estructura: rutas/carpetas/archivos.
2. Contenido: SHA-256.
3. Origen oficial: upstream/commit canónico.
4. Post-publicación: read-back desde `main` y clasificación `MISSING/EXTRA/MODIFIED`.

## 5. OpenClaw — hechos registrados
Canonical OpenClaw: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`.
`ROOTS/openclaw/` es la raíz exclusiva del agente.
El lockfile canónico se registró con SHA `cefd1fdf77f5c170ffacfad4b75e03c4c33345cf`. `pnpm-lock.yaml.zip` y `pnpm-lock.yaml.txt` fueron temporales/duplicados tratados después de verificación. El lockfile global no debe eliminarse por nombre: se distingue por ruta/hash.

## 6. Arquitectura multi-raíz
```text
ROOTS/
  openclaw/
  <agente-2>/
  <agente-3>/
```
Pipeline, bitácora y manifests permanecen fuera de las raíces.

## 7. Auditoría ZIP conocida
Se recuperaron 8 artifacts de ZIP mediante GitHub Actions. La extracción confirmada preservó rutas relativas y produjo manifests/SHA-256. Unión observada: 14.698 rutas únicas. ZIP1 y ZIP4 son duplicados exactos; los demás son piezas complementarias con overlaps documentados. La raíz final no debe construirse pegando ciegamente piezas: el ref canónico es autoridad y los ZIP sirven como evidencia cruzada.

## 8. Pipeline CPU
Workflow independiente `.github/workflows/cpu-benchmark.yml`. UNA ejecución, UNA cadena, UN artifact. Diez pruebas: CPU identification; Sysbench; OpenSSL SHA-256; 7-Zip; Integer/C; Floating point; stress-ng; SHA-256 throughput; JSON; scaling 1/2/4.

La existencia del workflow NO prueba una ejecución. Solo `run/job/artifact` real permite `PASS`.

## 9. Regla de continuidad GPT/Grok
Leer esta bitácora y `PIPELINE-ACR-CONSOLIDATED.md`; tomar snapshot; trabajar en staging; registrar gap; corregir; hash; read-back; actualizar bitácora.

## 10. Estado
OpenClaw: raíz separada y debe tratarse como zona protegida.
ZIP: extracción deja el ZIP intacto; eliminar es operación posterior y condicionada a PASS.
Benchmark CPU: workflow preparado; ejecución física pendiente hasta evidencia real.
Auditoría completa: pendiente mientras existan tareas T09–T16 sin evidencia.

## 11. Regla anti-alucinación
Si no existe evidencia de GitHub (commit, archivo, run, job, artifact o hash), registrar `PENDIENTE`, nunca `DONE`.
