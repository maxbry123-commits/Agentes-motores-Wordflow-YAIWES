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
Cada lote requiere `manifest + count + hash + destino + estado`.

## 6. Verificación cruzada — 4 pasadas
**A — estructura:** árbol, rutas, cantidad.

**B — contenido:** SHA-256 de críticos o todos los blobs cuando sea viable.

**C — upstream:** comparación contra repositorio oficial y commit canónico.

**D — post-publicación:** read-back desde `main`, clasificar `MISSING / EXTRA / MODIFIED`, y comparar snapshot pre/post.

## 7. Protección de una raíz de agente
```text
ROOTS/<agente>
 -> CODEOWNERS
 -> branch protection / PR requerido
 -> CI guard que rechaza deletes/modificaciones no autorizadas
 -> manifest + SHA
 -> snapshot de commit conocido
 -> auditoría pre/post
```

## 8. OpenClaw
Canonical: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`.
Destino exclusivo: `ROOTS/openclaw/`.
Lockfile canónico registrado: `cefd1fdf77f5c170ffacfad4b75e03c4c33345cf`.

## 9. Laboratorio CPU reutilizable
`.github/workflows/cpu-benchmark.yml` es independiente de las raíces. Solo `run/job/artifact` real permite PASS.

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

---

# 12. INVESTIGACIÓN HUGGING FACE — REGISTRO MAESTRO

**Estado:** PLANIFICADA / EN INVESTIGACIÓN. Esta sección registra el alcance aprobado y evita repetir investigaciones ya cerradas.

## 12.1 Objetivo
Investigar componentes reutilizables para una capa externa que mejore al agente en exactamente seis áreas:
1. Agente de trabajo
2. CODE
3. Razonamiento
4. Lógica avanzada
5. Frontend
6. Memoria

Debe aportar conocimiento/componentes y **CODE ejecutable** para una capa externa de control/workflow. No se busca construir todo desde cero.

## 12.2 Lista AI aprobada — estado actual

### CODE
- Qwen3.5-9B Q5
- KAT-Coder Q5

### Liquid AI / compactos
- LFM2.5-8B-A1B
- LFM2-2.6B

### Reasoning
- ERNIE-4.5-21B-A3B-Thinking Q6_K_L — 18.15 GB de pesos
- Yuan3.0-Flash-4bit — RAM total de ejecución pendiente de medición/verificación; no inventar cifra
- Jamba-1B-Reasoning
- HRM-Text-1B
- HRM-checkpoint-ARC-2
- HRM-checkpoint-sudoku-extreme
- HRM-checkpoint-maze-30x30-hard

### General / multimodal
- Gemma 4 E2B
- Gemma 4 E4B
- Hunyuan-1.8B-FP8

### NVIDIA
- Nemotron 3.5 Lightning 30B-A3B Q5
- Nemotron 3.5 — velocidad
- Cosmos3-Nano
- Nemotron 3.5 ASR 0.6B

### Meta
- Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf — archivo ~16.8 GB; objetivo 24 GB según la distribución investigada

### Eliminado
- Trinity-Large-Thinking — FUERA

## 12.3 Regla de memoria/caché
- Modelo >16 GB: caché máxima 1 GB; uso prioritario CODE/reasoning; reiniciar caché al cambiar/terminar el modelo.
- Modelo <=16 GB: caché máxima 3 GB.
- RAM de pesos no equivale a RAM total de inferencia. Si falta medición de runtime, registrar PENDIENTE y no inventar.

## 12.4 Formato obligatorio de cada modelo
Nombre; marca/laboratorio; mes/año; parámetros; RAM necesaria; funcionalidad/especialidad detallada; cuantizaciones; capa externa adicional; función de esa capa; candidato prioritario SI/NO.

## 12.5 Modelos adicionales obligatorios
### Meta 2026
- Nuevos modelos de Meta de 2026.
- Candidatos que quepan en 26 GB.
- Muse / Muse Glimmer y variantes cuantizadas.

### NVIDIA 2026
Buscar nuevos modelos disponibles en 2026 y modelos de otros laboratorios disponibles por NVIDIA, <=32 GB, en voz, audio, imagen, video, razonamiento y CODE.

### IBM / Microsoft / Liquid AI
Buscar modelos relevantes con fecha, especialidad, parámetros, cuantización y RAM <=32 GB.

### TOP 5 adicional
Buscar 5 nuevos modelos mejor valorados/disponibles en Hugging Face para CODE + reasoning, <=32 GB, de laboratorio original y no destilados.

## 12.6 Datasets
20 por cada área: agente de trabajo, CODE, razonamiento, lógica avanzada, frontend y memoria.
**Total: 120 datasets.**

## 12.7 Adaptadores
20 por cada una de las seis áreas.
**Total: 120 adaptadores.**

## 12.8 Skills
20 por cada una de las seis áreas.
**Total: 120 Skills.**

## 12.9 Capa externa / prompt-code ejecutable
20 componentes por cada una de las seis áreas que aporten CODE ejecutable, control, workflow o mecanismo reutilizable.
**Total: 120 componentes.**

No aceptar texto libre como sustituto de CODE ejecutable.

## 12.10 Router inteligente universal
Investigar los 3 mejores routers open source instalables que permitan reutilización/fusión/cableado sin construir un router desde cero.

## 12.11 Memoria
- 3 sistemas de memoria completos instalables sin programación, conectables/cableables con SQLite, caché y almacenamiento.
- 3 componentes adicionales para conectar memoria + SQLite + caché.
**Total: 6 candidatos.**

## 12.12 Ventana/inbox documental
Investigar sistemas open source instalables similares a ventana documental tipo Claude/Anthropic y tipo iOS.

## 12.13 Aceleradores AI — auditoría anti-duplicación
Primero auditar PIPELINE, bitácoras, archivos y repositorio para evitar repetir aceleradores.

**Auditoría actual del repositorio:** `PIPELINE-ACR-CONSOLIDATED.md` no contiene una lista registrada de aceleradores LLaMA/llama.cpp, vLLM u otros. Las búsquedas directas del repositorio para `llama`, `vLLM` y `quant` no devolvieron coincidencias. Por ello, ningún acelerador se marca como ya investigado en el PIPELINE solo por memoria conversacional.

La investigación de aceleradores debe registrar: nombre, función, modelos compatibles, cuantización/inferencia, requisito de hardware y ubicación arquitectónica.

## 12.14 Revisión final HF
```text
AI APROBADAS
 + MODELOS NUEVOS 2026
 + META
 + NVIDIA
 + IBM
 + MICROSOFT
 + LIQUID AI
 + TOP 5 CODE/REASONING
 + DATASETS
 + ADAPTADORES
 + SKILLS
 + CAPAS EXTERNAS
 + ROUTERS
 + MEMORIA
 + DOCUMENT UI
 + ACELERADORES
 -> LISTA FINAL HF
```

## 12.15 LOOP de investigación
```text
INTAKE
 -> INVENTARIO DE FUENTES
 -> AUDITORÍA DEL PIPELINE
 -> AUDITORÍA DEL CHAT
 -> DEDUPLICACIÓN
 -> INVESTIGACIÓN HF / WEB
 -> VERIFICACIÓN DE CADA CANDIDATO
 -> PRIORITARIO / NO PRIORITARIO / PENDIENTE
 -> REGISTRO EN PIPELINE
 -> SEGUNDA PASADA
 -> CROSSCHECK
 -> XRAY FINAL
 -> CIERRE
```

Un GAP/error no detiene el LOOP: diagnosticar → resolver → verificar → continuar. No marcar PASS sin evidencia.

## 12.16 Salidas
10 salidas. Cada salida: 100 búsquedas/investigaciones y confirmación del candidato prioritario. Fuente primaria: documento suministrado por el usuario con más de 100 ítems. Añadir 10 búsquedas adicionales por salida sobre las seis áreas, priorizando los mejor valorados en 2026 hasta la fecha.

## 12.17 Exclusiones
No mezclar con la tarea 11 que realiza otro GPT. Las tareas 8 y 9 del lote anterior también quedaron fuera por instrucción del usuario.
