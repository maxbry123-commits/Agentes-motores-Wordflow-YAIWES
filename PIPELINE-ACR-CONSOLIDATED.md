# PIPELINE ACR — CONSOLIDADO PARA FUTUROS AGENTES

## 1. Objetivo
Mapa operativo para GPT, Grok u otro agente. Distingue ejecución real de planificación y conserva el método ZIP→raíz, verificación y protección multi-agente.

## 2. Arquitectura
```text
repo/
├── ROOTS/
│   ├── openclaw/          # raíz exclusiva y protegida por proceso
│   └── <otros-agentes>/   # raíces hermanas
├── .github/workflows/     # control/pipeline fuera de las raíces
├── FORENSIC-ZIP/
├── BITACORA-ACR-XRAY.md
├── OPENCLAW-ROOT-MANIFEST.md
└── FORENSIC-CROSSCHECK-OPENCLAW.md
```

## 3. DSL / DAG maestro
```text
TASK_INTAKE
 -> SNAPSHOT
 -> INVENTORY
 -> ZIP_XRAY
 -> CANONICAL_COMPARE
 -> BUILD_SANDBOX
 -> LOCAL_VERIFY
 -> READY_FOR_PUBLISH
 -> PUBLISH
 -> REMOTE_READBACK
 -> FORENSIC_XRAY
 -> DONE
```

**Regla:** ningún nodo se marca PASS sin evidencia. Si un nodo falla, se conserva evidencia, se corrige la causa demostrada y se repite ese nodo.

## 4. ZIP → raíz: método exacto
**Extraer NO vacía el ZIP.** El ZIP sigue conteniendo sus miembros después de `unzip`. Eliminar el ZIP es una operación independiente que solo ocurre después de PASS.

```text
ZIP_SOURCE
 -> INVENTORY
 -> HASH_SOURCE
 -> ZIP_INTEGRITY
 -> EXTRACT_TO_STAGING
 -> MANIFEST_EXTRACTED
 -> CLASSIFY_AGENT
 -> MAP_RELATIVE_PATHS
 -> COPY/RSYNC_TO_ROOT
 -> HASH_DEST
 -> CROSSCHECK_ZIP_VS_DEST
 -> CROSSCHECK_DEST_VS_OFFICIAL
 -> VERIFY_COUNTS
 -> VERIFY_MISSING
 -> VERIFY_UNEXPECTED
 -> CLEAN_TEMPORARIES
 -> POST_AUDIT
 -> COMMIT
```

### Comandos de referencia
```bash
# inventario sin modificar el ZIP
unzip -Z1 agente.zip > zip-manifest.txt

# integridad
unzip -t agente.zip

# hash del contenedor
sha256sum agente.zip

# staging aislado
rm -rf .staging/agente
mkdir -p .staging/agente
unzip -q agente.zip -d .staging/agente

# inventario extraído
find .staging/agente -type f -print | sort > extracted-manifest.txt

# comparar cantidad de entradas de archivos
wc -l zip-manifest.txt extracted-manifest.txt

# preservar estructura al publicar
rsync -a --exclude='.git/' .staging/agente/ ROOTS/<agente>/

# hashes de destino
find ROOTS/<agente> -type f -print0 | sort -z | xargs -0 sha256sum > destination-sha256.txt

# solo después de verificar PASS y si el ZIP es temporal
rm agente.zip
```

**Nunca:** extraer directamente sobre una raíz protegida sin staging; usar `rsync --delete` sobre una raíz protegida; borrar por nombre sin comparar hash/ruta.

## 5. Despliegue en lotes
```text
ZIP
 -> INVENTARIO_GLOBAL
 -> LOTE_i
 -> STAGING_i
 -> MANIFEST_i
 -> SHA_i
 -> VALIDATE_i
 -> MERGE_LÓGICO
 -> HASH_GLOBAL
 -> ROOTS/<agente>
 -> AUDITORÍA
```
Cada lote requiere `manifest + count + hash + destino + estado`. Un ZIP con piezas complementarias no debe tratarse como una raíz completa.

## 6. Verificación cruzada — 4 pasadas
**A — estructura:** árbol, rutas, cantidad.

**B — contenido:** SHA-256 de críticos o todos los blobs cuando sea viable.

**C — upstream:** comparación contra repositorio oficial y commit canónico.

**D — post-publicación:** read-back desde `main`, clasificar `MISSING / EXTRA / MODIFIED`, y comparar snapshot pre/post.

## 7. Protección de una raíz de agente
Git no permite convertir una subcarpeta en una zona físicamente imborrable. La protección recomendada es por proceso:

```text
ROOTS/<agente>
 -> CODEOWNERS
 -> branch protection / PR requerido
 -> CI guard que rechaza deletes/modificaciones no autorizadas
 -> manifest + SHA
 -> snapshot de commit conocido
 -> auditoría pre/post
```

Para una protección fuerte, el workflow de CI debe detectar cambios bajo `ROOTS/<agente>/**` y fallar si no existe una señal/autorización explícita. Esto protege la raíz mediante GitHub; no debe describirse como un atributo de solo lectura.

## 8. OpenClaw
Canonical: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`.
Destino exclusivo: `ROOTS/openclaw/`.
Lockfile canónico registrado: `cefd1fdf77f5c170ffacfad4b75e03c4c33345cf`.

El proceso no debe borrar ni modificar `ROOTS/openclaw/**` durante limpiezas generales del repositorio sin snapshot + comparación + autorización específica.

## 9. Laboratorio CPU reutilizable
`.github/workflows/cpu-benchmark.yml` es independiente de las raíces. Una ejecución encadenada y un artifact contienen las 10 pruebas: CPU identification, Sysbench, OpenSSL SHA-256, 7-Zip, Integer/C, Floating point, stress-ng, SHA-256 throughput, JSON y scaling 1/2/4.

La existencia del YAML no es un benchmark ejecutado. Solo `run/job/artifact` real permite PASS.

## 10. Checklist de cierre
```text
[ ] snapshot inicial
[ ] inventario completo
[ ] ZIP integrity
[ ] manifests
[ ] ZIP↔ZIP
[ ] ZIP↔canonical
[ ] raíz construida
[ ] hashes
[ ] exclusiones
[ ] protección ROOTS/<agente>
[ ] publish
[ ] read-back
[ ] build/boot si aplica
[ ] benchmark real si aplica
[ ] artifact inspeccionado
[ ] snapshot pre/post
[ ] XRAY final
[ ] bitácora actualizada
[ ] DONE
```

## 11. Regla de continuidad
Leer primero `BITACORA-ACR-XRAY.md`, después este documento. Si el contexto conversacional se pierde, estos documentos + GitHub son la fuente de recuperación. Nunca convertir una hipótesis, plan o respuesta del asistente en evidencia.
